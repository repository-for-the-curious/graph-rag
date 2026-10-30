# Leitfaden — knowledge_hub_graphrag

[⬅ README](../../README.md) · [Português](../pt/Guide.md) · [English](../en/Guide.md)

## 1. Was das Projekt zeigt

Dass explizite Beziehungen zwischen Dokumenten (Links, Tags, Katalog) Fragen beantworten, die Vektorsuche nicht erreicht, und dass sich dieser Unterschied **messen** lässt. Alles läuft lokal: Neo4j, Ollama und Python, ohne API-Schlüssel.

## 2. Voraussetzungen

| Punkt | Minimum | Hinweis |
| --- | --- | --- |
| Docker + Docker Compose v2.24+ | erforderlich | siehe [how_to_containers](https://github.com/repository-for-the-curious/how_to_containers) |
| Freier RAM | 8 GB | Neo4j (1 GB Heap) + `qwen2.5:3b` |
| Speicher | 5 GB | Images + Modelle |
| GPU | optional | NVIDIA: den `deploy`-Block des Dienstes `ollama` einkommentieren |

## 3. Schritt für Schritt

```bash
cp .env.example .env
docker compose up -d                          # beim ersten Start werden qwen2.5:3b und nomic-embed-text geladen
docker compose logs -f ollama-models          # Download verfolgen; endet mit "success"
docker compose run --rm app ingest --reset    # ~15 Notizen, einige hundert Abschnitte
docker compose run --rm app ask "Auf welchem Port stellt Ollama die API bereit?" --show-context
```

`--show-context` zeigt jedes Kontextelement mit Herkunft: `vector` (Vektorsuche), `graph-neighbor` (Nachbarnotiz über Link oder Tag) oder `graph-fact` (Fakt aus Katalog/Tags). Der Neo4j Browser läuft unter http://localhost:7474 (Benutzer `neo4j`, Passwort aus `.env`). Graph ansehen:

```cypher
MATCH (r:Repository)-[:TAGGED]->(t:Tag {family: 'LibraryTags'}) RETURN r, t
```

## 4. Wie eine Frage beantwortet wird

1. **retrieve** — die Frage wird eingebettet (`search_query:` + Text), der Index `chunk_embedding` liefert die 5 nächsten Abschnitte.
2. **route_request** — Modus `vector` geht direkt zur Generierung, Modus `graph` über die Erweiterung.
3. **expand** — sammelt per `LINKS_TO` verbundene Notizen und Notizen *anderer* Repositories mit gemeinsamen TopicTags oder LibraryTags und sortiert deren Abschnitte nach Ähnlichkeit zur Frage. Dazu kommen **Graph-Fakten**: Repositories mit den in der Frage genannten Tags (per Name wie `selenium` oder Code wie `3.20`) und eine Karte für jedes genannte oder gefundene Repository (Sichtbarkeit, Datum, Tags).
4. **generate** — das Modell erhält den nummerierten Kontext mit der Anweisung, nur diesen zu nutzen, `[n]` zu zitieren und `NOT_FOUND` zu antworten, wenn die Antwort fehlt.
5. **verify** — behält nur Zitate, die im Kontext existieren; ohne gültiges Zitat lautet die Antwort „nicht gefunden“.

## 5. Evaluation

```bash
docker compose run --rm app eval                 # deterministische Metriken, 2 Antworten pro Frage
docker compose run --rm app eval --judge         # + TruLens (Groundedness, Relevanz), deutlich langsamer
docker compose run --rm app eval --min-source-hit 0.6   # Exit-Code 1 unter dem Schwellwert
```

`evals/results/latest.md` enthält die Zusammenfassung je Modus, `source_hit` je Fragetyp und Details je Frage. Erwartet wird, dass der Graph-Modus bei **Katalog**- und **Multi-Hop**-Fragen klar gewinnt und bei **Inhalts**fragen gleichauf liegt. Verliert er bei Inhaltsfragen, stört der zusätzliche Kontext: `KHG_EXPAND_K` oder `KHG_MAX_FACTS` senken.

Neue Frage: einen Eintrag in `evals/questions.yaml` mit `expected_sources` (Pfad oder Dateinamen-Fragment) und kleingeschriebenen `expected_keywords` ergänzen.

## 6. Observability (Langfuse)

```bash
docker compose --profile observability up -d     # http://localhost:3000
```

Benutzer und Projekt anlegen, Schlüssel in `KHG_LANGFUSE_PUBLIC_KEY` und `KHG_LANGFUSE_SECRET_KEY` in `.env` eintragen. Jedes `ask` wird ein Trace mit Spans `retrieve`, `expand` und der Generierung; jede `eval`-Frage erhält ihre Scores (`source_hit`, `keyword_recall` und die von TruLens) am Trace.

## 7. Eigene Notizen oder ein Obsidian-Vault

Jedes Repository bzw. jeden Vault in einen eigenen Unterordner legen und `ingest --corpus <Ordner> --reset` ausführen. Gelesen werden:

- YAML-Frontmatter des README (Vertrag von `empty_repo`) und jeder Notiz (Schlüssel, die auf `Tags` enden, oder `tags`);
- relative Markdown-Links, GitHub-URLs der Organisation und `[[Wikilinks]]`;
- `SEARCH_CONTENT.md`, falls vorhanden, für Tag-Baum und Katalog.

Für ein anderes Embedding-Modell `KHG_EMBED_MODEL`, `KHG_EMBED_DIM` und die Präfixe setzen und `ingest --reset` ausführen (der Vektorindex hat eine feste Dimension).

## 8. Fehlerbehebung

| Symptom | Wahrscheinliche Ursache | Maßnahme |
| --- | --- | --- |
| `Could not reach http://...:11434` | Ollama läuft nicht | `docker compose ps`, `docker compose logs ollama` |
| `model ... not found` | Download nicht fertig | `docker compose logs ollama-models` |
| `returns N dimensions but KHG_EMBED_DIM=768` | Embedding-Modell geändert | `KHG_EMBED_DIM` setzen und `ingest --reset` |
| Viele „nicht gefunden“-Antworten | kleines Modell lässt Zitate weg | `KHG_LLM_MODEL=qwen2.5:7b` oder zum Debuggen `KHG_REQUIRE_CITATION=false` |
| `There is no procedure ... vector` | altes Neo4j | das Image `neo4j:5.26` aus dem Compose nutzen |
