# greedy-token-workshop

Учебный репозиторий занятия 5 курса **AI-first QA**: одна и та же проверка идёт восемью шагами — от голого чата до скрипта, который можно скормить CI.

Не путать с [greedy.guru](https://greedy.guru) (браузерный mill). Здесь пакет [greedy-token](https://pypi.org/project/greedy-token/) и Python.

Студенты **форкают** этот репо. Монорепо преподавателя не открывают.

## Одна задача на все шаги

В `lab/users.json` у каждого объекта должны быть ключи `id` и `email`. У записи с `"id": 2` ключа `email` нет — это дырка.

```bash
python3 lab/check_users.py lab/users.json      # exit 1
python3 lab/check_users.py lab/users.ok.json   # exit 0
python3 lab/check_users.py                     # exit 2
```

Поиск слова `email` в файле — это **не** эта проверка. Поиск находит адреса. Скрипт проверяет ключи.

## Восемь шагов = восемь PR

В учебном контуре нет букв L и P. Только **шаг** и **PR**.

| PR | Ветка | Что появляется | Когда идти дальше |
|----|--------|----------------|-------------------|
| [#1](../../pull/1) | `pr1-install` | MCP/CLI живой, фикстура на месте | `doctor` зелёный, 6 tools или CLI отвечает |
| [#2](../../pull/2) | `pr2-chat` | Зафиксирован дрейф голого чата | Два ответа на один промпт — разный текст **или** честно: Cursor Agent с Read не врёт |
| [#3](../../pull/3) | `pr3-search` | jq-маршрут по ключам | 0 токенов в платную; это схема, не список адресов |
| [#4](../../pull/4) | `pr4-script` | `lab/check_users.py` | JSON + exit 1 / 0 / 2 |
| [#5](../../pull/5) | `pr5-docs` | два RAG-чанка | «как у нас принято» находит чанк; синоним — мимо |
| [#6](../../pull/6) | `pr6-local` | локальная Ollama 7b | classify на ноуте, без 30b |
| [#7](../../pull/7) | `pr7-cloud` | [ollama.qa.guru](https://ollama.qa.guru) | 401 без учётки — **стоп**, не подменять localhost |
| [#8](../../pull/8) | `pr8-orchestrator` | платная модель = прораб | `route` зовёт скрипт, модель файл глазами не перечитывает |

Шаги 7 и 8 на паре **отрезаемые**. Дома обязательны 1, 4 и один свой скрипт из [ASSIGNMENT.md](ASSIGNMENT.md).

Карта: [STEPS.md](STEPS.md). Промпты в чат: [PROMPTS.md](PROMPTS.md). Один чат = один PR. Коммит в конце шага — часть задания, не опция.

## Окна

| Кто | Что открыть |
|-----|-------------|
| Студент | форк этого репо, VS Code + Cline + Ollama (Cursor — по желанию) |
| Преподаватель на проекторе | этот репо, не `zero-design-system`, не `ai-first-student-workspace`, не папку `greedy-guru-lesson` |

## Установка (шаг 1)

Python **3.12+**, `rg`, локальная Ollama по желанию.

```bash
pip install "greedy-token[mcp]"
greedy-token init --profile solo
greedy-token doctor
```

Cursor: Customize → MCPs → **+ New MCP Server** → вставить `.cursor/mcp.json` (если файла ещё нет). Marketplace пустой — сервер свой. Новый Agent-чат после сохранения.

Cline: MCP не обязателен; хватает CLI.

## Честно про деньги

Чат Cursor/Cline уже тарифицируется. Ноль LLM — это терминал, CI и хук, не «бесплатный агент». Цифры `$82/$820` из README пакета — иллюстрация CLI-микса, не ваш счёт за эту пару.

## Хаб

```bash
greedy-token hub serve --host 127.0.0.1 --port 8787
```

Открыть руками [http://127.0.0.1:8787](http://127.0.0.1:8787). Флага `--open` нет. В PyPI 0.16 вкладки Overview / Sessions / Crystals / Routes / Providers / Tests. Вида «прогресс по шагам» в пакете может не быть — не рисовать макет.
