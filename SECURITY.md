# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | ✅ Active          |

## Reporting a Vulnerability

Если вы обнаружили проблему безопасности в любом скилле или в репозитории в целом:

1. **Не создавайте публичный Issue** для уязвимостей.
2. Напишите на **security@best.local** (или используйте GitHub Security Advisories: Settings → Security → Advisories → Report a vulnerability).
3. Опишите:
   - Какой скилл/файл затронут
   - Тип уязвимости (RCE, injection, path traversal, secrets leak, etc.)
   - Шаги воспроизведения (PoC)
   - Возможное влияние

Мы ответим в течение 72 часов и координируем исправление. После релиза фикса — публикуем Advisory.

## Scope

Политика охватывает:
- Все скиллы в `skills/*` (SKILL.md, skill.json, скрипты, шаблоны)
- Репозиторий в целом (CI, workflows, документация)
- Зависимости скиллов (requirements в skill.json)

## Out of Scope

- Уязвимости в самих AI-агентах (opencode, Sisyphus) — репортите их владельцам
- Социально-инженерные атаки на аккаунты пользователей
- Проблемы в сторонних API, которые используют скиллы (GitHub, Reddit, picsum.dev, etc.)

## Best Practices для авторов скиллов

- Не хардкодьте секреты/токены в SKILL.md или скриптах — используйте переменные окружения
- Валидируйте все внешние входы (пути, URL, пользовательский ввод)
- Используйте `subprocess` с `shell=False` и списком аргументов
- Ограничивайте права доступа (permissions в skill.json) минимально необходимыми
- Проверяйте integrity checksum при скачивании внешних ресурсов