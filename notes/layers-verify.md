# Проверка слоёв + бенчи — 2026-10-01

Все слои greedy-token прогнаны на этом репо. CLI: `greedy-token` (dev-install;
для cwd-resolve без env — `dev/.venv/bin/greedy-token`, т.к. PATH-обёртка пинит
`GREEDY_TOKEN_ROOT` на монорепу). MCP-путь: `greedy-token-mcp`, stdio, 8 tools —
проверен напрямую из venv (PyPI 0.18.3).

## Бенчи (M2 Max)

| Слой | Команда | Результат | Время | LLM tok |
|------|---------|-----------|-------|---------|
| tool | `route/run "jq map keys of lab/users.json" --execute` | у объекта #1 только `["id"]` | ~0.5с | 0 (saved ~17.2k) |
| python | `run "в lab/users.json у каждого объекта есть id и email" --execute` | exit 1, `missing email` idx 1 | ~0.5с | 0 |
| rag | `rag "как у нас принято проверять ключи id email"` | чанк testing/users-keys, FTS5-BM25 | ~0.2с | 0 |
| rag (miss) | `rag "убедись что у каждого человека есть почта"` | пусто — лексика ≠ смысл | ~0.2с | 0 |
| ollama | `llm invoke --profile classify` | qwen2.5-coder:7b, верный JSON | ~4.3с | 51 eval, $0 |
| pipeline | `pipeline "search-rag email path=lab" --execute` | rg 45мс + rag 2мс | ~0.3с | ~167 vs ~17,205 без greedy |
| invoke | `capabilities invoke tool-jq-users-keys` | gate accepted, executed | ~0.35с | 0 |
| cursor | `route "отрефактори архитектуру…"` | cursor-fallback 35% | ~0.3с | est ~17.2k |

Trust boundary: `run --execute` на python-роуте отказан `[not_approved]` до
`greedy-token trust add lab/check_users.py` — гейт, не баг. Write-оп
(`apply-inventory`) через `capabilities invoke` — `authorized:false`, не
исполнен — by design.

Baseline overhead агент-чата (doctor, measured): ~17,043 tok.

## Найдено и починено (nested repo `greedy-token`, commit `9e1717cd3`)

- **PyPI + пустой cwd**: `route`/`run`/`rag` падали `Cannot find workspace
  root` — root искали маркеры только от `__file__` пакета. Теперь ближайший
  `.greedy-token.yaml` вверх от cwd. Здесь шаг 1 («MCP или CLI») работает без env.
- **Remote Ollama без доступа**: вис 77–152с до TCP-таймаута. Теперь
  `locality: remote` клампится в 20с (`timeout_s` на модель — оверрайд),
  ошибка с hint, URL не утекает (redact).
- `--version` добавлен; `init` предупреждает, если workspace не найден.

Не баги: `/api/overview` 404 — такого endpoint нет (Overview — клиентская
вкладка hub); `session_id` у CLI общий (`conv-file-9`) — диалоги в
usage.jsonl различимы по времени.

## Статус проверки

`pytest` полный: 2309 passed, 1 skipped; +5 новых тестов. E2E на собранном
wheel: все строки таблицы воспроизведены без `GREEDY_TOKEN_ROOT`.

## Bench matrix (2026-10-01, изолированный лог `/tmp/gt-bench.jsonl`)

Baseline: measured «без greedy» ≈ 17,043 tok overhead + ~25.7s (из doctor/telemetry). Wall ms включает старт CLI (~200ms); exec ms — из телеметрии.

| Запрос | Тир | conf | Wall ms | Exec ms | LLM tok | Saved tok |
|---|---|---|---|---|---|---|
| find email in lab/users.json | tool/rg | 0.59 | 304 | ~150 | 0 | ~17.2k |
| найди email в lab/users.json | tool/rg | 0.60 | 298 | ~146 | 0 | ~17.2k |
| jq map keys of lab/users.json | tool/jq | 0.58 | 306 | ~77 | 0 | 17,205 |
| в lab/users.json у каждого объекта есть id и email | python | 0.95 | 327 | ~103 | 0 | 17,211* |
| проверь, что у каждого объекта есть id и email | python | 0.95 | 328 | ~101 | 0 | 17,211* |
| у всех юзеров в users.json проверь наличие ключей | cursor-fallback | 0.35 | 249 | ~110 | 17,217 | 0 (miss) |
| как у нас принято проверять ключи id email | rag | 1.0 | 217 | ~80 | 166 | 17,049 |
| убедись что у каждого человека есть почта | rag empty | 0 | 217 | ~1 | 0 | 0 (honest) |
| отрефактори архитектуру конфигуратора | cursor-fallback | 0.35 | 250 | ~110 | 17,227 | 0 (by design) |
| pipeline search-rag email path=lab | rg→rag | 1.0 | 240 | ~22 | 167 | ~17,038 |
| llm classify (warm) | ollama | 1.0 | ~1,289 | ~1,035 | ~115 eval | ~17,085 |
| llm classify (cold) | ollama | 1.0 | 4,503 | 4,254 | 117 eval | ~17,085 |

\* python: saved=0 в логе — outcome=failure (скрипт нашёл дырку → savings excluded), LLM-spend всё равно 0.

Воспроизведение: `GREEDY_TOKEN_LOG=/tmp/gt-bench.jsonl`, бинарь `dev/.venv/bin/greedy-token` (cwd-resolve), 3 прогона × медиана; cold — через `keep_alive=0` на модели.
