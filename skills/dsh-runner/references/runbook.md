# dsh-runner runbook

> Чек-листы и типовые ошибки при работе с DeepSeek Harness (`dsh`).
> Источник истины по API — репозиторий deepseek-ai/deepseek-harness (README,
> docs/architecture.md, docs/user/guide/python-sdk.md). Проект в developer
> preview — при конфликте с реальным поведением доверяй свежему README.

## Перед запуском (чек-лист)

- [ ] `pip show deepseek-harness-sdk` — SDK установлен (Python 3.10+)
- [ ] `DEEPSEEK_API_KEY` задан — **или** ключ DeepSeek доступен в auth.json
      opencode (`~/.local/share/opencode/auth.json` / `~/.config/opencode/auth.json`,
      провайдер `deepseek`) — `dsh_task.py` подхватит его автоматически;
      **или** задан `DEEPSEEK_BASE_URL` (OpenAI-совместимый endpoint)
- [ ] workspace — **одноразовая папка** (клон/чек-аут), НЕ рабочее дерево
      с незакоммиченными изменениями
- [ ] `--session-id` уникален для каждой задачи (иначе лог перезапишется)
- [ ] Для сравнения моделей — одинаковый workspace, разные session-id

## После прогона (проверка результата)

- [ ] exit code 0 + непустой `final_response`
- [ ] `find <session-root> -name "session.jsonl.zstd"` — лог на месте (zstd-сжатый
      JSONL в `<session-root>/<sanitized-cwd>/<session-id>/`); размер — метрика токенов
- [ ] Декод лога для аудита: `zstd -d -c <файл> | jq -s .` (типы записей:
      `tool/call`, `tool/result`, `assistant/message`, `turn/end`)
- [ ] Если в workspace есть тесты: прогони их, сравни «до/после»
- [ ] Если это git-клон: `git diff` и просмотри патч глазами
- [ ] Сравнение моделей: размер JSONL (≈токены), время, качество финального ответа

## Типовые ошибки

| Ошибка | Причина | Решение |
|---|---|---|
| `pip install` падает на платформе | SDK-раннер поставляется бинарником под macOS 14+ arm64 / Linux x64,arm64 | Проверь версию ОС/архитектуру; на других платформах собери из исходников |
| `DEEPSEEK_API_KEY` not set | ключ не экспортирован | `export DEEPSEEK_API_KEY=sk-...` — или просто используй ключ из auth.json opencode (см. чек-лист выше); если и там нет — `opencode auth login` |
| Модель не найдена | неверный id модели | проверь доступные модели провайдера; по умолчанию `deepseek-v4-flash` |
| Сломанный API после обновления | developer preview, breaking changes | `pip install -U deepseek-harness-sdk`, сверь с README |
| Агент «вышел за пределы» workspace | композиция `danger-full-access` | Запускай в контейнере/изолированной VM; используй sandbox-профили (landlock/e2b) если доступны |
| Лог пустой/маленький | задача тривиальная или агент завершился сразу | Проверь `finish_reason`; увеличь `--max-tokens` |
| `session.jsonl.zstd` вместо `*.jsonl` | SDK хранит лог сжатым, путь зависит от workspace | Ищи через `find <session-root> -name "session.jsonl.zstd"` |

## Сравнение с другими инструментами (не путать)

- **lm-evaluation-harness (EleutherAI)** — статическая оценка качества генерации
  на бенчмарках (MMLU, GSM8K…). dsh — НЕ это.
- **SWE-bench harness** — готовый бенчмарк+раннер в Docker. dsh — движок,
  бенчмарки подключаются снаружи (датасет → workspace → задача → своя проверка).
- **OpenHands** — агентная платформа. dsh отличается Cordis-архитектурой
  («всё — плагин»), Landlock/e2b песочницами и JSON-RPC SDK.

## Полезные ссылки

- Репозиторий: https://github.com/deepseek-ai/deepseek-harness
- Архитектура: docs/architecture.md (в репо)
- Python SDK guide: docs/user/guide/python-sdk.md (в репо)
- Web UI guide: docs/user/guide/index.md (в репо)
- Сообщество: GitHub Discussions + Discord (ссылка в README репо)