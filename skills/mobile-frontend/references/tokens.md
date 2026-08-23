# Мобильные токены (Mobile Foundations)

Единый источник правды по числам для мобильной вёрстки. Все значения — CSS-переменные
в `:root`. Вне токенов допустимы только `transparent` и `currentColor`.

## Spacing (4/8-сетка, pt → px: 1pt ≈ 1.333px)

```css
:root{
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;   /* базовый отступ секции */
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 40px;   /* крупные секции / 40pt-зона */
  --space-8: 48px;

  --content-px: 20px;        /* боковые поля контента на телефоне */
  --content-max: 720px;      /* верхняя граница контейнера (планшет) */
  --header-h: 56px;          /* высота sticky-шапки */
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 22px;
}
```

## Type scale (clamp = мобильный→десктоп)

```css
:root{
  --fs-body: 16px;            /* НЕ меньше 16px — иначе iOS зумит при фокусе input */
  --fs-small: 14px;
  --fs-h1: clamp(28px, 8vw, 44px);
  --fs-h2: clamp(22px, 6vw, 32px);
  --fs-h3: clamp(18px, 4.5vw, 24px);
  --lh-body: 1.5;
  --lh-tight: 1.2;
}
body{ font-size: var(--fs-body); line-height: var(--lh-body); }
h1{ font-size: var(--fs-h1); line-height: var(--lh-tight); }
```

## Breakpoints (mobile-first: min-width)

```css
--bp-sm: 480px;   /* крупные телефоны / ландшафт */
--bp-md: 768px;   /* планшет */
--bp-lg: 1024px;  /* десктоп */
```
Базовые стили = мобильные. Расширения только через `@media (min-width: ...)`.

## Якоря под фиксированной шапкой

```css
:root{ --header-h: 56px; }
html{ scroll-behavior: smooth; }
section[id], [id]{ scroll-margin-top: calc(var(--header-h) + 16px); }
```
Проверка: `element.getBoundingClientRect().top >= headerBottom - 1` после скролла.

## Safe-area (чёлка / home indicator)

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```
```css
:root{
  --sat: env(safe-area-inset-top);
  --sar: env(safe-area-inset-right);
  --sab: env(safe-area-inset-bottom);
  --sal: env(safe-area-inset-left);
}
.header{ padding-top: calc(var(--space-4) + var(--sat)); }
.tabbar{ padding-bottom: calc(var(--space-3) + var(--sab)); }
```

## Tap-target

```css
/* любая интерактивная цель — минимум 44×44 */
a, button{ min-height: 44px; min-width: 44px; }
.icon-btn{ width: 44px; height: 44px; display: inline-flex; align-items: center; justify-content: center; }
```

## Motion

```css
@media (prefers-reduced-motion: reduce){
  *{ animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; scroll-behavior: auto !important; }
}
```

## Цвета (пример, замените под бренд)

```css
:root{
  --bg: #0F172A;
  --surface: #1E293B;
  --text: #F8FAFC;
  --text-muted: #94A3B8;
  --primary: #2563EB;
  --primary-contrast: #FFFFFF;
  --border: rgba(255,255,255,0.10);
}
/* контраст: --text на --bg ≥ 4.5:1; --primary-contrast на --primary ≥ 4.5:1 */
```
