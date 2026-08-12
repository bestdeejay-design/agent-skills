# Social preview (og:image) — как создать

GitHub **само** генерирует превью репозитория, но кастомное социальное превью
(картинка при шаринге ссылки на репо и в OG-тегах Pages-сайта) ставится только
через **Settings → Social preview → Edit → Upload** — публичного REST/CLI API для
заливки **нет**. Скрипт `scripts/generate_social_preview.py` лишь **создаёт файл**
картинки, который ты потом заливаешь вручную.

## Спецификация файла

- Формат: **PNG / JPG / GIF**, размер **< 1 MB**.
- Минимальное разрешение: **≥ 640×320**; рекомендовано **1280×640**.
- Расположение в репо: корень / `docs/` / default-ветка (для raw-ссылки) и/или
  в `assets/` (для встраивания в README).
- Сплошной фон рекомендуется (прозрачность поддерживается, но может
  некрасиво смотреться на тёмных карточках соцсетей).
- Для Pages-сайта укажи `og:image` в `<head>`:

  ```html
  <meta property="og:image" content="https://<user>.github.io/<repo>/og-2026-08-11.png">
  <meta name="twitter:image" content="https://<user>.github.io/<repo>/og-2026-08-11.png">
  ```

## Генерация (скрипт)

Требует Pillow (`pip install pillow`). Композиция повторяет анимированный хедер:
чёрный фон, белый заголовок + подзаголовок, цветные волны снизу, отступы.

```bash
python3 scripts/generate_social_preview.py \
  --name "SVG Header & Footer Editor" \
  --desc "FOR GITHUB README" \
  --user bestdeejay-design \
  --cold "#00E5FF" --warm "#0ABAB5" \
  --out og-2026-08-11.png
```

Аргументы: `--name`, `--desc`, `--user`, `--cold`/`--warm` (hex), `--out`,
`--pad` (внутренний отступ, по умолчанию 80). Заголовок авто-подгоняется по ширине.

> Примечание: PNG — статичен, поэтому SMIL-анимация хедера в превью не
> отобразится; это нормально для соц-карточек.

## Чек-лист

- [ ] Файл 1280×640, < 1 MB, в репо.
- [ ] `og:image` прописан в `<head>` Pages-сайта.
- [ ] Картинка **вручную** загружена в Settings → Social preview.
