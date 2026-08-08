# Plan: Создать скилл changelog-generator

> Дата: 2026-08-08
> Статус: `approved`

## Goal
Новый скилл `skills/changelog-generator/` генерирует Keep a Changelog-раздел из
git-истории (Conventional Commits) с рабочим скриптом на Python 3 stdlib.

**Acceptance criteria (проверяемо):**
- [x] CR1: `scripts/changelog_gen.py --repo . --from-tag v1.0.0` выдаёт Markdown с секциями Added/Fixed/Changed
- [x] CR2: маппинг типов feat→Added, fix→Fixed, perf→Changed, breaking→отдельная секция
- [x] CR3: скилл проходит `validate_skills.py` (skill.json + SKILL.md + files)

## Constraints
- Только Python 3 stdlib (subprocess для git)
- Не трогать существующие скиллы
- Формат skill.json — по образцу code-review (required fields валидатора)

## Steps

### Step 1: скрипт-парсер git-лога
- Files: `skills/changelog-generator/scripts/changelog_gen.py`
- Produces: `parse_commits(tag_a, tag_b) -> list[Commit]` (hash, author, date, type, desc, breaking)
- Consumes: `git log --format=%H%x00%an%x00%aI%x00%s%x00%b%x1e tag..HEAD`
- Action: распарсить NUL-разделённые поля, классифицировать тип по Conventional Commits
- Verification: `python3 scripts/changelog_gen.py --repo skills-repo --from-tag <существующий>` → вывод секций
- [x] done

### Step 2: маппинг типов и рендер
- Files: `skills/changelog-generator/scripts/changelog_gen.py`
- Produces: `render_changelog(commits, version, date) -> str`
- Consumes: список Commit из Step 1
- Action: маппинг feat→Added, fix→Fixed, perf→Changed, breaking(!/BREAKING CHANGE)→Breaking; остальные скрыты
- Verification: в выводе присутствуют секции Added/Fixed/Changed; breaking-коммит в отдельной секции
- [x] done

### Step 3: манифесты скилла
- Files: `skills/changelog-generator/SKILL.md`, `skills/changelog-generator/skill.json`
- Action: SKILL.md по формату code-review (frontmatter, When to use, Workflow), skill.json со всеми required fields
- Verification: `python3 .github/workflows/validate_skills.py` → скилл в списке ✅
- [x] done

## Interfaces
- Consumes → Produces:
  - `Step1.parser` → `Step2.renderer`
  - `Step2.changelog_md` → `Step3.skill_description`

## Verification (полная)
- [x] `python3 skills/plan-skill/scripts/plan_validator.py <этот файл>` → ✅
- [x] Скрипт отработал на реальном git-логе репозитория
- [x] Локальный валидатор скиллов 14/14 ✅
- [x] Ревью: замечаний нет