from pathlib import Path

import pytest

from kh_graphrag.ingest import chunk_note, chunk_notes, load_data, validate_schema
from kh_graphrag.ingest.loader import extract_links, parse_frontmatter
from kh_graphrag.models import Note

CORPUS = Path(__file__).resolve().parents[1] / "data" / "corpus"


@pytest.fixture(scope="module")
def corpus():
    return load_data(CORPUS)


def test_frontmatter_keeps_tag_codes_as_strings():
    meta, body = parse_frontmatter("---\nRepo: x\nTopicTags:\n  - 3.10\n  - 3.20\n---\n# X\n")
    assert meta["TopicTags"] == ["3.10", "3.20"]  # not 3.1 / 3.2
    assert body.startswith("# X")


def test_validate_schema_rejects_bad_codes():
    with pytest.raises(ValueError):
        validate_schema({"Repo": "x", "TopicTags": ["three"]})
    with pytest.raises(ValueError):
        validate_schema({"Repo": "x", "CreatedAt": "2026"})
    assert validate_schema({"Repo": "x", "CreatedAt": "2026-11"}).created_at == "2026-11"


def test_catalog_and_tag_tree(corpus):
    repos = corpus.repositories
    assert repos["selenium_and_postgre_containers"].visibility == "private"
    assert repos["DOCS"].visibility == "public-read"
    assert repos["how_to_containers"].visibility == "public-contrib"
    assert "4.4" in repos["selenium_and_postgre_containers"].tags
    assert corpus.tag_names["4.4"] == "selenium"
    assert corpus.tag_names["3.20"] == "Deployment"
    assert not repos["my_markdown_tool"].has_content


def test_readme_frontmatter_wins_and_is_marked_with_content(corpus):
    repo = corpus.repositories["how_to_containers"]
    assert repo.has_content and repo.source == "how_to_containers/README.md"
    assert "3.20" in repo.tags and "3.10" in repo.tags
    assert corpus.warnings == []


def test_notes_language_title_and_links(corpus):
    notes = {n.path: n for n in corpus.notes}
    journey = notes["how_to_containers/docs/pt/Journey_to_Ollama_Docker.md"]
    assert journey.lang == "pt"
    assert journey.title.startswith("Journey to Ollama Docker")
    assert "how_to_containers/docs/pt/Install_Docker.md" in journey.links
    # GitHub URL of the same organization resolves to the corpus path
    assert "knowledge-hub/SEARCH_CONTENT.md" in notes["knowledge-hub/README.md"].links
    assert notes["knowledge-hub/SEARCH_CONTENT.md"].title != "MENU"


def test_wikilinks_and_relative_links():
    known = {"a/x.md", "a/sub/y.md", "b/z.md"}
    by_stem = {"x": "a/x.md", "y": "a/sub/y.md", "z": "b/z.md"}
    body = "see [y](sub/y.md#part), [[z|alias]], [web](https://example.com/a.md) and [[missing]]"
    assert extract_links(body, "a/x.md", known, by_stem) == ["a/sub/y.md", "b/z.md"]


def test_chunker_respects_size_and_code_fences():
    body = "# Title\n\nintro text long enough to keep\n\n```bash\n# not a heading\necho hi\n```\n\n" \
           "## Part\n\n" + ("word " * 400)
    note = Note(path="r/n.md", repo="r", title="Title", body=body)
    chunks = chunk_note(note, size=500, overlap=50)
    assert all(len(c.text) <= 500 for c in chunks)
    assert any("# not a heading" in c.text for c in chunks)
    assert chunks[-1].heading == "Title > Part"
    assert len({c.id for c in chunks}) == len(chunks)


def test_corpus_chunks_are_stable(corpus):
    first = [c.id for c in chunk_notes(corpus.notes)]
    second = [c.id for c in chunk_notes(corpus.notes)]
    assert first == second and len(first) > 50
