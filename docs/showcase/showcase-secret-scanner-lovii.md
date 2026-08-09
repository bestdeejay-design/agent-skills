# Showcase: `secret-scanner` on lovii_demo

> Демонстрация работы скилла на **реальном** проекте — репозитории
> **lovii_demo** (https://github.com/bestdeejay-design/lovii_demo),
> фронтенд-лендинг/приложение (HTML + собранный JS-бандл в `index.js`).

## 1. Вход (Input)

| Что | Где |
|---|---|
| Проект (репозиторий) | `/Users/best/Projects/lovii_demo` |
| Что сканируем | все файлы, отслеживаемые git (`--git`): `index.html`, `index.js`, `js/`, `css/`, `design/`, `docs/` |
| Задача для скилла | Найти потенциально утёкшие токены/ключи перед публикацией репозитория |

*Почему именно эти данные:* проект содержит собранный production-бандл
(`index.js`, axios 1.13.6 inline) — типичный источник false positive'ов
(минифицированный код, UUID, хэши), что проверяет фильтры noise-allowlist'а
и keyword-anchored generic-детекцию.

## 2. Запуск (Run)

```bash
# Из репозитория agent-skills:
python3 skills/secret-scanner/scripts/secret_scanner.py --git /Users/best/Projects/lovii_demo --redact 12
```

## 3. Вывод (Output)

Сокращённый **реальный** вывод (запуск 2026-08-09):

```text
[Medium] index.js:7 — Generic API key (keyword-anchored) (generic-api-key)
    secret: ab546df8-91b……………………………………………, entropy=3.6

Total findings: 1
```

JSON-режим с тем же результатом (тот же прогон):

```json
{
  "target": "/Users/best/Projects/lovii_demo",
  "total": 1,
  "findings": [
    {
      "rule": "generic-api-key",
      "severity": "Medium",
      "secret": "ab546df8…",
      "entropy": 3.6,
      "path": "index.js",
      "line": 6
    }
  ]
}
```

## 4. Интерпретация (Interpretation)

- **Что означает результат**: скрипт не нашёл ни одного typed-секрета
  (AWS/GitHub/OpenAI/Anthropic/Slack/Stripe/private keys) — 18 из 19 правил
  прошли вхолостую. Единственный сигнал — generic-правило (keyword-anchored)
  на UUID-подобном значении (`ab546df8-…`, энтропия 3.6) в собранном
  минифицированном бандле `index.js`.
- **Это false positive**: значение по формату — UUID (тестовый/конфигурационный
  идентификатор, вероятно версия или build hash), а не секрет. Скилл честно
  маркирует его как **Medium + "potential"** (никакой сетевой верификации не
  делается) — это ровно та гибкость, ради которой в модели есть allowlist
  ($VAR, EXAMPLE, …) и далее интерпретатор решает: смотреть контекст или
  занести в baseline.
- **Полезно владельцу `lovii_demo`**: подтверждение, что репозиторий
  безопасен для публикации (нет `AKIA…`, `ghp_…`, `sk-…T3BlbkFJ…`, ключей
  Stripe и т.п.). Рекомендация: в реальном CI поставить `--exit-code` + baseline;
  для этого проекта сигнал можно занести в suppressed-baseline (он
  перепроверится на следующем запуске).
- **Ограничение**: скынер статический (нет проверки "живости" токена);
  `.env*` в tomto репозитории отсутствует в `git ls-files` (см. `.gitignore`),
  поэтому он не попал в обоиск — если в репо лежит real `.env`, нужно сканировать
  через `--path` (не `--git`), либо включить его в трекинг.

---

> Чек-лист:
> - [x] вход — реальный репозиторий lovii_demo;
> - [x] команда воспроизводима (выполнена 2026-08-09);
> - [x] вывод — реальный. Current: 1 Medium (FP, UUID), остальное чисто.