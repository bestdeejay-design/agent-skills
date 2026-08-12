# Определение контекста: PROJECT_NAME / PROJECT_DESC / COLD / WARM / FONTCOLOR

> Вынесено из SKILL.md. Здесь — все автоматически определяемые значения
> генерации header/footer: приоритеты, таблицы автогенерации, правила
> градиента.

## Определение владельца (USERNAME)

- `USERNAME` = сегмент после `github.com/` в URL репозитория.
- Пример: `github.com/bestdeejay-design/repo` → `USERNAME = "bestdeejay-design"`.
- Если владелец неочевиден — подтвердить у пользователя до генерации.

## Определение названия проекта (PROJECT_NAME)

Приоритет (от высокого к низкому):
1. Поле `name` в `package.json`
2. Поле `name` в `pyproject.toml` / `setup.py` / `Cargo.toml`
3. Поле `name` в `composer.json` / `pubspec.yaml`
4. Название репозитория (без префикса владельца)
5. Заголовок первого `#` в существующем README

## Определение описания (PROJECT_DESC)

Приоритет:
1. Поле `description` в `package.json` / `pyproject.toml`
2. Поле `description` репозитория на GitHub
3. Анализ технологий → автогенерация (см. таблицу ниже)
4. По типу репозитория (см. таблицу)
5. Fallback: `Open Source Project`

### Таблица автогенерации desc

| Технология/Тип | desc |
|---|---|
| React/Vue/Svelte/Next.js | `Frontend Developer` |
| Node.js/Express/Fastify | `Backend Engineer` |
| Python/Django/Flask | `Backend Developer` |
| TypeScript | `Type-Safe Code` |
| Rust | `Systems Programming` |
| Go | `Backend Tool` |
| Telegram/Discord/Slack bot | `Automation Tool` |
| CLI/terminal | `Developer Utility` |
| Mobile (React Native/Flutter/Swift) | `Mobile App` |
| UI library/design system | `UI Components` |
| Portfolio | `Creative Developer` |
| Documentation | `Knowledge Base` |
| API | `API Service` |
| Database/ORM | `Data Layer` |
| AI/ML/PyTorch/TensorFlow | `AI / Machine Learning` |
| DevOps/Docker/K8s | `DevOps Tool` |
| Game/Unity/Godot | `Game Development` |
| Chrome/Firefox extension | `Browser Extension` |
| VS Code extension | `IDE Plugin` |
| Web App (без конкретного стека) | `Web Application` |
| Library (общее) | `Developer Library` |

## Определение цветовой схемы (COLD + WARM)

Приоритет:
1. Явно указанные цвета проекта (брендинг, design tokens, бейджи README, `og-image`)
2. Цвета из настроек VSCode / темы (если присутствуют в репо)
3. AI подбирает по тематике (см. таблицу)
4. Fallback: `#0ABAB5` + `#F64A8A`

### Таблица подбора цветов

| Тематика | Цвет 1 | Цвет 2 |
|---|---|---|
| Дизайн / UI / Frontend | `#0ABAB5` | `#F64A8A` |
| Backend / API / Инфра | `#1E3A8A` | `#F59E0B` |
| AI / ML / Data | `#7C3AED` | `#06B6D4` |
| DevOps / Cloud | `#0EA5E9` | `#10B981` |
| Mobile | `#8B5CF6` | `#EC4899` |
| Боты / Automation | `#9B4DCA` | `#00D4FF` |
| Игры | `#DC2626` | `#7C3AED` |
| Финансы / Крипто | `#1E293B` | `#FBBF24` |
| Безопасность | `#18181B` | `#EF4444` |
| Образование | `#2563EB` | `#F97316` |
| Open source общее | `#6366F1` | `#EC4899` |
| Fallback | `#0ABAB5` | `#F64A8A` |

Из таблицы: **Цвет 1 → COLD**, **Цвет 2 → WARM** (или наоборот — AI выбирает
направление так, чтобы градиент был контрастным; оба варианта допустимы, главное —
единообразие в рамках проекта).

## Правила для градиента

- **HEADER**: слева `COLD` → справа `WARM`.
- **FOOTER**: слева `WARM` → справа `COLD` (**инверсия header**).
- Запрещено использовать белый (`#FFFFFF`) в середине градиента — сольётся с текстом.
- `FONTCOLOR`: `#FFFFFF` (или `#1A1A2E`, если градиент светлый).

## Алгоритм работы AI

1. Определи `USERNAME` из URL репозитория (подтвердить, если неочевиден).
2. Определи `PROJECT_NAME` по приоритетам выше.
3. Определи `PROJECT_DESC` по приоритетам / таблице.
4. Определи `COLD` и `WARM` по приоритетам / таблице цветов.
5. Определи `FONTCOLOR` (`#FFFFFF` по умолчанию).
6. Создай `assets/` (если нет) и сгенерируй `assets/header.svg` по шаблону
   (`references/svg-animation.md` или `scripts/generate_assets.py`).
7. Сгенерируй `assets/footer.svg` по шаблону.
8. Добавь ссылки в начало и конец README.md (и в `README.<lang>.md`, если есть).
9. Если `assets/header.svg` / `assets/footer.svg` уже существуют — спросить:
   перезаписать?

> Совет: для детерминированной генерации используй
> `python3 scripts/generate_assets.py --cold ... --warm ... --name ... --desc ... --user ...`
> вместо ручной подстановки в шаблон, затем прогони
> `python3 scripts/validate_svg.py assets/`.