"""Command line: ingest, ask, eval.

    python -m kh_graphrag ingest [--corpus data/corpus] [--reset]
    python -m kh_graphrag ask "Which repositories use selenium?" [--mode graph|vector]
    python -m kh_graphrag eval [--modes vector graph] [--judge] [--min-source-hit 0.6]
"""

from __future__ import annotations

import argparse
import logging
import sys

from kh_graphrag.config import Settings


def _store(s: Settings):
    from kh_graphrag.graph import Neo4jStore

    return Neo4jStore(s.neo4j_uri, s.neo4j_user, s.neo4j_password)


def cmd_ingest(args, s: Settings) -> int:
    from kh_graphrag.ingest import chunk_notes, load_data
    from kh_graphrag.llm import OllamaClient

    corpus = load_data(args.corpus or s.corpus_dir)
    chunks = chunk_notes(corpus.notes, s.chunk_size, s.chunk_overlap)
    print(f"Loaded {len(corpus.notes)} notes, {len(corpus.repositories)} repositories, "
          f"{len(chunks)} chunks. Embedding with {s.embed_model}...")
    embeddings = OllamaClient(s).embed([f"{c.heading}\n{c.text}" for c in chunks])
    store = _store(s)
    try:
        if args.reset:
            store.reset()
        store.ensure_schema(s.embed_dim)
        counts = store.write_corpus(corpus, chunks, embeddings)
    finally:
        store.close()
    print("Graph written: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    for w in corpus.warnings:
        print(f"warning: {w}")
    return 0


def cmd_ask(args, s: Settings) -> int:
    from kh_graphrag.agent import answer_question
    from kh_graphrag.llm import OllamaClient
    from kh_graphrag.observability import make_tracer

    store, tracer = _store(s), make_tracer(s)
    try:
        result, _ = answer_question(args.question, args.mode, store, OllamaClient(s), s, tracer)
    finally:
        store.close()
        tracer.flush()
    print(result.answer)
    if result.citations:
        print("\nSources:")
        for c in result.citations:
            where = c.source + (f" — {c.heading}" if c.heading else "")
            print(f"  [{c.n}] {where} ({c.origin})")
    if args.show_context:
        print("\nContext:")
        for i, item in enumerate(result.context, start=1):
            print(f"  [{i}] {item.origin} {item.source} {item.via or ''}")
    print(f"\n({result.mode} mode, {result.latency_s:.1f}s)")
    return 0


def cmd_eval(args, s: Settings) -> int:
    from kh_graphrag.agent import answer_question
    from kh_graphrag.evals import TruLensJudge, evaluate_model, load_cases, summarize, write_results
    from kh_graphrag.llm import OllamaClient
    from kh_graphrag.observability import log_metrics, make_tracer

    cases = load_cases(args.cases)
    store, llm, tracer = _store(s), OllamaClient(s), make_tracer(s)
    judge = TruLensJudge(s.judge_engine, s.ollama_url) if args.judge else None
    try:
        rows = evaluate_model(
            cases,
            args.modes,
            lambda q, m: answer_question(q, m, store, llm, s, tracer),
            judge=judge,
            on_scores=log_metrics,
        )
    finally:
        store.close()
        tracer.flush()
    md, js = write_results(
        rows,
        {"llm_model": s.llm_model, "embed_model": s.embed_model,
         "judge": s.judge_engine if args.judge else None},
        args.out,
    )
    summary = summarize(rows)
    for mode, values in summary.items():
        print(f"{mode:>6}: " + "  ".join(f"{k}={v}" for k, v in values.items()))
    print(f"Report: {md}  Data: {js}")
    gate = summary.get("graph") or next(iter(summary.values()))
    if args.min_source_hit is not None and (gate["source_hit"] or 0) < args.min_source_hit:
        print(f"FAILED: source_hit {gate['source_hit']} < {args.min_source_hit}")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kh_graphrag", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ingest", help="load the Markdown corpus into Neo4j")
    p.add_argument("--corpus", help="folder with one sub-folder per repository")
    p.add_argument("--reset", action="store_true", help="delete the graph and index first")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("ask", help="ask one question")
    p.add_argument("question")
    p.add_argument("--mode", choices=["graph", "vector"], default="graph")
    p.add_argument("--show-context", action="store_true")
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("eval", help="run the eval set in vector and graph modes")
    p.add_argument("--cases", default="evals/questions.yaml")
    p.add_argument("--modes", nargs="+", choices=["vector", "graph"], default=["vector", "graph"])
    p.add_argument("--judge", action="store_true", help="add TruLens LLM-as-judge metrics")
    p.add_argument("--out", default="evals/results")
    p.add_argument("--min-source-hit", type=float, default=None,
                   help="exit 1 if graph-mode source_hit is below this value (CI gate)")
    p.set_defaults(func=cmd_eval)

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                        format="%(levelname)s %(name)s: %(message)s")
    from neo4j.exceptions import AuthError, ServiceUnavailable

    settings = Settings()
    try:
        return args.func(args, settings)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ServiceUnavailable:
        print(f"error: Neo4j is not reachable at {settings.neo4j_uri} "
              "(docker compose up -d neo4j)", file=sys.stderr)
        return 2
    except AuthError:
        print("error: Neo4j rejected the credentials (check KHG_NEO4J_PASSWORD)", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
