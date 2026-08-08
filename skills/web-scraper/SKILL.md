---
name: web-scraper
description: "Вежливый скраппинг HTML-страниц в Markdown/JSON. Скрипт scrape.py читает страницу по URL, применяет простой CSS-селектор (tag, tag#id, tag.class) для выбора строк/секций, извлекает текст, ссылки и таблицы и отдаёт результат в Markdown или JSON. Легальные guardrails встроены в код: проверка robots.txt, честный User-Agent, задержка между запросами (по умолчанию 1.0 с), лимит размера страницы 10 МБ. Триггеры: 'web scraping', 'скраппинг', 'скачать данные с сайта', 'парсинг сайта', 'парсер html', 'извлечь данные', 'scrape', 'scraping'."
license: MIT
metadata:
  author: best
  version: 1.0.0
compatibility: "Requires Python 3 stdlib; legal guardrails: robots.txt, rate limit 1.0s, page size cap 10 MB"
---

# Web Scraper

> Вежливый скраппинг HTML-страниц в Markdown/JSON на чистом Python 3 stdlib.

Загружай этот скилл когда нужно **извлечь данные с веб-страницы**: текст,
ссылки и таблицы из выбранных секций — для анализа, отчётов или датасетов.

## 🎯 When to use

Use this skill when:
- Нужно скачать данные с сайта: текст, ссылки, таблицы из выбранных блоков
- Просят «скраппинг», «парсинг сайта», «парсер html», «извлечь данные»
- Нужен быстрый дамп страницы в Markdown или JSON без установки библиотек
- Нужен вежливый сбор данных с учётом robots.txt и rate limit

Do NOT use when:
- Нужен полноценный CSS/XPath-парсер с вложенными селекторами — это `BeautifulSoup`/`lxml`
- Нужен обход JS-рендеринга (SPA) — stdlib не исполняет JavaScript
- Нужен массовый сбор тысяч страниц — согласуй с владельцем сайта и ToS
- Нужны данные из API — используй прямой HTTP-запрос к API

## 📦 Files

- `SKILL.md` — этот файл
- `scripts/scrape.py` — скрапер (Python 3 stdlib: `urllib.request`, `html.parser`)

## 🧰 Usage

```bash
# Markdown (по умолчанию), селектор по классу:
python3 skills/web-scraper/scripts/scrape.py --url https://example.com --selector "div.item"

# JSON, селектор по id:
python3 skills/web-scraper/scripts/scrape.py --url https://example.com --selector "div#list" --output json

# Все абзацы страницы:
python3 skills/web-scraper/scripts/scrape.py --url https://example.com --selector "p"

# Локальный файл (без сети, для теста):
python3 skills/web-scraper/scripts/scrape.py --url file:///tmp/test.html --selector "p"

# Увеличить задержку между запросами:
python3 skills/web-scraper/scripts/scrape.py --url https://example.com --selector "article" --delay 2.5
```

Селектор — простой `tag`, `tag#id` или `tag.class` (например `div#list`, `tr.row`).
Каждый совпавший элемент становится отдельным пунктом: текст, ссылки и таблицы.

## ⚖️ Legal guardrails

Скрипт соблюдает правила вежливого скраппинга (встроены в код):

- **robots.txt** — перед запросом читается `robots.txt` с origin-хоста; если путь
  запрещён правилом `Disallow`, скрипт пропускает страницу с сообщением и кодом 3.
- **User-Agent** — честный идентификатор
  `Mozilla/5.0 (compatible; web-scraper/1.0; +educational)`.
- **Rate limit** — задержка между запросами по умолчанию 1.0 с (`--delay`).
- **Лимит размера** — страницы больше 10 МБ отклоняются.
- **ToS** — перед массовым сбором проверь условия использования сайта и
  авторские права на данные; скрипт предназначен для образовательных целей.

## 🔬 Проверка результата

- Markdown: начинается с `# <title>`, содержит секции `## Элементы (N)` с текстом,
  ссылками и таблицами.
- JSON: валидный JSON с ключами `title`, `url`, `matched`, `items[]` (`text`, `href`).
- При ошибке сети/robots скрипт пишет причину в stderr и завершается с кодом 2
  (или 3 при запрете robots.txt), без traceback в stdout.

## Canonical analogues

Канонические аналоги, недостающие техники (Retry-After, backoff + jitter, crawl-delay, rate-limit заголовки, условные запросы) и CLI-примеры — в [references/canonical-patterns.md](references/canonical-patterns.md). Топ:

- **MCP Fetch Server** (modelcontextprotocol/servers) — эталон «URL → Markdown»: robots.txt по умолчанию, честный UA, лимит размера.
- **Scrapy** — эталон вежливости: RobotsTxtMiddleware, AutoThrottle (адаптивная задержка), ретраи на 408/429/5xx.
- **Crawlee** (Apify) — `respect_robots_txt_file=True`, ретраи с backoff, autoscaling, ротация прокси.
- **Playwright** — браузерное извлечение: locator API, `text_content()`, `page.content()`.
- **Trafilatura** — ближайший по назначению аналог: CLI HTML → Markdown/JSON.
- **Mozilla Readability** — канонический алгоритм извлечения основного контента статьи.