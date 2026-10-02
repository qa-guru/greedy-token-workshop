#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$ROOT/scripts/ollama/_common.sh"

FILE="${1:?usage: classify-file.sh <path>}"
[[ -f "$ROOT/$FILE" ]] || { echo "classify-file: no such file under workspace root: $FILE" >&2; exit 2; }

# Workshop task: which objects in a JSON array lack required fields.
# The file goes to the local LLM via --user-file — it is NOT read into
# the agent context (that is the point of the script tier).
SYSTEM='Ты валидатор JSON-массива объектов. Для каждого объекта проверь наличие полей id и email (отсутствующим считается и null, и ""). Ответь ОДНИМ JSON-объектом без прозы и без markdown-ограждений:
{"total": <число объектов>, "valid": <число валидных>, "invalid": [{"id": <id или null>, "missing": ["email"]}]}
Если на входе не массив объектов — {"error": "not a json array"}.'

ollama_file "$SYSTEM" "$ROOT/$FILE" "classify"
