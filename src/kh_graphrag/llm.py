"""call_external_api (5.7): thin HTTP client for the local Ollama server."""

from __future__ import annotations

import requests

from kh_graphrag.config import Settings


def call_external_api(url: str, payload: dict, timeout: int = 300) -> dict:
    """POST JSON and return JSON, with a readable error when Ollama is not reachable."""
    try:
        response = requests.post(url, json=payload, timeout=timeout)
    except requests.ConnectionError as exc:
        raise RuntimeError(
            f"Could not reach {url}. Is Ollama running? (docker compose up -d ollama)"
        ) from exc
    if response.status_code == 404 and "model" in response.text:
        raise RuntimeError(
            f"{response.text.strip()} -> pull it first: ollama pull {payload.get('model')}"
        )
    response.raise_for_status()
    return response.json()


class OllamaClient:
    def __init__(self, settings: Settings):
        self.s = settings
        self.base = settings.ollama_url.rstrip("/")

    def embed(self, texts: list[str], *, query: bool = False, batch: int = 16) -> list[list[float]]:
        prefix = self.s.embed_query_prefix if query else self.s.embed_doc_prefix
        vectors: list[list[float]] = []
        for i in range(0, len(texts), batch):
            data = call_external_api(
                f"{self.base}/api/embed",
                {"model": self.s.embed_model, "input": [prefix + t for t in texts[i : i + batch]]},
                self.s.request_timeout_s,
            )
            vectors += data["embeddings"]
        if vectors and len(vectors[0]) != self.s.embed_dim:
            raise RuntimeError(
                f"{self.s.embed_model} returns {len(vectors[0])} dimensions but KHG_EMBED_DIM="
                f"{self.s.embed_dim}. Set KHG_EMBED_DIM and re-run ingest with --reset."
            )
        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self.embed([text], query=True)[0]

    def chat(self, messages: list[dict], *, temperature: float = 0.0) -> str:
        data = call_external_api(
            f"{self.base}/api/chat",
            {
                "model": self.s.llm_model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature},
            },
            self.s.request_timeout_s,
        )
        return data["message"]["content"].strip()
