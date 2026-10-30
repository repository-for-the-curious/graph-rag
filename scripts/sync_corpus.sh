#!/usr/bin/env bash
# Refresh data/corpus from the public repositories of repository-for-the-curious.
# Only Markdown files are copied. Private repositories stay out: their metadata
# still reaches the graph through knowledge-hub/SEARCH_CONTENT.md.
set -euo pipefail

ORG="https://github.com/repository-for-the-curious"
REPOS=("knowledge-hub" "how_to_containers" "$@")
DEST="$(cd "$(dirname "$0")/.." && pwd)/data/corpus"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

for repo in "${REPOS[@]}"; do
  echo "-> $repo"
  git clone --depth 1 --quiet "$ORG/$repo.git" "$TMP/$repo"
  rm -rf "${DEST:?}/$repo"
  (cd "$TMP/$repo" && find . -name '*.md' -not -path './.git/*' -print0 |
    while IFS= read -r -d '' f; do
      mkdir -p "$DEST/$repo/$(dirname "$f")"
      cp "$f" "$DEST/$repo/$f"
    done)
  echo "   $(git -C "$TMP/$repo" rev-parse --short HEAD) $(git -C "$TMP/$repo" log -1 --format=%cs)"
done
echo "Done. Update data/CORPUS_SOURCES.md with the commits above, then: make ingest"
