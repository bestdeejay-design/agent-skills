---
name: test-graphics
description: "Генерируй тестовые картинки, фото-заглушки, иконки и аватары для моков, staging и e2e-тестов. Используй, когда нужны placeholder-изображения, даже если пользователь не называет их «тестовыми». Триггеры: 'test images', 'placeholder', 'тестовые картинки', 'иконки для теста', 'заглушки', 'mock data images', 'сгенерировать фото', 'test data icons', 'заполнить картинками', 'тестовые данные изображения'."
license: MIT
metadata:
  author: best
  version: "1.0.0"
compatibility: "Requires Python 3 and Pillow"
---

# Test Graphics — Генератор тестовых изображений

Загружай этот скилл когда нужно быстро получить тестовые картинки, иконки, фото-заглушки.

## Инструмент

`scripts/test-graphics.py` — Python-скрипт в папке скилла (относительный путь от корня скилла).
Запуск: `python3 scripts/test-graphics.py ...`.
Зависимости: Python 3, Pillow, requests (есть на системе).

## Команды

### Фото (настоящие, random)

```bash
scripts/test-graphics.py photo [width] [height] [output]
```

Источник: picsum.dev (1-й приоритет), loremflickr.com (fallback), placehold.co (цветной блок), Pillow-генерация (полный fallback).

Примеры:
```bash
# Случайное фото 800x600
scripts/test-graphics.py photo

# 200x150
scripts/test-graphics.py photo 200 150

# В конкретный файл
scripts/test-graphics.py photo 1920 1080 ./assets/hero.jpg
```

### Placeholder (цветной блок с текстом)

```bash
scripts/test-graphics.py placeholder <width> <height> [color] [text] [output]
```

Примеры:
```bash
# Базовый 800x600 со случайным цветом
scripts/test-graphics.py placeholder

# 200×150 красный
scripts/test-graphics.py placeholder 200 150 "#FF0000" "My Image"

# Синий с текстом
scripts/test-graphics.py placeholder 300 200 "#3498DB" "Hello"
```

Цвета: `#RRGGBB`. Если текст содержит пробелы — в кавычки.

### Иконка (SVG, встроенные 35 штук)

```bash
scripts/test-graphics.py icon <name> [color] [size] [output]
```

Список всех иконок:
```bash
scripts/test-graphics.py list-icons
```

Примеры:
```bash
# Красная звезда 64×64
scripts/test-graphics.py icon star "#E74C3C"

# Синий дом 48×48
scripts/test-graphics.py icon home "#3498DB" 48

# В папку
scripts/test-graphics.py icon user "#2ECC71" 96 ./icons/user.svg
```

Доступные имена: star, circle, square, triangle, heart, home, user, mail,
settings, search, arrow-{right,left,up,down}, check, cross, plus, minus,
info, warning, download, upload, folder, file, image, calendar, clock,
location, tag, cart, eye, lock, phone, chart, gift.

### Аватар (ui-avatars.com)

Генерирует иконку-аватар по имени с настраиваемым фоном/цветом.

```bash
scripts/test-graphics.py avatar <name> [--param value] [output]
```

Параметры (все опциональные, `--` перед значением):

| Параметр | По умолч. | Описание |
|---|---|---|
| `--size` | 64 | Размер в px |
| `--background` | random | Цвет фона HEX (`000`, `4ECDC4`) |
| `--color` | fff | Цвет текста HEX |
| `--length` | — | Длина инициалов (1 или 2) |
| `--font-size` | — | Размер шрифта (0.5) |
| `--rounded` | false | `true` для круглого аватара |
| `--uppercase` | true | `false` для строчных |
| `--bold` | false | `true` для жирного |
| `--format` | png | `svg` для SVG |

Примеры:
```bash
# Стандартный аватар
scripts/test-graphics.py avatar "John Doe"

# Круглый красный на чёрном 128px
scripts/test-graphics.py avatar "AB" --size 128 --background 000 --color ff0000 --rounded true

# SVG формат
scripts/test-graphics.py avatar "User" --size 200 --format svg ./icons/user-avatar.svg
```

### Batch — пачка фото

```bash
scripts/test-graphics.py batch-photos <count> [output_dir]
```

Пример: `scripts/test-graphics.py batch-photos 10 ./assets/photos/`

### Batch — пачка иконок

```bash
scripts/test-graphics.py batch-icons <count> [output_dir]
```

Пример: `scripts/test-graphics.py batch-icons 20 ./assets/icons/`

Иконки будут случайных цветов и размеров (32/48/64/96px).

### Скачать иконки из Lucide

```bash
scripts/test-graphics.py download-icons <names> [output_dir]
```

Пример: `scripts/test-graphics.py download-icons "star,heart,home,user,settings" ./icons/`

Загружает настоящие SVG из репозитория Lucide (MIT license).
GitHub может rate-limit'ить — просто повтори позже для упавших.

### Скачать одну иконку из Lucide

```bash
scripts/test-graphics.py lucide <name> [output_dir]
```

Пример: `scripts/test-graphics.py lucide arrow-right ./icons/`

## Когда применять

- Нужны картинки для карточек товаров в тестовых данных
- Иконки для меню/кнопок/навигации
- Placeholder'ы для SEO-превью
- Аватарки для пользователей
- Фото для галерей/блогов в staging
- Заполнить пустые alt-атрибуты
- Графика для e2e-тестов (визуальные регрессии)

## Do not use

- Не используй для реальных продакшн-фото и контентной графики — это тестовые заглушки.
- Не используй для брендированной графики клиента (логотипы, фирменные макеты) — здесь нужен дизайнер, а не генератор заглушек.

## Если не хватает иконок

Список встроенных — `scripts/test-graphics.py list-icons` (35 штук).
Если нужно что-то конкретное — `download-icons` из Lucide (4000+ иконок, MIT).

## Если фото не загружаются

Скрипт использует 4 источника в порядке приоритета:
1. picsum.dev — настоящие фото, без ключа
2. loremflickr.com — резерв
3. placehold.co — цветной блок с размером
4. Pillow — градиент (полный fallback)

В любом случае файл будет создан.

## Варианты использования в других скиллах

При загрузке этого скилла можно вызывать скрипт напрямую через bash:
```bash
scripts/test-graphics.py photo 800 600 ./public/images/hero.jpg
```

Агент (Sisyphus) координирует: определяет что нужно (фото/иконка/placeholder),
выбирает размеры и цвета, запускает скрипт, сообщает результат.
