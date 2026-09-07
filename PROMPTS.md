# Промпты

SSOT для чата. План преподавателя на эти тексты ссылается, а не копирует второй раз.

Правила, из-за которых первая пара развалилась:

1. Первая строка промпта — **шаг N / PR #N / ветка**. Нет букв L и P.
2. Один чат = один шаг. Новый Agent / New Task после коммита.
3. В конце — коммит. «Не коммить» писать нельзя: тогда не будет PR.
4. STOP, если cwd это `zero-design-system` или в корне есть `docs/CONTEXT.md`.
5. Не вставлять сюда промпты про правку пакета greedy-token, хаб `#/ladder`, переписывание слайдов — это подготовка до эфира.
6. Смоук шага 1 («найди email») **намеренно** ищет адреса. Проверка ключей — шаги 3 и 4.

Перед шагом:

```bash
git checkout main
git checkout -b prN-<имя>
```

После шага: `git add` · `git commit` · PR в свой форк.

---

## Шаг 1 — установка · ветка `pr1-install`

```text
Это шаг 1 / PR #1, ветка pr1-install. Не подготовка пакета, не монорепо.
STOP сразу, если cwd содержит zero-design-system или файл docs/CONTEXT.md — напиши «открой форк greedy-token-workshop» и ничего не делай.

Помоги поставить greedy-token в этот воркспейс и проверить, что он живой. По шагам, останавливайся после каждого и показывай вывод.
1. Проверь python 3.12+, ripgrep и Ollama: python3 --version, rg --version, curl -s localhost:11434/api/tags. Нет Ollama — напиши и иди дальше, не ставь.
2. pip install "greedy-token[mcp]".
3. greedy-token init --profile solo и greedy-token doctor. Покажи вывод doctor целиком.
4. Если doctor жалуется на модель — покажи, какая модель в конфиге и какие есть в Ollama. Конфиг не меняй без моего «да».
5. Cursor: скажи, что нажать в Customize → MCPs, чтобы подхватить .cursor/mcp.json. Cline: достаточно CLI.
6. Смоук: найди email в lab/users.json через greedy-token (MCP search или CLI). Покажи футер с тиром. Это список адресов, не проверка ключей.

Не ставь ничего кроме greedy-token и его зависимостей. Не docker. Не правь чужие конфиги без «да». Если шаг упал — стоп, ошибку целиком.
В конце закоммить на pr1-install: mcp, rule, фикстура lab/users.json.
```

Коротко:

```text
Шаг 1 / PR #1 / pr1-install. STOP если монорепо.
python3.12+ / rg / ollama (если есть), pip install "greedy-token[mcp]", init --profile solo, doctor.
MCP: Customize → MCPs, не Marketplace. Смоук: поиск email в lab/users.json (адреса, не схема).
Запрет: лишние пакеты, docker, правка конфигов без «да», продолжать после падения, «не коммить».
Конец: коммит на pr1-install.
```

---

## Шаг 2 — голый чат · ветка `pr2-chat`

Новый чат. Cline + Ollama лучше Cursor Agent: у Agent есть Read, дрейф часто **не** воспроизводится (так было 7 сентября).

```text
Это шаг 2 / PR #2, ветка pr2-chat. Без greedy-token, без MCP, без Read/Grep если можешь отказаться.
Проверь lab/users.json: у каждого объекта есть id и email.
Ответь коротко, по-русски.
Не комментируй задание. Не предлагай скрипт.
```

Пять раз вставить тот же текст (New Task каждый раз, либо пять сообщений). В `notes/02-chat.md` записать два-три ответа **дословно** либо строку: «Cursor Agent каждый раз нашёл дырку через Read — дрейф не вышел».

Коротко:

```text
Шаг 2 / PR #2. Без greedy-token. Один и тот же текст 5 раз: «Проверь lab/users.json: у каждого объекта есть id и email. Коротко, по-русски.»
Записать ответы в notes/02-chat.md. Коммит.
```

---

## Шаг 3 — поиск и ключи · ветка `pr3-search`

