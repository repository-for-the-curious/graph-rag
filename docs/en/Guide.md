# Guide — knowledge_hub_graphrag

[⬅ README](../../README.md) · [Português](../pt/Guide.md) · [Deutsch](../de/Guide.md)

## 1. What the project demonstrates

That explicit relations between documents (links, tags, a catalog) answer questions vector search cannot reach, and that this difference can be **measured**. Everything runs locally: Neo4j, Ollama and Python, no API key.

## 2. Requirements

| Item | Minimum | Note |
| --- | --- | --- |
| Docker + Docker Compose v2.24+ | required | see [how_to_containers](https://github.com/repository-for-the-curious/how_to_containers) |
| Free RAM | 8 GB | Neo4j (1 GB heap) + `qwen2.5:3b` |
| Disk | 5 GB | images + models |
| GPU | optional | NVIDIA: uncomment the `deploy` block of the `ollama` service |

## 3. Step by step

```bash
cp .env.example .env
docker compose up -d                          # first run downloads qwen2.5:3b and nomic-embed-text
docker compose logs -f ollama-models          # follow the download; ends with "success"
docker compose run --rm app ingest --reset    # ~15 notes, a few hundred chunks
docker compose run --rm app ask "Which port does Ollama expose its API on?" --show-context
```

`--show-context` lists every context item with its origin: `vector` (vector search), `graph-neighbor` (neighbouring note through a link or tag) or `graph-fact` (catalog/tag fact). Neo4j Browser runs at http://localhost:7474 (user `neo4j`, password from `.env`). To look at the graph:

```cypher
MATCH (r:Repository)-[:TAGGED]->(t:Tag {family: 'LibraryTags'}) RETURN r, t
```

## 4. How a question is answered

1. **retrieve** — the question is embedded (`search_query:` + text) and the `chunk_embedding` index returns the 5 closest chunks.
2. **route_request** — `vector` mode goes straight to generation; `graph` mode goes through expansion.
3. **expand** — collects notes linked by `LINKS_TO` to the retrieved notes and notes of *other* repositories sharing TopicTags or LibraryTags, then re-ranks their chunks by similarity to the question. It also builds **graph facts**: repositories carrying the tags named in the question (by name, like `selenium`, or code, like `3.20`) and a card for each repository mentioned or retrieved (visibility, date, tags).
4. **generate** — the model gets the numbered context and is told to use only that, cite `[n]`, and reply `NOT_FOUND` when the answer is not there.
5. **verify** — keeps only citations that exist in the context; with no valid citation, the answer becomes "not found".

## 5. Evaluation

```bash
docker compose run --rm app eval                 # deterministic metrics, 2 answers per question
docker compose run --rm app eval --judge         # + TruLens (groundedness, relevance), much slower
docker compose run --rm app eval --min-source-hit 0.6   # exits 1 below the gate
```

`evals/results/latest.md` holds the summary per mode, `source_hit` per question kind and per-question details. Graph mode is expected to win clearly on **catalog** and **multi-hop** questions and tie on **content** ones. If graph mode loses on content, the extra context is getting in the way: lower `KHG_EXPAND_K` or `KHG_MAX_FACTS`.

To add a question, append an item to `evals/questions.yaml` with `expected_sources` (path or file-name fragment) and lower-case `expected_keywords`.

## 6. Observability (Langfuse)

```bash
docker compose --profile observability up -d     # http://localhost:3000
```

Create a user and a project, then copy its keys to `KHG_LANGFUSE_PUBLIC_KEY` and `KHG_LANGFUSE_SECRET_KEY` in `.env`. Each `ask` becomes a trace with `retrieve`, `expand` and generation spans; every `eval` question gets its scores (`source_hit`, `keyword_recall` and the TruLens ones) on its trace.

## 7. Using your own notes or an Obsidian vault

Put each repository or vault in its own sub-folder and run `ingest --corpus <folder> --reset`. It reads:

- YAML frontmatter of the README (the `empty_repo` contract) and of any note (keys ending in `Tags`, or `tags`);
- relative Markdown links, GitHub URLs of the organization and `[[wikilinks]]`;
- `SEARCH_CONTENT.md`, when present, for the tag tree and the catalog.

For another embedding model, set `KHG_EMBED_MODEL`, `KHG_EMBED_DIM` and the prefixes, then run `ingest --reset` (the vector index has a fixed dimension).

## 8. Troubleshooting

| Symptom | Likely cause | Action |
| --- | --- | --- |
| `Could not reach http://...:11434` | Ollama is not up | `docker compose ps`, `docker compose logs ollama` |
| `model ... not found` | download not finished | `docker compose logs ollama-models` |
| `returns N dimensions but KHG_EMBED_DIM=768` | embedding model changed | set `KHG_EMBED_DIM` and run `ingest --reset` |
| Many "not found" answers | small model dropping citations | `KHG_LLM_MODEL=qwen2.5:7b`, or `KHG_REQUIRE_CITATION=false` to debug |
| `There is no procedure ... vector` | old Neo4j | use the compose `neo4j:5.26` image |
