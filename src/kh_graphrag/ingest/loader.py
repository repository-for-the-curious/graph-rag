"""load_data (5.1) and validate_schema (5.3).

Reads a folder of repositories (one sub-folder per repository) containing Markdown
files, in the same shape as the repository-for-the-curious organization:

- each repository README.md carries YAML frontmatter with the five tag families;
- knowledge-hub/SEARCH_CONTENT.md holds the tag tree and the catalog of every
  repository, including private ones whose content is not in the corpus;
- notes link to each other with relative Markdown links, GitHub URLs of the same
  organization, or Obsidian [[wikilinks]].
"""

from __future__ import annotations

import logging
import posixpath
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

import yaml
from pydantic import ValidationError

from kh_graphrag.models import TAG_CODE, VISIBILITY, Note, RepoMeta, Repository

log = logging.getLogger(__name__)

ORG_URL = re.compile(
    r"https?://github\.com/repository-for-the-curious/([^/\s)]+)/(?:blob|tree)/[^/\s)]+/([^\s)#]+)"
)
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
TAG_TREE_ITEM = re.compile(r"^-\s+\*\*(\d+\.\d+)\*\*\s+(.+?)\s*$")
CATALOG_ROW = re.compile(r"^\|\s*(\S+)\s*\|\s*\[([^\]]+)\]\([^)]*\)\s*\|(.+)$")
LANG_DIRS = {"pt", "en", "de"}


@dataclass
class Corpus:
    root: Path
    repositories: dict[str, Repository] = field(default_factory=dict)
    notes: list[Note] = field(default_factory=list)
    tag_names: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split a leading YAML block (--- ... ---) from the Markdown body."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines(keepends=True)
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            raw = "".join(lines[1:i])
            body = "".join(lines[i + 1 :])
            try:
                # BaseLoader keeps every scalar as a string: tag "3.10" must not become 3.1.
                data = yaml.load(raw, Loader=yaml.BaseLoader) or {}
            except yaml.YAMLError:
                return {}, text
            return (data if isinstance(data, dict) else {}), body
    return {}, text


def validate_schema(meta: dict, *, source: str = "") -> RepoMeta:
    """Validate README frontmatter against the organization contract (raises ValueError)."""
    try:
        return RepoMeta.model_validate(meta)
    except ValidationError as exc:
        raise ValueError(f"{source}: invalid frontmatter: {exc.errors(include_url=False)}") from exc


def parse_tag_tree(search_content: str) -> dict[str, str]:
    """Read '- **4.4** selenium' lines into {'4.4': 'selenium'}."""
    names: dict[str, str] = {}
    for line in search_content.splitlines():
        m = TAG_TREE_ITEM.match(line.strip())
        if m:
            names[m.group(1)] = m.group(2)
    return names


