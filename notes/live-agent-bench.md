# Live-agent benchmark — «с greedy» vs «без greedy»

Протокол живых прогонов. Парные промпты: одна задача, два исполнения.
Цель — замерить **реальные** токены агент-сессии, а не оценку baseline.

## Условия

- Одна модель на весь прогон (записать какую — разные модели = разные цены).
- Каждый промпт — **свежий чат** (история диалога раздувает контекст и ломает
  сравнение).
- «Без greedy» — чат вне `greedy-token-workshop` **или** промпт с префиксом
  `nogreedy:` — иначе advisory-хук перехватит и попадёт в advisory.jsonl.
- «С greedy» — в воркшопе, MCP подключён (`.cursor/mcp.json` ставит root).
  Фолбэк без MCP: `greedy-token` CLI из `dev/.venv/bin`.
- Фиксировать: модель, wall-time до финального ответа, токены (usage IDE),
  число tool-вызовов, корректность ответа.

## Пара A — проверка ключей users.json (tool / python)

**Без greedy:**
```
Проверь, что в файле /Users/stanislav/greedy-token-workshop/lab/users.json
у каждого объекта есть ключи id и email. Скажи, у какого объекта чего не хватает.
```
Наивный агент: Read файла + ответ. Ожидание: index 1 без email.

**С greedy:**
```
Через greedy-token (greedy_token_route → greedy_token_invoke или CLI
route+run --execute): проверь, что в lab/users.json у каждого объекта есть
id и email. Не читай файл Read — только через greedy.
```
Ожидание: python-check-users-keys, exit 1, missing email у index 1, ~0 tok.

## Пара B — поиск email (tool / rg)

**Без greedy:**
```
Найди все строки с "email" в /Users/stanislav/greedy-token-workshop/lab/
и покажи их.
```

**С greedy:**
```
Через greedy-token: найди email в lab/ (route "find email in lab/users.json",
затем выполни). Не используй Grep — только greedy.
```
Ожидание: tool-rg-search, 0 tok.

## Пара C — проектная конвенция (rag)

**Без greedy:**
```
Как в этом проекте принято проверять ключи id и email у users?
Найди ответ в документации /Users/stanislav/greedy-token-workshop/docs/.
```

**С greedy:**
```
Через greedy-token: greedy_token_rag "как у нас принято проверять ключи
id email у users". Не читай файлы сам — только rag.
```
Ожидание: чанк testing/users-keys, ~166 tok.

## Пара D — классификация (ollama)

**Без greedy:**
```
Прочитай /Users/stanislav/greedy-token-workshop/lab/users.json и верни JSON
[{index, has_id, has_email}] для каждого объекта.
```
Платная модель делает вывод сама.

**С greedy:**
```
Через greedy-token: llm invoke --profile classify с объектами из
lab/users.json, верни только JSON [{index, has_id, has_email}].
Сам не рассуждай по файлу — передай в llm.
```
Ожидание: ollama local, ~115 eval tok, $0.

## Пара E — суждение (cursor fallback)

**Без greedy:**
```
Отрефактори архитектуру конфигуратора: разбей на компоненты, предложи
структуру и первые шаги. Код не пиши.
```

**С greedy:**
```
Через greedy-token route: "отрефактори архитектуру конфигуратора, разбей
на компоненты" — покажи какой тир выбран и почему; потом ответь сам
на вопрос (суждение не кристаллизуется — тут greedy только маршрутизирует).
```
Ожидание: cursor-fallback ~35%, дальше оба прогона идут дорогой моделью —
на этой паре экономии нет и не должно быть (контроль честности).

## Пара F — контроль промаха роутинга

**Без greedy:**
```
У всех юзеров в /Users/stanislav/greedy-token-workshop/lab/users.json
проверь наличие ключей и скажи, где чего нет.
```

**С greedy:**
```
Через greedy-token route: "у всех юзеров в users.json проверь наличие
ключей". Если тир cursor-fallback — скажи об этом, затем ответь сам.
```
Ожидание: промах роутинга → fallback. Честный отрицательный результат:
не всякая формулировка экономит.

## Что писать в таблицу

На каждую пару — **4 прогона**: «без greedy» на GPT-6.1 Sol Max, Kimi K3 Max
и Opus 5.5 Max, greedy на любой (executor-side не зависит от модели агента).

| Пара | Прогон | Модель | Токены (IDE usage) | Wall s | Tool-вызовов | Верный ответ? |
|------|--------|--------|--------------------|--------|--------------|---------------|
| A | без greedy | GPT-6.1 Sol Max | | | | |
| A | без greedy | Kimi K3 Max | | | | |
| A | без greedy | Opus 5.5 Max | | | | |
| A | greedy | любая | | | | |
| B | без greedy | GPT-6.1 Sol Max | | | | |
| B | без greedy | Kimi K3 Max | | | | |
| B | без greedy | Opus 5.5 Max | | | | |
| B | greedy | любая | | | | |
| … | | | | | | |

Токены «с greedy»-строк: agent-side из IDE usage + executor-side из
`usage.jsonl` (ollama eval / rag chunk — почти бесплатно, но записывать).

## Экономия налету

Разница в токенах на пару — одинакова для всех моделей (контекст ~тот же),
разница в **деньгах** — через ставку $/1M tok:

```
saved_$ (модель) = (tok_без_greedy − tok_greedy) × rate_$ / 1_000_000
```

Ставки подставляются в canvas-калькуляторе (поля ввода над таблицей) —
результат пересчитывается сразу. Реальные цены из IDE model picker
(2026-10-01, за 1M токенов: input / cached / output):

| Модель | input | cached | output |
|--------|-------|--------|--------|
| GPT-6.1 Sol Max | $2 | $0.1 | $10 |
| Kimi K3 Max | $3 | $0.3 | $15 |
| Opus 5.5 Max | $4 | $0.2 | $20 |

Saved-токены — это непрочитанный контекст → считаются по input-ставке
(output в замере <5%, игнорируется).


## Оговорки

- Свежие чаты: минимум системный промпт; real overhead включает IDE context
  (правила, файл-контекст) — это и есть честный «дорогой» путь.
- Не сравнивать пару с разными моделями.
- greedy-строки воркшопа логируются в usage.jsonl — после прогонов
  `greedy-token usage` покажет их отдельной волной.
