# Debug: Menu & Navigation

Самый частый источник мобильных багов. Проигрыш симптом → причина → фикс.

## 1. Меню не открывается / не закрывается по тапу

**Симптом:** тап по гамбургеру ничего не делает или меню «залипает».
**Причины и фиксы:**
- Обработчик навешен на невидимый элемент (оверлей перекрывает кнопку). Проверьте,
  что `z-index` кнопки выше оверлея, а оверлей `pointer-events:none` когда скрыт.
- `aria-expanded` есть, но класс видимости не переключается. Держите одну функцию
  `setMenu(open)`, которая атомарно меняет и класс, и `aria-expanded`, и `inert` на фоне.
- Кнопка < 44px и «не попадает» под палец — увеличьте tap-target.

```js
function setMenu(open){
  menu.classList.toggle('is-open', open);
  btn.setAttribute('aria-expanded', String(open));
  document.body.classList.toggle('menu-open', open);
  backdrop.toggleAttribute('inert', !open);
}
btn.addEventListener('click', () => setMenu(!menu.classList.contains('is-open')));
```

## 2. Меню не закрывается при выборе пункта

**Причина:** ссылки внутри не вызывают `setMenu(false)`.
**Фикс:** делегируйте клик по пунктам:

```js
menu.addEventListener('click', (e) => {
  if (e.target.closest('a')) setMenu(false);
});
```

## 3. Фокус уходит из меню / ловушка не работает

**Симптом:** при `Tab` фокус проваливается на фон (за меню) или теряется.
**Фикс — фокус-ловушка в открытом меню:**

```js
const focusable = () => menu.querySelectorAll('a[href],button:not([disabled])');
menu.addEventListener('keydown', (e) => {
  if (e.key !== 'Tab') return;
  const f = [...focusable()]; if (!f.length) return;
  const first = f[0], last = f[f.length-1];
  if (e.shiftKey && document.activeElement === first){ e.preventDefault(); last.focus(); }
  else if (!e.shiftKey && document.activeElement === last){ e.preventDefault(); first.focus(); }
});
```

## 4. Esc не закрывает

```js
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && menu.classList.contains('is-open')) setMenu(false); });
```

## 5. Якоря упираются в фиксированную шапку

**Симптом:** переход по `#section` прячет заголовок секции под sticky-хедером.
**Фикс:** `scroll-margin-top` (см. tokens.md) + не забыть `scroll-behavior: smooth`.
Для SPA-роутера — компенсировать скролл вручную: `window.scrollTo(0, y - headerH - 16)`.

## 6. z-index стекинг: меню под контентом или над модалкой

**Правило слоёв:**
```
фон контента        10
sticky шапка        100
оверлей меню        200
панель меню         210
модалка/тост        1000+
```
Не используйте `9999` «на всякий случай» — это ломает модалки.

## 7. Меню скрыто за home-indicator (safe-area)

**Симптом:** нижние пункты меню упираются в индикатор на iPhone.
**Фикс:** `padding-bottom: calc(var(--space-3) + env(safe-area-inset-bottom))` на меню/таббаре.

## 8. Анимация меню вызывает «прыжок» CLS

**Причина:** меню в потоке (push-content) меняет высоту при открытии.
**Фикс:** меню позиционируйте `position: fixed` (оверлей), не сдвигайте контент.
Или анимируйте `transform`, а не `height`/`margin`.

## 9. Трансформ ломает `position: fixed` внутри меню

**Симптом:** дочерний `fixed` элемент позиционируется относительно меню, а не вьюпорта.
**Причина:** предок с `transform`/`filter`/`will-change` создаёт containing block.
**Фикс:** уберите `transform` с предка меню или вынесите fixed-элемент наружу.

## Быстрая проверка (Playwright)

```js
// открыто ли меню по aria-expanded
const expanded = await page.getAttribute('#menuBtn', 'aria-expanded');
// клик по пункту закрывает
await page.click('#menu a[href="#about"]');
const stillOpen = await page.getAttribute('#menuBtn', 'aria-expanded');
// должно стать "false"
```
