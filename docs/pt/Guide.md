# Guia — knowledge_hub_graphrag

[⬅ README](../../README.md) · [English](../en/Guide.md) · [Deutsch](../de/Guide.md)

## 1. O que o projeto prova

Que relações explícitas entre documentos (links, tags, catálogo) respondem perguntas que a busca vetorial não alcança, e que dá para **medir** essa diferença. Tudo roda local: Neo4j, Ollama e Python, sem chave de API.

## 2. Pré-requisitos

| Item | Mínimo | Observação |
| --- | --- | --- |
| Docker + Docker Compose v2.24+ | obrigatório | ver [how_to_containers](https://github.com/repository-for-the-curious/how_to_containers) |
| RAM livre | 8 GB | Neo4j (1 GB de heap) + `qwen2.5:3b` |
| Disco | 5 GB | imagens + modelos |
| GPU | opcional | NVIDIA: descomente o bloco `deploy` do serviço `ollama` |

## 3. Passo a passo

```bash
cp .env.example .env
docker compose up -d                          # 1ª vez baixa qwen2.5:3b e nomic-embed-text
docker compose logs -f ollama-models          # acompanhe o download; termina com "success"
docker compose run --rm app ingest --reset    # ~15 notas, centenas de trechos
docker compose run --rm app ask "Em qual porta o Ollama expõe a API?" --show-context
```

`--show-context` lista cada item de contexto com a origem: `vector` (busca vetorial), `graph-neighbor` (nota vizinha por link ou tag) ou `graph-fact` (fato do catálogo/tags). O Neo4j Browser fica em http://localhost:7474 (usuário `neo4j`, senha do `.env`). Para ver o grafo:

```cypher
MATCH (r:Repository)-[:TAGGED]->(t:Tag {family: 'LibraryTags'}) RETURN r, t
```

## 4. Como uma pergunta é respondida

1. **retrieve** — a pergunta vira embedding (`search_query:` + texto) e o índice `chunk_embedding` devolve os 5 trechos mais próximos.
2. **route_request** — modo `vector` vai direto para a geração; modo `graph` passa pela expansão.
3. **expand** — busca notas ligadas por `LINKS_TO` às notas encontradas e notas de *outros* repositórios que compartilham TopicTags ou LibraryTags; reordena os trechos delas pela similaridade com a pergunta. Em seguida gera **fatos do grafo**: repositórios com as tags citadas na pergunta (por nome, como `selenium`, ou código, como `3.20`) e a ficha de cada repositório mencionado ou encontrado (visibilidade, data, tags).
4. **generate** — o modelo recebe o contexto numerado e a instrução de usar só ele, citar `[n]` e responder `NOT_FOUND` quando não houver resposta.
5. **verify** — mantém só citações que existem no contexto; sem citação válida, a resposta vira "não encontrei".

## 5. Avaliação

```bash
docker compose run --rm app eval                 # métricas determinísticas, ~2 respostas por pergunta
docker compose run --rm app eval --judge         # + TruLens (groundedness, relevância), bem mais lento
docker compose run --rm app eval --min-source-hit 0.6   # sai com código 1 abaixo do limite
```

O relatório `evals/results/latest.md` traz o resumo por modo, o `source_hit` por tipo de pergunta e o detalhe de cada pergunta. O esperado é o modo graph ganhar com folga nas perguntas de **catálogo** e **multi-hop** e empatar nas de **conteúdo**. Se o modo graph perder em conteúdo, o contexto extra está atrapalhando: reduza `KHG_EXPAND_K` ou `KHG_MAX_FACTS`.

Para adicionar uma pergunta, acrescente um item em `evals/questions.yaml` com `expected_sources` (caminho ou fragmento do nome do arquivo) e `expected_keywords` em minúsculas.

## 6. Observabilidade (Langfuse)

```bash
docker compose --profile observability up -d     # http://localhost:3000
```

Crie usuário e projeto, copie as chaves para `KHG_LANGFUSE_PUBLIC_KEY` e `KHG_LANGFUSE_SECRET_KEY` no `.env`. Cada `ask` vira um trace com spans `retrieve`, `expand` e a geração; cada pergunta do `eval` recebe as notas (`source_hit`, `keyword_recall` e as do TruLens) no próprio trace.

## 7. Usar com as suas notas ou um vault Obsidian

Coloque cada repositório ou vault em uma subpasta e rode `ingest --corpus <pasta> --reset`. São lidos:

- frontmatter YAML do README (contrato do `empty_repo`) e de qualquer nota (chaves terminadas em `Tags` ou `tags`);
- links Markdown relativos, URLs da organização no GitHub e `[[wikilinks]]`;
- `SEARCH_CONTENT.md`, se existir, para a árvore de tags e o catálogo.

Para outro modelo de embeddings, ajuste `KHG_EMBED_MODEL`, `KHG_EMBED_DIM` e os prefixos, e rode o `ingest --reset` (o índice vetorial tem dimensão fixa).

## 8. Problemas comuns

| Sintoma | Causa provável | Ação |
| --- | --- | --- |
| `Could not reach http://...:11434` | Ollama não subiu | `docker compose ps`, `docker compose logs ollama` |
| `model ... not found` | download não terminou | `docker compose logs ollama-models` |
| `returns N dimensions but KHG_EMBED_DIM=768` | modelo de embedding trocado | ajuste `KHG_EMBED_DIM` e rode `ingest --reset` |
| Muitas respostas "não encontrei" | modelo pequeno esquecendo citações | `KHG_LLM_MODEL=qwen2.5:7b`, ou `KHG_REQUIRE_CITATION=false` para depurar |
| `There is no procedure ... vector` | Neo4j antigo | use a imagem `neo4j:5.26` do compose |
