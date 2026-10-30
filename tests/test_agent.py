from kh_graphrag.agent import NOT_FOUND, answer_question, parse_citations
from kh_graphrag.config import Settings
from kh_graphrag.graph.store import match_repos, match_tags
from kh_graphrag.models import ContextItem


class FakeStore:
    def __init__(self, hits=True):
        self.hits = hits
        self.expanded = False

    def vector_search(self, embedding, k):
        if not self.hits:
            return []
        return [ContextItem(source="how_to_containers/docs/pt/Journey_to_Ollama_Docker.md",
                            text="O Ollama escuta na porta 11434.", chunk_id="c1", score=0.9)]

    def expand(self, seed_ids, embedding, k):
        self.expanded = True
        assert seed_ids == ["c1"]
        return [ContextItem(source="how_to_containers/docs/pt/Install_Docker.md",
                            text="docker compose version", origin="graph-neighbor",
                            chunk_id="c2", via=["link:x"])]

    def graph_facts(self, question, seed_sources, limit):
        return [ContextItem(source="knowledge-hub/SEARCH_CONTENT.md",
                            text="Repositories tagged 4.4 selenium (LibraryTags): MODULES",
                            origin="graph-fact")]


class FakeLLM:
    def __init__(self, reply):
        self.reply = reply
        self.calls = 0
        self.last_prompt = ""

    def embed_query(self, text):
        return [0.0, 1.0]

    def chat(self, messages, temperature=0.0):
        self.calls += 1
        self.last_prompt = messages[-1]["content"]
        return self.reply


S = Settings(_env_file=None)


def test_vector_mode_skips_expansion():
    store, llm = FakeStore(), FakeLLM("A porta é 11434 [1].")
    result, _ = answer_question("Qual a porta?", "vector", store, llm, S)
    assert not store.expanded
    assert result.grounded and result.citations[0].source.endswith("Journey_to_Ollama_Docker.md")


def test_graph_mode_adds_facts_first_then_neighbours():
    store, llm = FakeStore(), FakeLLM("MODULES usa selenium [1]; porta 11434 [2].")
    result, _ = answer_question("Quem usa selenium?", "graph", store, llm, S)
    assert store.expanded
    assert [c.origin for c in result.context] == ["graph-fact", "vector", "graph-neighbor"]
    assert [c.origin for c in result.citations] == ["graph-fact", "vector"]
    assert "[3] (how_to_containers/docs/pt/Install_Docker.md)" in llm.last_prompt


def test_answer_without_citation_becomes_not_found():
    result, _ = answer_question("Qual a porta?", "vector", FakeStore(), FakeLLM("11434"), S)
    assert result.not_found and result.answer == NOT_FOUND


def test_model_refusal_and_empty_context():
    result, _ = answer_question("?", "vector", FakeStore(), FakeLLM("NOT_FOUND"), S)
    assert result.not_found
    llm = FakeLLM("should not be called")
    result, _ = answer_question("?", "vector", FakeStore(hits=False), llm, S)
    assert result.not_found and llm.calls == 0


def test_parse_citations_ignores_out_of_range_and_duplicates():
    items = [ContextItem(source="a", text="x"), ContextItem(source="b", text="y")]
    cites = parse_citations("one [2] two [2] three [7] four [1]", items)
    assert [c.n for c in cites] == [2, 1]


def test_match_tags_by_name_and_code():
    tags = [{"code": "4.4", "name": "selenium"}, {"code": "3.20", "name": "Deployment"},
            {"code": "3.2", "name": "Automation"}, {"code": "3.10", "name": "API"}]
    assert match_tags("Quais repositórios usam Selenium?", tags) == ["4.4"]
    assert match_tags("tagged with 3.20?", tags) == ["3.20"]  # not 3.2
    assert match_tags("porta 11434", tags) == []


def test_match_repos_exact_names():
    names = ["DOCS", "my_markdown_tool", "how_to_containers"]
    assert match_repos("is my_markdown_tool private?", names) == ["my_markdown_tool"]
    assert match_repos("read the docs/pt folder", names) == []
    assert match_repos("what is in DOCS?", names) == ["DOCS"]
