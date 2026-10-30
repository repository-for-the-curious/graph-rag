"""Neo4j access: write the corpus, vector search, graph expansion and graph facts."""

from __future__ import annotations

import re

from kh_graphrag.graph import schema as q
from kh_graphrag.ingest.loader import Corpus
from kh_graphrag.models import Chunk, ContextItem, tag_family

VISIBILITY_LABEL = {
    "private": "🔒 private",
    "public-read": "👁️ public (read and use)",
    "public-contrib": "🔓 public (contributions welcome)",
}


def match_tags(question: str, tags: list[dict]) -> list[str]:
    """Tag codes the question mentions, by code ('3.20') or by name ('selenium')."""
    text = question.lower()
    found: list[str] = []
    for tag in tags:
        code, name = tag["code"], (tag.get("name") or "")
        if re.search(rf"(?<![\d.]){re.escape(code)}(?![\d])", text):
            found.append(code)
            continue
        if len(name) >= 3 and re.search(rf"\b{re.escape(name.lower())}\b", text):
            found.append(code)
    return found


def match_repos(question: str, names: list[str]) -> list[str]:
    """Repository names written exactly as in the catalog (case-sensitive: 'DOCS', not 'docs')."""
    return [n for n in names if re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", question)]


def _card(row: dict) -> str:
    vis = VISIBILITY_LABEL.get(row.get("visibility") or "", "visibility not declared")
    content = "content indexed here" if row.get("has_content") else "catalog entry only"
    tags = "; ".join(t for t in row.get("tags") or [] if t) or "no tags"
    created = row.get("created_at") or "unknown"
    return (
        f"Repository {row['name']} | {vis} | CreatedAt {created} | {content} | tags: {tags}"
    )


class Neo4jStore:
    def __init__(self, uri: str, user: str, password: str):
        from neo4j import GraphDatabase  # imported lazily so tests run without a server

        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.driver.verify_connectivity()  # fail fast instead of retrying for ~30 s
        self._tags: list[dict] | None = None

    def close(self) -> None:
        self.driver.close()

    def run(self, cypher: str, **params) -> list[dict]:
        records, _, _ = self.driver.execute_query(cypher, parameters_=params)
        return [r.data() for r in records]

    # ---- write -------------------------------------------------------------------
    def reset(self) -> None:
        self.run("MATCH (n) DETACH DELETE n")
        self.run(f"DROP INDEX {q.VECTOR_INDEX} IF EXISTS")

    def ensure_schema(self, dim: int) -> None:
        for statement in q.schema_statements(dim):
            self.run(statement)

    def write_corpus(
        self, corpus: Corpus, chunks: list[Chunk], embeddings: list[list[float]], batch: int = 200
    ) -> dict[str, int]:
        tags = sorted(
            {*corpus.tag_names, *(t for r in corpus.repositories.values() for t in r.tags)}
        )
        self.run(
            q.UPSERT_TAGS,
            rows=[
                {"code": c, "name": corpus.tag_names.get(c), "family": tag_family(c)} for c in tags
            ],
        )
        self.run(q.UPSERT_REPOS, rows=[r.model_dump() for r in corpus.repositories.values()])
        notes = [n.model_dump(exclude={"body", "links"}) for n in corpus.notes]
        self.run(q.UPSERT_NOTES, rows=notes)
        links = [{"src": n.path, "dst": d} for n in corpus.notes for d in n.links]
        self.run(q.UPSERT_LINKS, rows=links)
        rows = [{**c.model_dump(), "embedding": e} for c, e in zip(chunks, embeddings)]
        for i in range(0, len(rows), batch):
            self.run(q.UPSERT_CHUNKS, rows=rows[i : i + batch])
        self.run("CALL db.awaitIndexes(300)")
        self._tags = None
        return {
            "repositories": len(corpus.repositories),
            "notes": len(notes),
            "links": len(links),
            "chunks": len(rows),
            "tags": len(tags),
        }

    # ---- read --------------------------------------------------------------------
    def vector_search(self, embedding: list[float], k: int) -> list[ContextItem]:
        return [
            ContextItem(
                source=r["source"],
                text=r["text"],
                heading=r["heading"] or "",
                origin="vector",
                score=r["score"],
                chunk_id=r["chunk_id"],
            )
            for r in self.run(q.VECTOR_SEARCH, k=k, embedding=embedding)
        ]

    def expand(self, seed_ids: list[str], embedding: list[float], k: int) -> list[ContextItem]:
        if not seed_ids or k <= 0:
            return []
        return [
            ContextItem(
                source=r["source"],
                text=r["text"],
                heading=r["heading"] or "",
                origin="graph-neighbor",
                score=r["score"],
                chunk_id=r["chunk_id"],
                via=r["vias"],
            )
            for r in self.run(q.EXPAND, ids=seed_ids, embedding=embedding, k=k)
        ]

    def tags(self) -> list[dict]:
        if self._tags is None:
            self._tags = self.run(q.ALL_TAGS)
        return self._tags

    def graph_facts(self, question: str, seed_sources: list[str], limit: int) -> list[ContextItem]:
        """Structured facts the vector index cannot see: catalog metadata and tag lookups."""
        facts: list[ContextItem] = []
        codes = match_tags(question, self.tags())
        for row in self.run(q.REPOS_WITH_TAGS, codes=codes) if codes else []:
            facts.append(
                ContextItem(
                    source="knowledge-hub/SEARCH_CONTENT.md",
                    heading=f"Tag {row['code']}",
                    text=(
                        f"Repositories tagged {row['code']} {row['name']} ({row['family']}): "
                        + ", ".join(sorted(row["repos"]))
                    ),
                    origin="graph-fact",
                    via=[f"tag:{row['code']}"],
                )
            )
        names = [r["name"] for r in self.run(q.ALL_REPO_NAMES)]
        wanted = match_repos(question, names)
        wanted += [r["name"] for r in self.run(q.REPOS_OF_NOTES, paths=seed_sources)]
        wanted = list(dict.fromkeys(wanted))
        cards = self.run(q.REPO_CARDS, names=wanted) if wanted else []
        for row in sorted(cards, key=lambda r: wanted.index(r["name"])):
            facts.append(
                ContextItem(
                    source=row["source"] or "knowledge-hub/SEARCH_CONTENT.md",
                    heading=f"Repository {row['name']}",
                    text=_card(row),
                    origin="graph-fact",
                    via=[f"repo:{row['name']}"],
                )
            )
        return facts[:limit]
