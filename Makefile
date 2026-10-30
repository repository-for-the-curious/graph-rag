.PHONY: up ingest ask eval eval-judge test observability down

Q ?= Quais repositórios usam a biblioteca selenium?

up:            ## start neo4j + ollama and download the models
	docker compose up -d

ingest:        ## load data/corpus into Neo4j (from scratch)
	docker compose run --rm app ingest --reset

ask:           ## make ask Q="your question"
	docker compose run --rm app ask "$(Q)" --show-context

eval:          ## vector x graph comparison -> evals/results/latest.md
	docker compose run --rm app eval

eval-judge:    ## same, plus TruLens LLM-as-judge metrics (slower)
	docker compose run --rm app eval --judge

test:          ## unit tests, no services needed
	python -m pytest -q

observability: ## start Langfuse on http://localhost:3000
	docker compose --profile observability up -d

down:
	docker compose --profile observability down
