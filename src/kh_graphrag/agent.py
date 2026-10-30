"""orchestrate_pipeline (5.10) and route_request (5.9): the LangGraph answer flow.

    START -> retrieve -> route_request --vector--> generate -> verify -> END
                                      \\--graph---> expand ---/

- retrieve: top-k chunks from the Neo4j vector index.
- expand (graph mode only): neighbour chunks via LINKS_TO / shared tags, plus
  graph facts (catalog metadata, tag lookups) that have no text chunk at all.
- generate: a local model answers only from the numbered context, citing [n].
- verify: keeps only valid citations; without one, answers "not found".
"""

from __future__ import annotations

import re
import time
from typing import Any, Literal, Protocol, TypedDict

from langgraph.graph import END, START, StateGraph

from kh_graphrag.config import Settings
from kh_graphrag.models import Answer, Citation, ContextItem
from kh_graphrag.observability import Trace, Tracer

NOT_FOUND = (
    "Não encontrei isso nas notas. · Not found in the notes. · Nicht in den Notizen gefunden."
)

SYSTEM_PROMPT = """You answer questions about a technical knowledge base.
Rules:
- Use ONLY the numbered context below. Do not use outside knowledge.
- After each sentence, cite the context it came from as [n], e.g. [2] or [1][3].
- If the context does not contain the answer, reply exactly: NOT_FOUND
- Answer in the same language as the question. Be concise: at most 5 sentences or a short list.
- Keep commands, ports, file names and repository names exactly as written in the context."""

CITATION = re.compile(r"\[(\d{1,2})\]")


class Store(Protocol):
    def vector_search(self, embedding: list[float], k: int) -> list[ContextItem]: ...
    def expand(self, seed_ids: list[str], embedding: list[float], k: int) -> list[ContextItem]: ...
    def graph_facts(self, question: str, seed_sources: list[str], limit: int) -> list[ContextItem]: ...


class LLM(Protocol):
    def embed_query(self, text: str) -> list[float]: ...
    def chat(self, messages: list[dict], *, temperature: float = 0.0) -> str: ...


class State(TypedDict, total=False):
    question: str
    mode: Literal["vector", "graph"]
    embedding: list[float]
    context: list[ContextItem]
    raw_answer: str
    answer: str
    citations: list[Citation]
    grounded: bool
    not_found: bool


def format_context(items: list[ContextItem]) -> str:
    blocks = []
    for i, item in enumerate(items, start=1):
        where = f"{item.source}" + (f" — {item.heading}" if item.heading else "")
        blocks.append(f"[{i}] ({where})\n{item.text.strip()}")
    return "\n\n".join(blocks)


def parse_citations(text: str, items: list[ContextItem]) -> list[Citation]:
    seen: list[int] = []
    for raw in CITATION.findall(text):
        n = int(raw)
        if 1 <= n <= len(items) and n not in seen:
            seen.append(n)
    return [
        Citation(n=n, source=items[n - 1].source, heading=items[n - 1].heading,
                 origin=items[n - 1].origin)
        for n in seen
    ]


def build_graph(store: Store, llm: LLM, settings: Settings, trace: Trace | None = None):
    trace = trace or Trace()

    def retrieve(state: State) -> State:
        with trace.span("retrieve", {"question": state["question"]}) as out:
            embedding = llm.embed_query(state["question"])
            items = store.vector_search(embedding, settings.top_k)
            out["sources"] = [i.source for i in items]
        return {"embedding": embedding, "context": items}

    def route_request(state: State) -> str:
        return "expand" if state.get("mode") == "graph" else "generate"

    def expand(state: State) -> State:
        with trace.span("expand") as out:
            seeds = state["context"]
            seed_ids = [i.chunk_id for i in seeds if i.chunk_id]
            neighbours = store.expand(seed_ids, state["embedding"], settings.expand_k)
            facts = store.graph_facts(
                state["question"], list(dict.fromkeys(i.source for i in seeds)), settings.max_facts
            )
            out["neighbours"] = [f"{n.source} via {n.via}" for n in neighbours]
            out["facts"] = [f.text for f in facts]
        # Facts first: they are short and often answer catalog questions directly.
        return {"context": facts + seeds + neighbours}

    def generate(state: State) -> State:
        items = state.get("context") or []
        if not items:
            return {"raw_answer": "NOT_FOUND"}
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n\n{format_context(items)}\n\nQuestion: {state['question']}",
            },
        ]
        raw = llm.chat(messages)
        trace.generation("generate", getattr(settings, "llm_model", "llm"), messages, raw)
        return {"raw_answer": raw}

    def verify(state: State) -> State:
        raw = (state.get("raw_answer") or "").strip()
        items = state.get("context") or []
        citations = parse_citations(raw, items)
        refused = not raw or raw.upper().startswith("NOT_FOUND")
        if refused or (settings.require_citation and not citations):
            return {"answer": NOT_FOUND, "citations": [], "grounded": False, "not_found": True}
        return {"answer": raw, "citations": citations, "grounded": True, "not_found": False}

    graph = StateGraph(State)
    graph.add_node("retrieve", retrieve)
    graph.add_node("expand", expand)
    graph.add_node("generate", generate)
    graph.add_node("verify", verify)
    graph.add_edge(START, "retrieve")
    graph.add_conditional_edges("retrieve", route_request, {"expand": "expand", "generate": "generate"})
    graph.add_edge("expand", "generate")
    graph.add_edge("generate", "verify")
    graph.add_edge("verify", END)
    return graph.compile()


def answer_question(
    question: str,
    mode: Literal["vector", "graph"],
    store: Store,
    llm: LLM,
    settings: Settings,
    tracer: Tracer | None = None,
) -> tuple[Answer, Trace]:
    tracer = tracer or Tracer()
    trace = tracer.trace("ask", input={"question": question}, metadata={"mode": mode})
    started = time.perf_counter()
    final: dict[str, Any] = build_graph(store, llm, settings, trace).invoke(
        {"question": question, "mode": mode}
    )
    result = Answer(
        question=question,
        mode=mode,
        answer=final["answer"],
        citations=final.get("citations", []),
        context=final.get("context", []),
        grounded=final.get("grounded", False),
        not_found=final.get("not_found", True),
        latency_s=round(time.perf_counter() - started, 3),
    )
    trace.end({"answer": result.answer, "citations": [c.source for c in result.citations]})
    return result, trace
