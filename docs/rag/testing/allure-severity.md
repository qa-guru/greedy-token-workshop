# Allure severity labels

Отчёт Allure помечает кейсы label `severity`. Допустимые значения: blocker, critical, normal, minor, trivial.

Ставить label на сценарий, а не на шаг. blocker — блокер релиза; critical — основной поток сломан; normal — типичный регресс; minor и trivial — косметика.

Не смешивать severity с flaky и owner: это разные labels. В пайплайне сортируют падения по severity, чтобы сначала смотреть blocker и critical.
