#!/usr/bin/env bash
# Remove ficheiros *:Zone.Identifier (marcações do Windows/WSL) sob a pasta do script.
#
# Uso: clear_zone.Identifier_files.sh [maxdepth [passes]]
#   maxdepth — mesmo critério que find(1) -maxdepth (1 = só a raiz IA_suitcase; 2 = +1 nível; etc.).
#              Omitir = sem limite (toda a árvore).
#   passes   — quantas varreduras seguidas (defeito: 1); ajuda com locks/races ou ficheiros tardios.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAXDEPTH_ARG=()
PASSES=1

usage() {
  echo "Uso: $0 [maxdepth [passes]]" >&2
  echo "  maxdepth  inteiro >= 1 (find -maxdepth); omitir = ilimitado" >&2
  echo "  passes    inteiro >= 1, número de repetições (defeito: 1)" >&2
}

if [[ "${1:-}" == -h || "${1:-}" == --help ]]; then
  usage
  exit 0
fi

if [[ -n "${1:-}" ]]; then
  if ! [[ "$1" =~ ^[0-9]+$ ]] || [[ "$1" -lt 1 ]]; then
    echo "Erro: maxdepth tem de ser um inteiro >= 1" >&2
    usage
    exit 1
  fi
  MAXDEPTH_ARG=(-maxdepth "$1")
fi

if [[ -n "${2:-}" ]]; then
  if ! [[ "$2" =~ ^[0-9]+$ ]] || [[ "$2" -lt 1 ]]; then
    echo "Erro: passes tem de ser um inteiro >= 1" >&2
    usage
    exit 1
  fi
  PASSES="$2"
fi

for ((i = 1; i <= PASSES; i++)); do
  if [[ "$PASSES" -gt 1 ]]; then
    echo "Varredura $i / $PASSES ..." >&2
  fi
  find "$ROOT" "${MAXDEPTH_ARG[@]}" -type f -name '*:Zone.Identifier' -print -delete
done
