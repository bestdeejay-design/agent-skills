# Canonical Patterns: вежливый и законный веб-скрапинг

Справочник канонических аналогов, недостающих техник и цитируемых примеров для
`scripts/scrape.py`. Скрипт уже соблюдает базовые guardrails (robots.txt, честный
User-Agent, задержка 1.0 c, лимит 10 МБ) — ниже: что делают эталоны и чего не хватает.

## (a) Canonical analogues

| # | Name | Owner | URL | Type |
|---|------|-------|-----|------|
| 1 | MCP Fetch Server | modelcontextprotocol | https://github.com/modelcontextprotocol/servers/tree/main/src/fetch | MCP server «URL → Markdown» |
| 2 | Scrapy | scrapy/scrapy | https://github.com/scrapy/scrapy | Python crawling framework |
| 3 | Crawlee | apify/crawlee | https://github.com/apify/crawlee | Crawling library (JS/TS, есть Python) |
| 4 | Playwright | microsoft/playwright | https://github.com/microsoft/playwright | Browser automation |
| 5 | Trafilatura | adbar/trafilatura | https://github.com/adbar/trafilatura | CLI/library: HTML → Markdown/JSON |
| 6 | Mozilla Readability | mozilla/readability | https://github.com/mozilla/readability | Main-content extraction algorithm |

