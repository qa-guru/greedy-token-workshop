#!/usr/bin/env bash
# Workshop variant: greedy-token is pip-installed (`greedy-token` on PATH),
# no repo venv. All provider calls go through `greedy-token llm invoke`
# so the spend guard applies — a denied call must fail closed.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export GREEDY_TOKEN_ROOT="${GREEDY_TOKEN_ROOT:-$ROOT}"

ollama_chat() {
  local system="$1" prompt="$2" profile="${3:-classify}"
  if ! command -v greedy-token >/dev/null 2>&1; then
    echo "ollama_chat: greedy-token CLI not found; refusing unguarded call" >&2
    return 1
  fi
  greedy-token llm invoke \
    --profile "$profile" --system "$system" --user "$prompt"
}

ollama_file() {
  local system="$1" file="$2" profile="${3:-classify}"
  if ! command -v greedy-token >/dev/null 2>&1; then
    echo "ollama_file: greedy-token CLI not found; refusing unguarded call" >&2
    return 1
  fi
  greedy-token llm invoke \
    --profile "$profile" --system "$system" --user-file "$file"
}
