"""Runtime settings, read from environment variables (prefix KHG_) or a .env file."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KHG_", env_file=".env", extra="ignore")

    # Neo4j (graph + vector index)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "graphrag-demo"

    # Ollama (local models)
    ollama_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:3b"
    embed_model: str = "nomic-embed-text"
    embed_dim: int = 768
    # nomic-embed-text expects task prefixes; leave empty for models that do not.
    embed_doc_prefix: str = "search_document: "
    embed_query_prefix: str = "search_query: "
    request_timeout_s: int = 300

    # Retrieval
    top_k: int = 5
    expand_k: int = 5
    max_facts: int = 8
    chunk_size: int = 1200
    chunk_overlap: int = 150
    require_citation: bool = True

    # Corpus
    corpus_dir: str = "data/corpus"

    # Langfuse (optional; tracing is disabled when keys are empty)
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "http://localhost:3000"

    # TruLens judge (optional; defaults to the same local model)
    judge_model: str = ""

    @property
    def tracing_enabled(self) -> bool:
        return bool(self.langfuse_public_key and self.langfuse_secret_key)

    @property
    def judge_engine(self) -> str:
        return f"ollama/{self.judge_model or self.llm_model}"
