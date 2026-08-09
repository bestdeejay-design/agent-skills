# Showcase: security-review on a real project

> Демонстрация работы скилла на **реальном** проекте (не абстрактном `foo.txt`).
> Эталонный проект: **lovii.ru** — https://github.com/bestdeejay-design/lovii_demo

## 1. Вход (Input)

| Что | Где |
|---|---|
| Проект (репозиторий) | `https://github.com/bestdeejay-design/lovii_demo` |
| Файлы, к которым применяется скилл | `package-lock.json` (`.opencode/`) |
| Задача для скилла | Инвентаризация lockfile'ов зависимостей + классификация exit-кодов security-инструментов перед аудитом |

*Почему именно эти данные:* у lovii_demo есть реальный npm-lockfile для
вспомогательного инструментария (`.opencode/`), что типично для проектов с
CI-зависимостями. Скилл должен найти его, определить экосистему и подсказать
правильный сканер, а также правильно интерпретировать коды возврата сканеров
(findings vs. инфраструктурная ошибка).

## 2. Запуск (Run)

```bash
python3 skills/security-review/scripts/security_review.py inventory --dir /Users/best/Projects/lovii_demo
python3 skills/security-review/scripts/security_review.py inventory --dir /Users/best/Projects/lovii_demo --json
python3 skills/security-review/scripts/security_review.py classify --tool osv-scanner --exit-code 129
python3 skills/security-review/scripts/security_review.py classify --tool semgrep --exit-code 1
```

## 3. Вывод (Output)

```text
ecosystem  tool       lockfile
npm        npm audit  .opencode/package-lock.json
```

```json
[
  {
    "path": ".opencode/package-lock.json",
    "name": "package-lock.json",
    "ecosystem": "npm",
    "tool": "npm audit"
  }
]
```

```text
osv-scanner exit 129 → error (not a scan report)
semgrep exit 1 → findings (expected report)
```

## 4. Интерпретация (Interpretation)

- В lovii_demo единственный npm-lockfile находится в `.opencode/` — это
  зависимости вспомогательного инструмента; для него канонический аудит —
  `npm audit` или `osv-scanner`.
- `osv-scanner` exit `129` означает **ошибку API/инфраструктуры**, а не
  отсутствие уязвимостей; наш классификатор не даёт воспринять это как «чисто».
- `semgrep` exit `1` — реальные находки (expected report), это нормальный
  сигнал для CI-gate: findings → fail, exit 0 → clean.
- Владельцу проекта: добавить `.opencode/package-lock.json` в периодический
  SCA-скан (npm audit / osv-scanner) — это единственная точка dependency-риска.
- Ограничение: security-review **не сканирует сам** — он оркестрирует и
  нормализует внешние сканеры (semgrep/osv-scanner/pip-audit и т.д.), которые
  должны быть установлены отдельно.

---

> Чек-лист перед принятием showcase:
> - [x] входные пути ведут в реальный репозиторий (не абстрактные примеры);
> - [x] команда запуска воспроизводима (`bash -c` командой из шага 2);
> - [x] вывод в шаге 3 — реальный (не придуманный).