**1. MCP Fetch Server** — фактически «родной fetch» экосистемы Anthropic
(MCP-стандарт создан Anthropic). README подтверждает ровно те guardrails, что у
нас: robots.txt по умолчанию, честный User-Agent
`ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)`
с контактным URL, лимит `max_length` (по умолчанию 5000 символов), чанкованное
чтение через `start_index` —
[README](https://github.com/modelcontextprotocol/servers/blob/76d64c822f51/src/fetch/README.md).

**2. Scrapy** — эталон «вежливых» настроек как middleware:
`RobotsTxtMiddleware` скачивает robots.txt per-domain и кидает `IgnoreRequest`
при запрете ([robotstxt.py](https://github.com/scrapy/scrapy/blob/1bd839b57ddb/downloadermiddlewares/robotstxt.py));
`AutoThrottle` — адаптивная задержка `target_delay = latency / target_concurrency`
([throttle.py](https://github.com/scrapy/scrapy/blob/1bd839b57ddb/extensions/throttle.py)); `RetryMiddleware` — ретраи по умолчанию на `{500, 502, 503, 504, 522, 524, 408, 429}`.

**3. Crawlee** (Apify) — современный эталон: `respect_robots_txt_file=True` в
опциях краулера ([пример](https://crawlee.dev/python/docs/examples/respect-robots-txt-file)),
ретраи с backoff, autoscaling, ротация прокси; открытый issue про автоматическое соблюдение `crawl-delay` из robots.txt:
[apify/crawlee-python#1396](https://github.com/apify/crawlee-python/issues/1396).

**4. Playwright** — канонические паттерны извлечения: `Locator.text_content()`,
`Locator.innerHTML()`, `Page.content()`, `get_by_role(...).all_inner_texts()`
([class-locator.md](https://github.com/microsoft/playwright/blob/c973356ee9e3/docs/src/api/class-locator.md));
паттерн Anthropic webapp-testing: `page.wait_for_load_state('networkidle')` перед
извлечением ([SKILL.md](https://github.com/anthropics/skills/blob/main/skills/webapp-testing/SKILL.md)).

**5. Trafilatura** — ближайший по назначению аналог: CLI и Python-библиотека
извлечения основного текста статьи в Markdown/JSON/TXT.

**6. Mozilla Readability** — канонический алгоритм извлечения основного контента
страницы (движок Reader View в Firefox); сильнее простого CSS-селектора для статей.

В официальном `anthropics/skills` scraping-скилла нет; сторонние GitHub-скиллы
низкорепутационные и эталонами не являются.

## (b) Techniques missing vs canonicals

Техники, которых нет в `scrape.py`, но которые есть в эталонах:

- **Crawl-delay / Request-rate из robots.txt** — `urllib.robotparser` умеет из
  коробки: `crawl_delay(useragent)`, `request_rate(useragent)`, `site_maps()`
  (Python 3.6+/3.8+). Вместо фиксированной задержки 1.0 c уважать `Crawl-delay`
  (каппировать: серверы пишут часы — Slatecave: «cap this at 2 minutes»);
  Google `crawl-delay` не поддерживает.
- **Кэширование robots.txt + перепроверка** — `mtime()`/`modified()` для
  периодической перепроверки на долгих краулах; Google кэширует robots.txt до
  24 часов, при 5xx не краулит 12 часов; практика: refetch после минут краулинга.
- **Retry-After (оба формата)** — RFC 9110 §10.2.3: `http-date` ИЛИ
  `delay-seconds`; применяется к 503/429/редиректам. Эталон: `urllib3.util.Retry`
  — `respect_retry_after_header=True`, `RETRY_AFTER_STATUS_CODES = {413, 429, 503}`,
  потолок `retry_after_max = 21600` (6 часов); http-date — через `email.utils`.
- **Exponential backoff + jitter** — формула urllib3:
  `sleep = backoff_factor * (2 ** retries) + random.uniform(0, backoff_jitter)`,
  кап `backoff_max = 120`. GitHub API: ретраи во время rate limit «may result
  in the banning».
- **429 handling** — не просто ретраить, а замедлиться (снизить темп) и уважать Retry-After.
- **Status-code retry set** — эталон Scrapy: `{408, 413, 429, 500, 502, 503, 504, 522, 524}` (default Scrapy без 413 — расширенный вариант из urllib3).
- **Rate-limit заголовки** — читать `X-RateLimit-Limit/Remaining/Reset/Used`
  (канон: GitHub API); не ретраить до `x-ratelimit-reset` / `Retry-After`; многие
  сайты отдают Retry-After без 429-семантики — проверять заголовок на любом ответе.
- **Conditional requests** — ETag/Last-Modified → `If-None-Match`/`If-Modified-Since`
  → `304 Not Modified`; HEAD перед GET для проверки Content-Type/Content-Length;
  отделять краулинг от анализа (кэшировать сырой HTML).
- **Accept-Encoding: gzip** — лимит 10 МБ должен считаться по декодированному
  размеру, иначе лимит обходится сжатием; stdlib: `urllib.request` + `gzip.decompress`.
- **Adaptive delay (латентность)** — Scrapy AutoThrottle
  `target_delay = latency / target_concurrency`; Stract/Unobtanium: dynamic delay
  как кратное времени ответа.
- **meta robots / X-Robots-Tag** — доп. сигналы запрета индексации помимо robots.txt.
- **From header (RFC 9110 §10.1.2)** — email владельца бота, поле создано именно
  для ботов; дескриптивный UA: имя бота, версия, URL/email (канон: The Web
  Scraping Club — «MyAwesomeScraper/1.0 (http://…/bot.html; mailto:bot@…)»).
- **Sitemap как вежливый источник** — `site_maps()` из robotparser; краулить только разрешённое и по sitemap, а не перебором.
- **PII / GDPR / ToS awareness** — скрейпинг персональных данных подпадает под
  GDPR/CPRA даже при публичности; републикация текстов = риск копирайта;
  «Don't scrape what you could get through an API»; суды не всегда трактуют
  robots.txt как юридически обязательный — но соблюдение остаётся профстандартом.
- **Cache-busting** — анти-паттерн вежливого скрапинга: увеличивает нагрузку;
  канон — уважать кэш (условные запросы); применять только когда нужна свежая версия.

## (c) Citable CLI/API examples

```bash
# curl: ретраи, честный UA, gzip, лимит размера (man: https://curl.se/docs/manpage.html#--retry)
curl --retry 3 --retry-delay 5 --retry-all-errors --retry-connrefused \
     --compressed -A "MyBot/1.0 (+https://example.org/bot.html; bot@example.org)" \
     --max-filesize 10485760 -o page.html https://target.example/page

# wget: вежливое зеркалирование (GNU wget manual: https://www.gnu.org/software/wget/manual/wget.html#index-wait)
wget --wait=2 --random-wait --limit-rate=50k --robots=on https://target.example/page

# Python stdlib: robots.txt до запроса (https://docs.python.org/3/library/urllib.robotparser.html)
python3 -c "
from urllib.robotparser import RobotFileParser
rp = RobotFileParser(); rp.set_url('https://target.example/robots.txt'); rp.read()
print(rp.can_fetch('MyBot/1.0', 'https://target.example/page'))
print(rp.crawl_delay('MyBot/1.0'))   # уважать это значение вместо фиксированной задержки
"

# urllib3 Retry: эталон backoff + Retry-After (https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html)
from urllib3.util.retry import Retry
Retry(total=5, backoff_factor=0.1, backoff_jitter=0.5,
      status_forcelist=[408, 413, 429, 500, 502, 503, 504, 522, 524],
      respect_retry_after_header=True, retry_after_max=21600)

# Scrapy shell: интерактивная отладка селекторов (эталон синтаксиса)
scrapy shell https://docs.scrapy.org/en/latest/_static/selectors-sample1.html
# response.css('title::text').get()  →  'Example website'

# Trafilatura: HTML → Markdown из CLI (https://github.com/adbar/trafilatura)
trafilatura -u https://target.example/article --output-format markdown

# MCP Fetch Server: эталонный «fetch» с robots.txt по умолчанию (https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)
uvx mcp-server-fetch        # tools: fetch(url, max_length, start_index, raw)
```

Селекторный канон (parsel/Scrapy): `::text` для текстовых узлов, `::attr(href)`
для атрибутов (CSS-расширения, отсутствуют в спеке W3C Selectors), `.get()` =
первый или None, `.getall()` = список, `.xpath(".//p")` — относительные пути;
формат `tag#id`, `tag.class` из `scrape.py` — подмножество этого канона.

## Sources

Официальные спеки: RFC 9309 (robots.txt) · RFC 9110 §10.2.3 (Retry-After) ·
RFC 9110 §10.1.2 (From) · urllib.robotparser (Python 3.14) · Google robots.txt
spec · MDN Retry-After / X-Robots-Tag · GitHub API rate limits.