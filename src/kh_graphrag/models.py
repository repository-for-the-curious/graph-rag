"""Typed data contracts shared by ingestion, retrieval, the agent and the evals."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

TAG_CODE = re.compile(r"^[1-9]\d*\.\d+$")

TAG_FAMILIES = {
    "1": "StageTags",
    "2": "DomainTags",
    "3": "TopicTags",
    "4": "LibraryTags",
    "5": "ModuleTags",
}

VISIBILITY = {
    "🔒": "private",
    "👁️": "public-read",
    "👁": "public-read",
    "🔓": "public-contrib",
}


def tag_family(code: str) -> str:
    return TAG_FAMILIES.get(code.split(".", 1)[0], "OtherTags")


class RepoMeta(BaseModel):
    """Frontmatter contract of every README in the organization (see empty_repo)."""

    repo: str = Field(alias="Repo")
    created_at: str | None = Field(default=None, alias="CreatedAt")
    stage_tags: list[str] = Field(default_factory=list, alias="StageTags")
    domain_tags: list[str] = Field(default_factory=list, alias="DomainTags")
    topic_tags: list[str] = Field(default_factory=list, alias="TopicTags")
    library_tags: list[str] = Field(default_factory=list, alias="LibraryTags")
    module_tags: list[str] = Field(default_factory=list, alias="ModuleTags")

    model_config = {"populate_by_name": True}

    @field_validator("created_at", mode="before")
    @classmethod
    def _created_at(cls, value):
        if value is None:
            return None
        value = str(value).strip()
        if not re.fullmatch(r"\d{4}-\d{2}", value):
            raise ValueError(f"CreatedAt must be YYYY-MM, got {value!r}")
        return value

    @field_validator(
        "stage_tags", "domain_tags", "topic_tags", "library_tags", "module_tags", mode="before"
    )
    @classmethod
    def _codes(cls, value):
        if value is None:
            return []
        if isinstance(value, (str, int, float)):
            value = [value]
        codes = [str(v).strip() for v in value]
        bad = [c for c in codes if not TAG_CODE.match(c)]
        if bad:
            raise ValueError(f"invalid tag codes: {bad}")
        return codes

    @property
    def all_tags(self) -> list[str]:
        return [
            *self.stage_tags,
            *self.domain_tags,
            *self.topic_tags,
            *self.library_tags,
            *self.module_tags,
        ]


class Repository(BaseModel):
    name: str
    created_at: str | None = None
    visibility: str | None = None  # private | public-read | public-contrib
    tags: list[str] = Field(default_factory=list)
    has_content: bool = False  # True when its Markdown files are in the corpus
    source: str  # file the metadata came from (README.md or SEARCH_CONTENT.md)


class Note(BaseModel):
    path: str  # relative to the corpus root, e.g. how_to_containers/docs/pt/Install_Docker.md
    repo: str
    title: str
    lang: str | None = None
    tags: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)  # resolved note paths
    body: str


class Chunk(BaseModel):
    id: str
    note_path: str
    ord: int
    heading: str
    text: str


class ContextItem(BaseModel):
    """One numbered piece of context handed to the model."""

    source: str  # note path (or metadata file for graph facts)
    text: str
    heading: str = ""
    origin: Literal["vector", "graph-neighbor", "graph-fact"] = "vector"
    score: float | None = None
    chunk_id: str | None = None
    via: list[str] = Field(default_factory=list)


class Citation(BaseModel):
    n: int
    source: str
    heading: str = ""
    origin: str = "vector"


class Answer(BaseModel):
    question: str
    mode: Literal["vector", "graph"]
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    context: list[ContextItem] = Field(default_factory=list)
    grounded: bool = False
    not_found: bool = False
    latency_s: float = 0.0