```text
Это шаг 3 / PR #3, ветка pr3-search. Через greedy-token, не Read/Grep.
Проверь lab/users.json — у каждого объекта есть ключи id и email.
Не ищи слово email. Нужна проверка схемы, не список адресов.
1) greedy_token_route (или greedy-token route) на эту задачу.
2) Если тир tool/jq — выполни, покажи jq и футер.
3) Новые скрипты не пиши, пока я не скажу.
Ожидание: у объекта id 2 нет ключа email.
В конце закоммить jq-маршрут в .greedy-token.yaml, если его ещё нет.
```

Если соседний чат «не проходит»: агент снова ищет слово `email`. Остановить и повторить «не ищи слово email».

---

## Шаг 4 — скрипт · ветка `pr4-script`

```text
Это шаг 4 / PR #4, ветка pr4-script. Через greedy-token, не Read/Grep, не ищи слово email.

1. Положи lab/users.ok.json — все три объекта с id и email.
2. Напиши lab/check_users.py: JSON на stdout; exit 0 если ок, 1 если дырка, 2 если нет файла или аргумента. Лови битый JSON и не-dict.
3. Прогони и покажи stdout + echo $?:
   python3 lab/check_users.py lab/users.json
   python3 lab/check_users.py lab/users.ok.json
   python3 lab/check_users.py
   Ожидание: 1 / 0 / 2.
4. Добавь в .greedy-token.yaml роут python-check-users-keys с командой на этот скрипт.
   В patterns обязательно русская фраза «у каждого объекта есть id и email» — иначе route уйдёт в cursor-fallback.
   jq-маршрут не ломай.

Повторно модель на тот же прогон не вызывай.
В конце закоммить скрипт, эталон и роут. Это и есть PR.
```

Коротко:

```text
Шаг 4 / PR #4. check_users.py, JSON, exit 1/0/2, роут python-check-users-keys + русские patterns. Коммит. Не «не коммить».
```

---

## Шаг 5 — RAG · ветка `pr5-docs`

```text
Это шаг 5 / PR #5, ветка pr5-docs. Через greedy-token, не Read/Grep кода, не greedy_token_search.

1. Положи мини-корпус:
   docs/rag/testing/users-keys.md — как у нас проверяют фикстуру users: ключи id и email, скрипт check_users.py, exit 0/1/2.
   docs/rag/testing/allure-severity.md — про labels severity, без слов id/email/users.
   docs/rag/manifest.jsonl — оба чанка (id, domain, path, tags).
2. Один greedy_token_rag: «как у нас принято проверять ключи id email у users».
   Покажи чанк, тир и футер.
3. Второй greedy_token_rag: «убедись что у каждого человека есть почта».
   Не подменяй синонимами в запросе. Покажи, что лексика ≠ смысл (пусто или чужой чанк).
4. Не вызывай Ollama и не пиши новый python-скрипт.

Ожидание: первый запрос бьёт users-keys; второй — ложь лексики.
Коммит корпуса.
```

---

## Шаг 6 — локальная Ollama · ветка `pr6-local`

```text
Это шаг 6 / PR #6, ветка pr6-local. Через greedy-token (не Read/Grep, не search, не rag).

1. greedy-token doctor без --apply. Покажи configured, installed, рекомендацию. Конфиг не меняй, ollama pull не делай.
2. Классифицируй 3 объекта из lab/users.json локальной Ollama: у записи оба ключа id и email или нет. Профиль classify / 7b.
   CLI: greedy-token llm invoke --profile classify (или эквивалент). Не платный Agent-чат как исполнитель.
3. Покажи: какая модель ответила, латентность, JSON, тир ollama, футер.
4. Одним абзацем: почему 7b хватило и когда эскалировать на 14b / 30b. 30b не вызывай.

Запрет: docker, правка ~/.greedy-token/config.yaml без «да», новый python-скрипт, повтор RAG.
Ожидание: локальный 7b, у id 2 нет email.
Локальную и облачную модели не склеивать в одну. В yaml это разные id (local-fast и cloud/heavy).
Коммит заметок/пресета, не секретов.
```

На первой паре 7b занял порядка 7–8 с. Своё число замерить, чужое не подставлять.

---

## Шаг 7 — облако · ветка `pr7-cloud` · отрезаемый

Студенческий чат (нет учётки):

