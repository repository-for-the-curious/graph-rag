# Corpus sources

`data/corpus/` is a snapshot of the Markdown files of the **public** repositories of
[repository-for-the-curious](https://github.com/repository-for-the-curious), released
under the MIT License like the rest of the organization. Refresh it with
`scripts/sync_corpus.sh`.

| Repository | Commit | Date | Files |
| --- | --- | --- | ---: |
| [knowledge-hub](https://github.com/repository-for-the-curious/knowledge-hub) | `9db5039` | 2026-04-30 | 2 |
| [how_to_containers](https://github.com/repository-for-the-curious/how_to_containers) | `02575d8` | 2026-03-21 | 13 |

Private repositories (🔒) are not copied. Their name, visibility, date and tags still
enter the graph from the catalog table in `knowledge-hub/SEARCH_CONTENT.md`, which is
what lets graph mode answer catalog questions that vector search cannot.

To use your own notes or an Obsidian vault, put each repository (or vault) in its own
sub-folder of a folder and run `python -m kh_graphrag ingest --corpus <folder> --reset`.
