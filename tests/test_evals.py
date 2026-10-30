from pathlib import Path

from kh_graphrag.evals import (EvalCase, evaluate_model, generate_report, load_cases,
                               score_answer, summarize)
from kh_graphrag.models import Answer, Citation

CASES = Path(__file__).resolve().parents[1] / "evals" / "questions.yaml"


def make_answer(text, sources, not_found=False, mode="graph"):
    return Answer(question="q", mode=mode, answer=text, not_found=not_found,
                  citations=[Citation(n=i + 1, source=s) for i, s in enumerate(sources)])


def test_eval_set_is_valid():
    cases = load_cases(CASES)
    assert len(cases) >= 15
    assert len({c.id for c in cases}) == len(cases)
    assert {"content", "catalog", "multi-hop", "negative"} <= {c.kind for c in cases}


def test_source_hit_matches_fragments_and_keywords():
    case = EvalCase(id="x", question="q", expected_sources=["Journey_to_Ollama_Docker.md"],
                    expected_keywords=["11434", "/api/tags"])
    hit, recall = score_answer(case, make_answer(
        "Port 11434 [1]", ["how_to_containers/docs/en/Journey_to_Ollama_Docker.md"]))
    assert hit == 1.0 and recall == 0.5


def test_negative_case_rewards_not_found():
    case = EvalCase(id="n", question="q", expect_not_found=True)
    assert score_answer(case, make_answer("x", [], not_found=True))[0] == 1.0
    assert score_answer(case, make_answer("Canberra [1]", ["a"]))[0] == 0.0


def test_evaluate_and_report_compare_modes():
    cases = [EvalCase(id="k", question="q", kind="catalog",
                      expected_sources=["SEARCH_CONTENT.md"], expected_keywords=["modules"])]

    def ask(question, mode):
        if mode == "graph":
            return make_answer("MODULES [1]", ["knowledge-hub/SEARCH_CONTENT.md"]), None
        return make_answer("not sure [1]", ["how_to_containers/README.md"], mode=mode), None

    logged = []
    rows = evaluate_model(cases, ["vector", "graph"], ask, on_scores=lambda t, s: logged.append(s))
    summary = summarize(rows)
    assert summary["graph"]["source_hit"] == 1.0 and summary["vector"]["source_hit"] == 0.0
    assert len(logged) == 2
    report = generate_report(rows, {"llm_model": "m", "embed_model": "e"})
    assert "| graph |" in report and "| catalog |" in report
