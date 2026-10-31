# Eval results

- Generated: 2026-10-30 23:01 UTC
- LLM: `qwen2.5:3b` · embeddings: `nomic-embed-text` · judge: `off`
- Cases: 19

## Summary

| Mode | source_hit | keyword_recall | groundedness | answer_relevance | context_relevance | latency_s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| vector | 0.32 | 0.18 | – | – | – | 78.14 |
| graph | 0.47 | 0.35 | – | – | – | 153.40 |

## source_hit by question kind

| Kind | vector | graph |
| --- | ---: | ---: |
| catalog | 0.17 | 0.67 |
| content | 0.33 | 0.22 |
| multi-hop | 0.00 | 0.50 |
| negative | 1.00 | 1.00 |

## Per question

| Case | Mode | source_hit | keyword_recall | Cited |
| --- | --- | ---: | ---: | --- |
| c01-ollama-port | vector | 0.00 | 0.00 | – |
| c01-ollama-port | graph | 0.00 | 1.00 | how_to_containers/README.md |
| c02-ollama-amd | vector | 0.00 | 0.00 | – |
| c02-ollama-amd | graph | 0.00 | 0.00 | – |
| c03-ollama-endpoints | vector | 0.00 | 0.00 | – |
| c03-ollama-endpoints | graph | 1.00 | 0.00 | how_to_containers/README.md, how_to_containers/docs/pt/Journey_to_Ollama_Docker.md |
| c04-git-line-endings | vector | 1.00 | 1.00 | how_to_containers/docs/pt/Guia_Guia_WSL_com_Ubuntu_para_Repositorios.md |
| c04-git-line-endings | graph | 1.00 | 1.00 | how_to_containers/docs/pt/Guia_Guia_WSL_com_Ubuntu_para_Repositorios.md |
| c05-compose-check | vector | 0.00 | 0.00 | – |
| c05-compose-check | graph | 0.00 | 0.00 | – |
| c06-raspberry | vector | 1.00 | 1.00 | how_to_containers/docs/de/Guia_instala├º├úo_Docker_e_docker_compose.md, how_to_containers/docs/de/Install_Docker.md, how_to_containers/docs/pt/Guia_instala├º├úo_Docker_e_docker_compose.md |
| c06-raspberry | graph | 0.00 | 1.00 | how_to_containers/docs/de/Guia_instala├º├úo_Docker_e_docker_compose.md |
| c07-hub-purpose | vector | 1.00 | 1.00 | knowledge-hub/README.md |
| c07-hub-purpose | graph | 0.00 | 0.00 | – |
| c08-contribution-flow | vector | 0.00 | 0.00 | – |
| c08-contribution-flow | graph | 0.00 | 0.00 | – |
| c09-visibility-icon | vector | 0.00 | 0.00 | – |
| c09-visibility-icon | graph | 0.00 | 0.00 | – |
| k01-selenium | vector | 0.00 | 0.00 | – |
| k01-selenium | graph | 1.00 | 1.00 | knowledge-hub/SEARCH_CONTENT.md |
| k02-deployment | vector | 0.00 | 0.00 | – |
| k02-deployment | graph | 1.00 | 0.00 | knowledge-hub/SEARCH_CONTENT.md |
| k03-webscraping | vector | 0.00 | 0.00 | – |
| k03-webscraping | graph | 1.00 | 0.67 | knowledge-hub/SEARCH_CONTENT.md |
| k04-library-tags | vector | 1.00 | 0.00 | knowledge-hub/SEARCH_CONTENT.md |
| k04-library-tags | graph | 0.00 | 0.00 | – |
| k05-private | vector | 0.00 | 0.00 | – |
| k05-private | graph | 1.00 | 1.00 | knowledge-hub/SEARCH_CONTENT.md |
| k06-created | vector | 0.00 | 0.00 | – |
| k06-created | graph | 0.00 | 0.00 | – |
| m01-ollama-and-orchestration | vector | 0.00 | 0.00 | – |
| m01-ollama-and-orchestration | graph | 1.00 | 0.33 | how_to_containers/docs/en/Journey_to_Ollama_Docker.md, knowledge-hub/SEARCH_CONTENT.md |
| m02-textual-editor | vector | 0.00 | 0.00 | – |
| m02-textual-editor | graph | 0.00 | 0.00 | – |
| n01-out-of-scope | vector | 1.00 | – | – |
| n01-out-of-scope | graph | 1.00 | – | – |
| n02-out-of-scope | vector | 1.00 | – | – |
| n02-out-of-scope | graph | 1.00 | – | – |