```text
Это шаг 7 / PR #7, ветка pr7-cloud. Не шаг 1. Шаг 6 уже был.
Через greedy-token, не Read/Grep, не search, не rag, не локальный 30b вместо облака.

1. Probe: curl -sS -o /tmp/ollama-tags.json -w "%{http_code}" https://ollama.qa.guru/api/tags
   Покажи код. Тело с ошибкой можно, логин/пароль — нет.
2. Если 401/403 — стоп. Напиши: шаг 7 без доступа. Локальный loopback без Authorization. Облако — nginx Basic.
   Конфиг не меняй, пароль не подбирай, docker не поднимай, localhost:11434 не подставляй вместо облака.
3. Если 200 — та же классификация 3 объектов, что на шаге 6, профиль heavy / 30b на ollama.qa.guru.
   Учётка только из уже заданных env (OLLAMA_* / CHEAP_LLM_*), в файлы не копируй.

Не ollama pull. Не правь config без «да».
Ожидание без доступа: 401 и стоп.
```

Учительский чат (учётка уже есть, **не** в студенческий репо):

```text
Это шаг 7 на машине преподавателя. Env: set -a; source ~/.config/ollama-qa-guru.env; set +a
Пароль в чат и в git не писать.
Probe https://ollama.qa.guru/api/tags с Basic. Если 200 — classify/heavy, покажи модель и латентность vs шаг 6.
Не подменять облако localhost. Не коммитить .env.
```

Две дешёвые модели в `.greedy-token.yaml` можно: `local-fast` и `cloud`. Это не замена одной другой.

---

## Шаг 8 — прораб · ветка `pr8-orchestrator` · отрезаемый

```text
Это шаг 8 / PR #8, ветка pr8-orchestrator. Платная модель — прораб, не исполнитель.

Задача та же: «в lab/users.json у каждого объекта есть id и email».
Не перепроверяй файл глазами, не ищи слово email, не вызывай Ollama, не пиши новый скрипт, не делай crystallize promote.

1. Один greedy_token_route на эту задачу. Покажи выбранный тир, id роута, команду.
2. Исполнитель — только тот дешёвый слой, который назвал route (python-check-users-keys / jq).
   Покажи stdout и exit. Вердикт берёшь из скрипта, не из своей интерпретации JSON.
3. Таблица на 4 строки — что платной модели ещё можно, и что уже нельзя:

| Роль | Делает сейчас? | Комментарий |
| маршрутизатор | | |
| автор кристалла | | check_users.py уже есть — не писать второй раз |
| ремонтник | | скрипт не врёт, чинить нечего |
| голова / wiring | | этой задачей не занимаемся |

Запрет: docker, правка конфига, ollama pull, grep слова email.
Ожидание: python / python-check-users-keys, exit 1, missing email у index 1.
Если route дал cursor-fallback — не вызывай Ollama. Скажи, каких русских patterns не хватает в yaml. Это отдельный мини-шаг 8b, не новый слой.
Коммит, если правил patterns.
```

Шаг 8b (если fallback), из первой пары:

```text
Это шаг 8b, роль «голова / wiring», не новый номер слоя.
greedy_token_route на «в lab/users.json у каждого объекта есть id и email» дал cursor-fallback.
Добавь в существующий роут python-check-users-keys 2–3 паттерна под эту русскую фразу.
jq-роут и llm-блок не трогай. Скрипт не меняй.
Один route той же фразой. Ожидание: python / python-check-users-keys.
Исполни python3 lab/check_users.py lab/users.json. Вердикт только из скрипта.
```

---

## Crystallize CLI — не на паре, если нет времени

На первой паре `promote` без `draft` падал, `draft` без живой cheap LLM отдавал пустой шаблон, потом скрипт допиливали руками.

```text
greedy-token crystallize draft python-check-users-keys --since 1d
# смотрим файл, это должен быть чекер, не TODO
greedy-token crystallize promote python-check-users-keys
```

Имя роута в команде = id в yaml. Выдуманные `check-users` / `script-python-…` не находит.

---

## Хаб — показ, не слой

```text
Хаб, не новая проверка users.json.
greedy-token hub serve --host 127.0.0.1 --port 8787
Скажи открыть руками http://127.0.0.1:8787 (флага --open нет).
Не docker, не 0.0.0.0, конфиг не меняй, crystallize promote не делай.
Какие вкладки живые — по факту. Вида прогресса по шагам в PyPI 0.16 может не быть — так и напиши, не рисуй макет.
```
