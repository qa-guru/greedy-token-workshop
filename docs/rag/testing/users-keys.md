# Проверка фикстуры users

Фикстура `lab/users.json` — массив объектов users. Обязательные ключи: `id`, `email`.

Скрипт: `python3 lab/check_users.py lab/users.json`

Коды выхода:

- `0` — схема users валидна, ключи `id` и `email` на месте
- `1` — отсутствует `id` или отсутствует `email`
- `2` — файл недоступен либо JSON сломан

Stdout — JSON (0 LLM). Так у нас принято проверять ключи `id` и `email` у users.
