---
name: dsh-runner
description: "Запуск автономных агентных задач через DeepSeek Harness (dsh) — изолированные workspace, JSONL-логи сессий, параллельные прогоны. Скрипт dsh_task.py генерирует конфиг и запускает агента через Python SDK (jsonrpc-agent): задача → workspace → harness.run(prompt) → отчёт с final_response и логом. Режимы: headless-задача одной командой, Web UI (npx @deepseek-ai/dsh web), сравнение моделей. Ключ: DEEPSEEK_API_KEY (env) или автоматически из auth.json opencode (провайдер deepseek), либо OpenAI-совместимый endpoint через DEEPSEEK_BASE_URL. Триггеры: 'dsh', 'deepseek harness', 'агент в песочнице', 'изолированный агент', 'запусти агента на репо', 'агентная задача', 'агент-исполнитель', 'harness run', 'agent harness', 'запустить dsh', 'автономная задача агентом', 'параллельные агенты', 'сравнить модели на задаче', 'jsonrpc-agent'."
license: MIT
metadata:
  author: best
  version: 1.0.0
compatibility: "Requires Python 3.10+; deepseek-harness-sdk; DEEPSEEK_API_KEY (env или auth.json opencode) или DEEPSEEK_BASE_URL; macOS 14+ arm64 / Linux x64,arm64"
when_to_use: "Use when user wants to run an autonomous agent in isolation: 'dsh', 'deepseek harness', 'агент в песочнице', 'изолированный агент', 'запусти агента на репо', 'агентная задача', 'agent harness', 'запустить dsh'. Examples: 'run an agent to fix this bug in a sandbox', 'запусти агента на репозиторий и сравни модели'."
---

# dsh-runner

> Автономный агент DeepSeek Harness (`dsh`) как внешний исполнитель задач:
> изолированная папка-workspace, полный JSONL-лог каждого шага, никакого
> доступа к файлам вне задачи.

Загружай этот скилл, когда нужно **запустить агента на реальной задаче в
отдельном окружении**: починить баг в клоне репозитория, сгенерировать код по
описанию, прогнать одну задачу на разных моделях и сравнить результат.

## 🎯 When to use

Use this skill when:
- Просят «запусти агента на репо», «почини баг автономно», «агентная задача»
- Нужен изолированный прогон: агент не должен трогать файлы вне workspace
- Нужен полный лог сессии (JSONL) для аудита каждого шага
- Нужно сравнить 2+ модели на одной задаче (по качеству и токенам)
- Нужен Web UI для интерактивной работы с агентами (`dsh web`)

Do NOT use when:
- Задача простая и решается напрямую (мелкая правка, вопрос) — прямое
  редактирование быстрее, чем подъём агента
- Нет API-ключа и нет OpenAI-совместимого endpoint — dsh без них не запустится
- Нужна классическая оценка качества модели на бенчмарках (MMLU и т.п.) —
  это lm-evaluation-harness, а не dsh
- Нужен полный контроль каждого правки с апрувами — оставайся в основном агенте

## 📦 Files

- `SKILL.md` — этот файл
- `scripts/dsh_task.py` — запуск одной агентной задачи (Python SDK, JSON-RPC)
- `references/runbook.md` — чек-листы, типовые ошибки, примеры конфигов

## 🧰 Usage

### 0. Требования (один раз)

```bash
# Python 3.10+; SDK:
pip install deepseek-harness-sdk

# API-ключ: DEEPSEEK_API_KEY в env…
export DEEPSEEK_API_KEY=sk-...

# …ИЛИ ключ DeepSeek из auth.json opencode (провайдер `deepseek`) —
# dsh_task.py подхватит его автоматически:
# ~/.local/share/opencode/auth.json → ~/.config/opencode/auth.json

# ИЛИ свой OpenAI-совместимый endpoint (vLLM и т.п.):
# export DEEPSEEK_BASE_URL=http://127.0.0.1:8000/v1

# Модель (по умолчанию deepseek-v4-flash):
# export DSH_MODEL=deepseek-v4-flash
```

### 1. Одна задача в изолированном workspace

```bash
python3 skills/dsh-runner/scripts/dsh_task.py \
  --workspace /tmp/agent-ws/dj1 \
  --session-root /tmp/agent-sessions \
  --session-id fix-001 \
  "В репозитории падает тест test_player.test.ts. Найди причину и почини."
```

Агент клонирует/принимает workspace, решает задачу, возвращает:

- `final_response` — текстовый ответ агента
- `session_root` — корень, где SDK хранит лог
- `finish_reason` — чем завершился (например, `completed`)

Лог сессии: `<session_root>/<sanitized-cwd>/<session-id>/session.jsonl.zstd`
(zstd-сжатый JSONL, где каждый запрос/вызов инструмента/ответ — отдельная
запись; декодируется `zstd -d -c <файл> | jq -s .`).

### 2. Сравнение моделей на одной задаче

```bash
# Два прогона с разными моделями, отдельные session-id:
python3 skills/dsh-runner/scripts/dsh_task.py --workspace /tmp/ws --session-id cmp-a --model deepseek-v4-flash "задача"
python3 skills/dsh-runner/scripts/dsh_task.py --workspace /tmp/ws --session-id cmp-b --model anthropic/claude-sonnet-4-5 "задача"

# Сравни: final_response + размер JSONL-лога (токены) + время прогона
```

### 3. Web UI (интерактив)

```bash
npx @deepseek-ai/dsh web   # → http://127.0.0.1:3080
```

## ⚠️ Оговорки (важно)

- **Developer preview**: версия 0.1.0-rc.x, API ломается между релизами.
  Если SDK упал на незнакомой ошибке — проверь свежую версию
  (`pip install -U deepseek-harness-sdk`) и README репозитория.
- **Безопасность**: композиция `jsonrpc-agent` по умолчанию даёт агенту
  полный доступ к workspace (`danger-full-access`). Запускай только в
  одноразовой папке/контейнере. Никогда не указывай workspace = домашнюю
  директорию или рабочее дерево с незакоммиченными изменениями.
- **Проверка результата — снаружи**: dsh не оценивает «правильно/неправильно».
  После прогона запусти тесты/линтер сам и сравни патчи.
- **Лог** — JSONL в `--session-root/<session-id>.jsonl`: каждый запрос к модели,
  вызов инструмента и ответ. Используй для аудита и метрики токенов.

## 🔬 Проверка результата

- Скрипт завершился кодом 0 → `final_response` непустой, лог существует.
- Лог: `find <session-root> -name "session.jsonl.zstd"`; размер — метрика токенов;
  декод: `zstd -d -c <файл> | jq -s .`.
- Если в workspace были тесты — прогони их после агента и сравни с состоянием «до».
- Если задача требует проверки «правильно ли починил» — собери diff
  (`git diff` в workspace, если это клон) и просмотри.

## Runbook

Чек-листы «перед запуском», «после прогона», типовые ошибки и рабочие примеры
конфигов — в [references/runbook.md](references/runbook.md).
