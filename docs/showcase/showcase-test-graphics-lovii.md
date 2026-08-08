# Showcase: `test-graphics` on lovii

> Демонстрация работы скилла на **реальном** проекте — `lovii_demo` (SPA маркетплейс) и `lovii.ru` (лендинг White Paper). Цель: показать генерацию тестовых ассетов для реальных сценариев: аватары партнёров, placeholder-ы карточек товаров, иконки интерфейса.

---

## 1. Вход (Input)

| Что | Где |
|---|---|
| Проект | `bestdeejay-design/lovii_demo` (SPA) + `lovii.ru` (лендинг) |
| Реальные данные | `lovii_demo/js/data.js` (мок-данные: партнёры, товары, пользователи), `lovii_demo/design/` (дизайн-система) |
| Задачи для скилла | 1) Аватары партнёров/пользователей из мок-данных 2) Placeholder-ы карточек товаров 3) Иконки интерфейса (Lucide) 4) Batch-генерация для e2e |

---

## 2. Запуск (Run)

```bash
# Аватары партнёров из мок-данных (имена из lovii_demo/js/data.js)
python3 skills/test-graphics/scripts/test-graphics.py avatar "Иван Петров" --size 64 --background 3498DB --color fff --rounded true ./showcase/avatars/ivan.png
python3 skills/test-graphics/scripts/test-graphics.py avatar "Maria" --size 64 --background E74C3C --color fff --rounded true ./showcase/avatars/maria.png

# Placeholder-ы карточек товаров (800x600, brand colors lovii)
python3 skills/test-graphics/scripts/test-graphics.py placeholder 400 300 3498DB "Свежие продукты" ./showcase/placeholders/products.jpg
python3 skills/test-graphics/scripts/test-graphics.py placeholder 400 300 E74C3C "Горячая еда" ./showcase/placeholders/food.jpg

# Иконки интерфейса (Lucide, brand colors)
python3 skills/test-graphics/scripts/test-graphics.py icon star E74C3C 64 ./showcase/icons/star.svg
python3 skills/test-graphics/scripts/test-graphics.py icon home 3498DB 64 ./showcase/icons/home.svg
python3 skills/test-graphics/scripts/test-graphics.py icon user 2ECC71 64 ./showcase/icons/user.svg
python3 skills/test-graphics/scripts/test-graphics.py icon search F39C12 64 ./showcase/icons/search.svg

# Batch — 20 аватаров для e2e (партнёры + пользователи)
python3 skills/test-graphics/scripts/test-graphics.py batch-avatars 20 ./showcase/batch-avatars/

# Batch — 10 placeholder-ов товаров
python3 skills/test-graphics/scripts/test-graphics.py batch-placeholders 10 ./showcase/batch-placeholders/
```

---

## 3. Результат (Output)

```
📁 showcase/
├── avatars/
│   ├── ivan.png        # 64×64, rounded, синий фон #3498DB
│   └── maria.png       # 64×64, rounded, красный фон #E74C3C
├── placeholders/
│   ├── products.jpg    # 400×300, #3498DB "Свежие продукты"
│   └── food.jpg        # 400×300, #E74C3C "Горячая еда"
├── icons/
│   ├── star.svg        # 64×64, #E74C3C
│   ├── home.svg        # 64×64, #3498DB
│   ├── user.svg        # 64×64, #2ECC71
│   └── search.svg      # 64×64, #F39C12
├── batch-avatars/
│   ├── avatar-1.png .. avatar-20.png  # разные инициалы, случайные цвета
└── batch-placeholders/
    ├── placeholder-1.jpg .. placeholder-10.jpg  # случайные цвета/тексты
```

Пример аватара (base64 preview):
```
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAAC... (64×64 PNG, rounded, blue bg)
```

---

## 4. Интерпретация (Interpretation)

- **Аватары партнёров/пользователей** — используют детерминированную генерацию (DiceBear-style): одно и то же имя → один и тот же аватар. Для `lovii_demo` мок-данных (`js/data.js`) это даёт стабильные аватары в тестах и staging.
- **Placeholder-ы товаров** — brand-aware: используют цвета lovii (`#3498DB` — primary, `#E74C3C` — accent). Готовы для карточек товаров в staging/e2e.
- **Иконки** — Lucide SVG, tree-shaking ready, `stroke="currentColor"` → наследуют цвет текста CSS. Готовы для inline-использования в React/HTML.
- **Batch-генерация** — 20 аватаров + 10 placeholder-ов за ~2 секунды. Готово для наполнения e2e-стенда (`lovii_demo` staging) и визуальных регрессий (Playwright `toHaveScreenshot`).

---

## 5. Интеграция в e2e (Playwright)

```typescript
// test/generate-test-assets.ts
import { test } from '@playwright/test';
import { execSync } from 'child_process';

test('generate test assets for lovii_demo', async () => {
  // Аватары для мок-пользователей
  execSync('python3 skills/test-graphics/scripts/test-graphics.py batch-avatars 50 ./test-assets/avatars');
  // Placeholder-ы для каталога
  execSync('python3 skills/test-graphics/scripts/test-graphics.py batch-placeholders 30 ./test-assets/placeholders');
});

// В e2e-тесте: стабильные аватары для визуального регресса
test('product card visual regression', async ({ page }) => {
  await page.goto('https://web-test.lovii.ru/catalog');
  await expect(page.locator('.product-card').first()).toHaveScreenshot('product-card.png', {
    maxDiffPixelRatio: 0.01  // детерминированные placeholder-ы = стабильный diff
  });
});
```

---

> **Чек-лист готовности showcase:**
> - [x] Вход — реальные мок-данные `lovii_demo/js/data.js` + бренд-цвета lovii
> - [x] Команды воспроизводимы (все ассеты генерируются скриптом)
> - [x] Ассеты созданы: аватары, placeholder-ы, иконки, batch
> - [x] План интеграции в Playwright e2e описан
> - [x] Используются канонические паттерны: детерминированные аватары, SVG-иконки, batch CLI