def parse_catalog(search_content: str) -> list[tuple[str, RepoMeta]]:
    """Read the repository table of SEARCH_CONTENT.md -> [(visibility_icon, RepoMeta)]."""
    rows: list[tuple[str, RepoMeta]] = []
    for line in search_content.splitlines():
        m = CATALOG_ROW.match(line.strip())
        if not m:
            continue
        icon, name, rest = m.group(1), m.group(2), m.group(3)
        cells = [c.strip() for c in rest.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue

        def codes(cell: str) -> list[str]:
            return [c.strip() for c in cell.split(",") if TAG_CODE.match(c.strip())]

        meta = RepoMeta(
            Repo=name,
            CreatedAt=cells[0] or None,
            StageTags=codes(cells[1]),
            DomainTags=codes(cells[2]),
            TopicTags=codes(cells[3]),
            LibraryTags=codes(cells[4]),
            ModuleTags=codes(cells[5]),
        )
        rows.append((icon, meta))
    return rows


def detect_lang(rel_path: str) -> str | None:
    for part in rel_path.split("/")[:-1]:
        if part in LANG_DIRS:
            return part
    return None


def note_tags(frontmatter: dict) -> list[str]:
    """Tag codes declared in a note's own properties (any *Tags key, or `tags`)."""
    found: list[str] = []
    for key, value in frontmatter.items():
        if not (key.endswith("Tags") or key.lower() == "tags"):
            continue
        values = value if isinstance(value, list) else [value]
        found += [str(v).strip() for v in values if TAG_CODE.match(str(v).strip())]
    return sorted(set(found), key=found.index)


def title_of(body: str, fallback: str) -> str:
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("# ") and line[2:].strip().upper() != "MENU":
            return line[2:].strip()
    return fallback


def extract_links(body: str, note_path: str, known: set[str], by_stem: dict[str, str]) -> list[str]:
    """Resolve links in a note to other note paths that exist in the corpus."""
    out: list[str] = []
    base = posixpath.dirname(note_path)
    for target in MD_LINK.findall(body):
        target = unquote(target.split("#", 1)[0])
        if not target:
            continue
        org = ORG_URL.match(target)
        if org:
            candidate = posixpath.normpath(f"{org.group(1)}/{org.group(2)}")
        elif "://" in target or target.startswith("mailto:"):
            continue
        else:
            candidate = posixpath.normpath(posixpath.join(base, target))
        if candidate in known and candidate != note_path:
            out.append(candidate)
    for name in WIKI_LINK.findall(body):
        candidate = by_stem.get(name.strip().lower())
        if candidate and candidate != note_path:
            out.append(candidate)
    return sorted(set(out))


def load_data(corpus_dir: str | Path) -> Corpus:
    """Ingest every Markdown file under corpus_dir (one sub-folder per repository)."""
    root = Path(corpus_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"corpus folder not found: {root}")
    corpus = Corpus(root=root)

    files = sorted(p for p in root.rglob("*.md") if p.is_file() and not p.name.startswith("."))
    rel_paths = [p.relative_to(root).as_posix() for p in files]
    known = set(rel_paths)
    by_stem = {Path(r).stem.lower(): r for r in rel_paths}

    raw: dict[str, tuple[dict, str]] = {}
    for path, rel in zip(files, rel_paths):
        raw[rel] = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))

    # 1) Tag tree and catalog, when a SEARCH_CONTENT.md is present.
    catalog_source = next((r for r in rel_paths if r.endswith("SEARCH_CONTENT.md")), None)
    if catalog_source:
        text = raw[catalog_source][1]
        corpus.tag_names = parse_tag_tree(text)
        for icon, meta in parse_catalog(text):
            corpus.repositories[meta.repo] = Repository(
                name=meta.repo,
                created_at=meta.created_at,
                visibility=VISIBILITY.get(icon),
                tags=meta.all_tags,
                has_content=False,
                source=catalog_source,
            )

    # 2) Repositories present in the corpus; README frontmatter wins over the catalog.
    for top in sorted({r.split("/", 1)[0] for r in rel_paths if "/" in r}):
        readme = f"{top}/README.md"
        existing = corpus.repositories.get(top)
        repo = existing.model_copy() if existing else Repository(name=top, source=readme)
        repo.has_content = True
        if readme in raw and raw[readme][0]:
            try:
                meta = validate_schema(raw[readme][0], source=readme)
                repo.created_at = meta.created_at or repo.created_at
                repo.tags = meta.all_tags or repo.tags
                repo.source = readme
            except ValueError as exc:
                corpus.warnings.append(str(exc))
        corpus.repositories[top] = repo

    # 3) Notes.
    for rel in rel_paths:
        frontmatter, body = raw[rel]
        repo_name = rel.split("/", 1)[0] if "/" in rel else "_root"
        corpus.notes.append(
            Note(
                path=rel,
                repo=repo_name,
                title=title_of(body, Path(rel).stem),
                lang=detect_lang(rel),
                tags=note_tags(frontmatter),
                links=extract_links(body, rel, known, by_stem),
                body=body,
            )
        )

    unknown = {
        t for r in corpus.repositories.values() for t in r.tags if t not in corpus.tag_names
    }
    if corpus.tag_names and unknown:
        corpus.warnings.append(
            f"tag codes not in the SEARCH_CONTENT tag tree (propose them first): {sorted(unknown)}"
        )
    for w in corpus.warnings:
        log.warning(w)
    return corpus
