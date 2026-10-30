"""evaluate_model (5.5) and generate_report (5.6).

Two kinds of metrics per question and per mode (vector vs graph):

- deterministic, no model needed:
  source_hit      1 if a cited source matches an expected source (or a correct "not found")
  keyword_recall  share of expected keywords present in the answer (case-insensitive)
- LLM-as-judge with TruLens (optional, --judge), using a local Ollama model via LiteLLM:
  groundedness       is the answer supported by the retrieved context?
  answer_relevance   does the answer address the question?
  context_relevance  is the retrieved context relevant to the question?
"""

from __future__ import annotations

import json
import statistics
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import yaml
from pydantic import BaseModel, Field

from kh_graphrag.models import Answer


class EvalCase(BaseModel):
    id: str
    question: str
    kind: str = "content"  # content | catalog | multi-hop | negative
    expected_sources: list[str] = Field(default_factory=list)
    expected_keywords: list[str] = Field(default_factory=list)
    expect_not_found: bool = False


@dataclass
class EvalRow:
    case_id: str
    kind: str
    mode: str
    question: str
    answer: str
    cited: list[str]
    source_hit: float
    keyword_recall: float | None
    latency_s: float
    judge: dict[str, float | None] = field(default_factory=dict)


def load_cases(path: str | Path) -> list[EvalCase]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return [EvalCase.model_validate(item) for item in data["cases"]]


def _source_matches(cited: str, expected: str) -> bool:
    # an expected entry may be a full path or a fragment shared by all language versions
    return cited == expected or expected in cited


def score_answer(case: EvalCase, answer: Answer) -> tuple[float, float | None]:
    cited = [c.source for c in answer.citations]
    if case.expect_not_found:
        return (1.0 if answer.not_found else 0.0), None
    hit = any(_source_matches(c, e) for c in cited for e in case.expected_sources)
    if not case.expected_keywords:
        return float(hit), None
    text = answer.answer.lower()
    found = sum(1 for k in case.expected_keywords if k.lower() in text)
    return float(hit), round(found / len(case.expected_keywords), 3)


class TruLensJudge:
    """Feedback functions from TruLens, served by a local model through LiteLLM."""

    def __init__(self, model_engine: str, api_base: str):
        from trulens.providers.litellm import LiteLLM

        self.provider = LiteLLM(model_engine=model_engine, completion_kwargs={"api_base": api_base})

    def __call__(self, question: str, answer: Answer) -> dict[str, float | None]:
        if answer.not_found:
            return {"groundedness": None, "answer_relevance": None, "context_relevance": None}
        context = "\n\n".join(i.text for i in answer.context)

        def safe(fn):
            try:
                value = fn()
                return round(float(value[0] if isinstance(value, tuple) else value), 3)
            except Exception:  # a judge failure must not stop the whole run
                return None

        return {
            "groundedness": safe(
                lambda: self.provider.groundedness_measure_with_cot_reasons(context, answer.answer)
            ),
            "answer_relevance": safe(lambda: self.provider.relevance(question, answer.answer)),
            "context_relevance": safe(lambda: self.provider.context_relevance(question, context)),
        }


def evaluate_model(
    cases: list[EvalCase],
    modes: list[str],
    ask: Callable[[str, str], tuple[Answer, object]],
    judge: Callable[[str, Answer], dict[str, float | None]] | None = None,
    on_scores: Callable[[object, dict[str, float | None]], None] | None = None,
) -> list[EvalRow]:
    rows: list[EvalRow] = []
    for case in cases:
        for mode in modes:
            answer, trace = ask(case.question, mode)
            hit, recall = score_answer(case, answer)
            judged = judge(case.question, answer) if judge else {}
            if on_scores:
                on_scores(trace, {"source_hit": hit, "keyword_recall": recall, **judged})
            rows.append(
                EvalRow(
                    case_id=case.id,
                    kind=case.kind,
                    mode=mode,
                    question=case.question,
                    answer=answer.answer,
                    cited=[c.source for c in answer.citations],
                    source_hit=hit,
                    keyword_recall=recall,
                    latency_s=answer.latency_s,
                    judge=judged,
                )
            )
    return rows


def _mean(values: list[float | None]) -> float | None:
    clean = [v for v in values if v is not None]
    return round(statistics.mean(clean), 3) if clean else None


def summarize(rows: list[EvalRow]) -> dict[str, dict[str, float | None]]:
    summary: dict[str, dict[str, float | None]] = {}
    for mode in dict.fromkeys(r.mode for r in rows):
        mine = [r for r in rows if r.mode == mode]
        summary[mode] = {
            "source_hit": _mean([r.source_hit for r in mine]),
            "keyword_recall": _mean([r.keyword_recall for r in mine]),
            "groundedness": _mean([r.judge.get("groundedness") for r in mine]),
            "answer_relevance": _mean([r.judge.get("answer_relevance") for r in mine]),
            "context_relevance": _mean([r.judge.get("context_relevance") for r in mine]),
            "latency_s": _mean([r.latency_s for r in mine]),
        }
    return summary


def _fmt(value: float | None) -> str:
    return "–" if value is None else f"{value:.2f}"


def generate_report(rows: list[EvalRow], meta: dict) -> str:
    summary = summarize(rows)
    metrics = ["source_hit", "keyword_recall", "groundedness", "answer_relevance",
               "context_relevance", "latency_s"]
    lines = [
        "# Eval results",
        "",
        f"- Generated: {meta.get('generated_at')}",
        f"- LLM: `{meta.get('llm_model')}` · embeddings: `{meta.get('embed_model')}`"
        f" · judge: `{meta.get('judge') or 'off'}`",
        f"- Cases: {len({r.case_id for r in rows})}",
        "",
        "## Summary",
        "",
        "| Mode | " + " | ".join(metrics) + " |",
        "| --- | " + " | ".join("---:" for _ in metrics) + " |",
    ]
    for mode, values in summary.items():
        lines.append(f"| {mode} | " + " | ".join(_fmt(values[m]) for m in metrics) + " |")

    kinds = sorted({r.kind for r in rows})
    lines += ["", "## source_hit by question kind", "",
              "| Kind | " + " | ".join(summary) + " |",
              "| --- | " + " | ".join("---:" for _ in summary) + " |"]
    for kind in kinds:
        cells = [_fmt(_mean([r.source_hit for r in rows if r.kind == kind and r.mode == m]))
                 for m in summary]
        lines.append(f"| {kind} | " + " | ".join(cells) + " |")

    lines += ["", "## Per question", "", "| Case | Mode | source_hit | keyword_recall | Cited |",
              "| --- | --- | ---: | ---: | --- |"]
    for r in rows:
        cited = ", ".join(sorted(set(r.cited))) or "–"
        lines.append(f"| {r.case_id} | {r.mode} | {_fmt(r.source_hit)} | "
                     f"{_fmt(r.keyword_recall)} | {cited} |")
    return "\n".join(lines) + "\n"


def write_results(rows: list[EvalRow], meta: dict, out_dir: str | Path) -> tuple[Path, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), **meta}
    md = out / "latest.md"
    js = out / "latest.json"
    md.write_text(generate_report(rows, meta), encoding="utf-8")
    js.write_text(
        json.dumps({"meta": meta, "summary": summarize(rows), "rows": [asdict(r) for r in rows]},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return md, js
