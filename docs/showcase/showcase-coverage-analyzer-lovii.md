# Showcase: `coverage-analyzer` на реальном coverage.xml

> Демонстрация работы скилла на **реальном** отчёте покрытия — не на
> рукописном примере. Вход — настоящий `coverage.xml`, сгенерированный
> `coverage.py` 7.15.4 по реальному скрипту репозитория
> `agent-skills/.github/workflows/validate_skills.py`.

## 1. Вход (Input)

| Что | Где |
|---|---|
| Проект (репозиторий) | `/Users/best/Projects/test/skills-repo` (agent-skills) |
| Файл, по которому измеряем покрытие | `.github/workflows/validate_skills.py` (CI-валидатор манифестов скиллов, 83 строки) |
| Вход для скилла | реальный `coverage.xml` (coverage.py 7.15.4, `coverage run` + `coverage xml`) |
| Задача для скилла | Разобрать XML в читаемый анализ: total line-rate, worst-10, delta vs baseline, verdict по порогу |

*Почему именно эти данные:* `validate_skills.py` — реальный исполняемый
Python-скрипт репозитория с ветвлениями (`fail()`, `load_json()`, циклы по
скиллам), т.е. типичная цель для измерения покрытия. `coverage.py` на этой
машине не установлен глобально, поэтому XML получен через временный venv
(`/tmp/covvw`, `pip install coverage`) — сам XML при этом настоящий, от
coverage.py 7.15.4.

## 2. Запуск (Run)

```bash
# 1. Генерация реального coverage.xml (временный venv, т.к. coverage.py не установлен глобально):
python3 -m venv /tmp/covvw && /tmp/covvw/bin/pip install coverage
cd /Users/best/Projects/test/skills-repo
/tmp/covvw/bin/python -m coverage run --source .github/workflows .github/workflows/validate_skills.py
/tmp/covvw/bin/python -m coverage xml -o /tmp/coverage.xml

# 2. Анализ (из репозитория agent-skills):
python3 skills/coverage-analyzer/scripts/coverage_analyzer.py --xml /tmp/coverage.xml --threshold 80
```

## 3. Вывод (Output)

Реальный вывод (запуск 2026-08-09, coverage.py 7.15.4):

```text
# Coverage analysis: /tmp/coverage.xml

## Total
- line-rate: 0.7805 (78.0%)
- files: 1
- files_with_zero_lines: 0

## Worst 10 files (lowest line-rate)
| # | file | line-rate |
|---|------|-----------|
| 1 | validate_skills.py | 0.7805 (78.0%) |

## Verdict
FAIL — total 78.0% < threshold 80%
```

Тот же прогон с сохранением baseline и повторным сравнением:

```bash
$ python3 skills/coverage-analyzer/scripts/coverage_analyzer.py --xml /tmp/coverage.xml --save-baseline /tmp/baseline.json
baseline saved to /tmp/baseline.json (total 0.7805)

$ python3 skills/coverage-analyzer/scripts/coverage_analyzer.py --xml /tmp/coverage.xml --baseline /tmp/baseline.json --threshold 80
# Coverage analysis: /tmp/coverage.xml

## Total
- line-rate: 0.7805 (78.0%)
- files: 1
- files_with_zero_lines: 0

## Worst 10 files (lowest line-rate)
| # | file | line-rate |
|---|------|-----------|
| 1 | validate_skills.py | 0.7805 (78.0%) |

## Delta vs baseline
| file | before | after | Δ |
|------|--------|-------|---|
| validate_skills.py | 78.0% | 78.0% | +0.0 pp |
| **total** | 78.0% | 78.0% | +0.0 pp |

## Verdict
FAIL — total 78.0% < threshold 80%
```

`echo $?` после прогона с порогом → `1` (FAIL — CI-гейт сработал).

## 4. Интерпретация (Interpretation)

- **Что означает результат**: `validate_skills.py` покрыт на **78.0%**
  (32 из 41 исполняемой строки). Непокрытые строки — это ветки ошибок:
  `fail()` (строки 34–35), `load_json` при `JSONDecodeError` (42–43),
  `missing fields` (51), `folder missing` (63), `manifest missing` (66),
  `SKILL.md missing` (70), `not listed` (72) — т.е. все пути, которые в
  happy-path прогоне не срабатывают. `files_with_zero_lines: 0` — файлов с
  нулевым покрытием нет (в отчёте один файл).
- **Branch-rate отсутствует** — coverage.py запущен без `--branch`
  (`branches-valid="0"`), поэтому скилл честно не показывает строку
  branch-rate (0% с 0 валидных веток — это «не измерено», а не «0%»).
- **Полезно владельцу репозитория**: порог 80% не пройден (78.0% < 80%,
  exit 1). Чтобы закрыть гейт, достаточно добавить тест на негативные ветки
  `validate_skills.py` (битый JSON, отсутствующий `skill.json`, отсутствующий
  `SKILL.md`) — это поднимет покрытие выше 80%. Baseline-файл можно
  закоммитить и отслеживать регрессии по таблице `before → after → Δ`.
- **Ограничение**: скилл анализирует один локальный `coverage.xml`; он не
  запускает тесты и не агрегирует матрицу CI (как codecov/coveralls).
  Для этого проекта покрытие измерено только по одному скрипту — полная
  картина по репозиторию требует `coverage run -m pytest` по всему коду.

---

> Чек-лист:
> - [x] вход — реальный `coverage.xml` (coverage.py 7.15.4, не рукописный);
> - [x] команда воспроизводима (выполнена 2026-08-09);
> - [x] вывод — реальный: total 78.0%, 1 файл, FAIL при пороге 80% (exit 1).