# Canonical patterns: github-repo-hygiene

> Эталонные источники и пробелы текущего скилла относительно канонов.
> Обработка результатов librarian-исследования (август 2026).

---

## (a) Named analogues

| # | Name | Owner | URL | Type |
|---|------|-------|-----|------|
| 1 | Creating a default community health file | GitHub | https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file | Официальная документация |
| 2 | Community profiles / Community Profile API | GitHub | https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories | Официальная документация + REST API |
| 3 | GitHub CLI (`gh repo edit`, `gh release create`) | cli/cli | https://cli.github.com/manual/gh_repo_edit | Официальный CLI |
| 4 | GitHub REST API — Repositories / Pages / Licenses / Custom Properties | GitHub | https://docs.github.com/en/rest/repos/repos | Официальное API |
| 5 | `github/docs` | GitHub | https://github.com/github/docs | Эталонный репозиторий |
| 6 | `facebook/react`, `kubernetes/kubernetes`, `vercel/next.js`, `microsoft/vscode` | Meta / CNCF / Vercel / Microsoft | (см. ниже) | Эталонные репозитории |
| 7 | Contributor Covenant v2.1 | contributor-covenant | https://github.com/contributor-covenant/contributor-covenant | Стандарт текста CoC |
| 8 | SPDX License List | SPDX | https://github.com/spdx/license-list-data | Стандарт идентификаторов лицензий |

---

## (b) Techniques the script is MISSING

| # | Technique / Source | What is missing in current skill |
|---|--------------------|----------------------------------|
| 1 | **Org-level `.github` repository** (GitHub Docs) | Скилл не проверяет/создаёт org-level публичный репозиторий `.github` с дефолтными health-файлами для всей организации. |
| 2 | **Community Profile API** `GET /repos/{owner}/{repo}/community/profile` (GitHub Docs) | Нет использования официального аудита с метрикой `health_percentage` (эталон `github/docs` = 100). |
| 3 | **Org-level health files priority** (GitHub Docs) | Приоритет поиска: `.github/` → корень → `docs/`. Скилл ищет только в целевом репозитории. |
| 4 | **LICENSE cannot be default** (GitHub Docs) | Нет явного правила: лицензия не наследуется из org-level `.github` — обязательна в каждом репо. |
| 5 | **FUNDING.yml / GOVERNANCE.md** (GitHub Docs) | Не проверяет/создаёт `FUNDING.yml` (кнопка Sponsor) и `GOVERNANCE.md`. |
| 5 | **Issue template validity rules** (Community Profile API) | `.md`-шаблоны должны иметь `name:` + `about:`; `.yml`-формы — `name:` + `description:`. Иначе API не засчитывает их. |
| 7 | **gh repo edit — full flag set** (GitHub CLI) | Нет: `--add-topic/--remove-topic`, `--template`, `--default-branch`, `--enable-*` (issues/wiki/projects/discussions/advanced-security/secret-scanning), `--visibility` с обязательным `--accept-visibility-change-consequences`. |
| 8 | **gh release create — draft-then-publish flow** (GitHub CLI) | При ассетах: draft → parallel upload → publish (`PATCH {"draft": false, "make_latest": true}`); immutable releases (если включены в настройках). |
| 9 | **PATCH /repos/{owner}/{repo} — full field set** (REST API) | Нет: `is_template`, `archived`, `security_and_analysis` (advanced security, secret scanning, dependabot), `has_issues/has_wiki/has_projects/has_discussions`. |
| 10 | **Topics via separate endpoint** (REST API) | Топики редактируются **только** через `PUT /repos/{owner}/{repo}/topics` (полная замена списка), а не через PATCH /repos. |
| 11 | **Pages API** (REST API) | Нет: `POST /repos/{owner}/{repo}/pages` (source branch + path + `cname` + `build_type: legacy|workflow`), `GET /.../pages/health` (DNS-health-чек). |
| 12 | **Custom Properties API** (REST API) | Нет: `GET/PATCH /repos/{owner}/{repo}/properties/values` — enterprise метаданные (ownership, deployable, CodeQL-Block). Эталон: `github/docs`. |
| 13 | **Security & Analysis API** (REST API) | Нет управления `security_and_analysis` (advanced security, secret scanning, push protection, dependabot). |
| 14 | **Archival / Transfer via API** (REST API) | Нет: `PATCH {"archived": true}` и `POST /repos/{owner}/{repo}/transfer` (Pages не редиректится при трансфере). |
| 15 | **SPDX License API** (REST API) | Нет сверки лицензии через `GET /repos/{owner}/{repo}/license` (ключи = SPDX) и сверки с каталогом SPDX (`spdx/license-list-data`). |
| 16 | **Social preview — UI only** (GitHub Docs) | Social preview image (PNG/JPG/GIF <1MB, ≥640×320) настраивается **только через UI**; публичного REST-эндпоинта нет. |
| 17 | **Enterprise patterns: custom properties, CODEOWNERS, dependabot.yml** (`github/docs`) | Нет: custom properties (ownership/deployable), `CODEOWNERS`, `dependabot.yml`, issue-формы YAML + `config.yml`. |
| 18 | **SUPPORT.md / SECURITY_CONTACTS / AGENTS.md / CLAUDE.md** (k8s, react, next.js) | Нет шаблонов: SUPPORT.md (редирект на внешние каналы, паттерн k8s), SECURITY_CONTACTS (k8s legacy), AGENTS.md/CLAUDE.md (next.js AI-instructions). |
| 19 | **Contributor Covenant v2.1 as canonical CoC** | Скилл создаёт CoC, но канон — Contributor Covenant 2.1 (key `contributor_covenant` в community profile). |
| 20 | **SPDX License List as canonical identifiers** | Нет сверки с `spdx/license-list-data` и сверки через `GET /licenses` / `GET /repos/{owner}/{repo}/license`. |

---

## (c) Citable CLI/API examples

```bash
# 1) Community Profile API — официальный аудит гигиены (health_percentage + чеклист файлов)
gh api repos/bestdeejay-design/lovii_demo/community/profile --jq '{health_percentage, files, description, documentation}'

# 2) gh repo edit — полный набор флагов
gh repo edit bestdeejay-design/lovii_demo \
  --description "White-label SaaS platform for local marketplaces" \
  --homepage https://lovii.ru \
  --add-topic marketplace,white-label,saas,local-commerce \
  --enable-discussions \
  --enable-issues \
  --enable-wiki \
  --enable-projects=false \
  --default-branch main

# 3) Topics — только через отдельный эндпоинт (полная замена)
gh api repos/bestdeejay-design/lovii_demo/topics \
  -X PUT -f 'names[]="marketplace"&names[]="white-label"&names[]="saas"&names[]="local-commerce"'

# 4) Pages — создание/обновление + health check
gh api repos/bestdeejay-design/lovii_demo/pages \
  -X POST -f 'source[branch]=gh-pages' -f 'source[path]=/' \
  -f 'cname=lovii.ru' -f 'build_type=workflow' -f 'https_enforced=true'
gh api repos/bestdeejay-design/lovii_demo/pages/health --jq '.dns_resolves, .is_valid, .responds_to_https'

# 4) Custom Properties — enterprise метаданные
gh api repos/bestdeejay-design/lovii_demo/properties/values \
  -X PATCH -f 'properties[][property_name]=ownership-name&properties[][value]=bestdeejay-design' \
  -f 'properties[][property_name]=deployable&properties[][value]=true'

# 5) Security & Analysis
gh api repos/bestdeejay-design/lovii_demo -X PATCH \
  -f 'security_and_analysis[secret_scanning][status]=enabled' \
  -f 'security_and_analysis[secret_scanning_push_protection][status]=enabled' \
  -f 'security_and_analysis[dependabot_security_updates][status]=enabled'

# 6) Archival / Transfer
gh api repos/bestdeejay-design/lovii_demo -X PATCH -f archived=true    # архивация
gh api repos/bestdeejay-design/lovii_demo/transfer -X POST -f new_owner=acme-corp  # трансфер (Pages не редиректится)

# 7) License — SPDX сверка через API
gh api repos/bestdeejay-design/lovii_demo/license --jq '.license.spdx_id, .license.name'
gh api licenses --jq '.[] | select(.key=="mit") | .spdx_id'

# 8) gh release create — draft-then-publish + generate-notes
gh release create v1.2.3 --generate-notes --title "v1.2.3" --target main

# 9) gh repo edit — полные флаги (примеры)
gh repo edit bestdeejay-design/lovii_demo \
  --add-topic white-label,marketplace \
  --remove-topic deprecated \
  --template \
  --default-branch main \
  --enable-discussions \
  --enable-issues \
  --enable-secret-scanning \
  --enable-secret-scanning-push-protection \
  --visibility public --accept-visibility-change-consequences
```

---

## (d) Adopted already

1. **README EN/RU sync** — соответствует требованию bilingual README в community health docs.
2. **LICENSE check** — наличие LICENSE проверяется (но не сверяется через SPDX API).
3. **CODE_OF_CONDUCT / CONTRIBUTING / SECURITY / SUPPORT** — файлы проверяются/создаются.
4. **Issue/PR templates** — базовые шаблоны поддерживаются.
5. **Social preview** — упомянут (но реализация только через UI, API нет).
6. **Topics** — управление есть (но через PATCH, а не PUT topics endpoint).
7. **Releases** — `gh release create` используется.
8. **GitHub Pages** — наличие проверяется (но не через Pages API + health check).
9. **Description / Homepage** — `gh repo edit` с `-d/--homepage` используется.

---

## (e) Canonical analogue details (for deep enrichment)

### 1. GitHub Docs — Default community health files
- **URL**: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file
- **Паттерны**: org-level публичный репозиторий `.github` → дефолтные файлы для всех репо аккаунта; приоритет поиска `.github/` → root → `docs/`; LICENSE не наследуется; полный список health-файлов (CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, FUNDING.yml, GOVERNANCE.md, issue/PR templates + config.yml).

### 2. GitHub Docs — Community Profile API
- **URL**: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories
- **API**: `GET /repos/{owner}/{repo}/community/profile`
- **Ключевой паттерн**: `health_percentage` (0–100), структурированный чеклист файлов. Эталон `github/docs`: 100%. Шаблоны считаются валидными только при наличии `name:`+`about:` (md) или `name:`+`description:` (yml).

### 3. GitHub CLI
- **gh repo edit**: https://cli.github.com/manual/gh_repo_edit
- **gh release create**: https://cli.github.com/manual/gh_release_create
- **Паттерны**: полный набор флагов редактирования репозитория, draft-then-publish flow для релизов, immutable releases.

### 4. GitHub REST API
- **Repositories**: https://docs.github.com/en/rest/repos/repos
- **Pages**: https://docs.github.com/en/rest/pages/pages
- **Licenses**: https://docs.github.com/en/rest/licenses/licenses
- **Custom Properties**: https://docs.github.com/en/rest/repos/custom-properties
- **Паттерны**: PATCH /repos (все поля), PUT /repos/{owner}/{repo}/topics (топики отдельно), Pages API (cname, health check, build_type workflow), Custom Properties API, security_and_analysis, archival/transfer.

### 5. github/docs — эталонный репозиторий
- **URL**: https://github.com/github/docs
- **Community health**: 100%.
- **Паттерны**: .github/ (CODE_OF_CONDUCT=Contributor Covenant, CONTRIBUTING, PULL_REQUEST_TEMPLATE, ISSUE_TEMPLATE с config.yml + 3 YAML-формы, CODEOWNERS, dependabot.yml, workflows), custom properties (ownership-name, ownership-type, deployable, CodeQL-Block), topics: docs/works-with-codespaces, LICENSE CC-BY-4.0.

### 6. Эталонные репозитории (react / k8s / next.js / vscode)
- **facebook/react**: SECURITY.md как pointer на программу вознаграждений, has_pages=true, homepage=react.dev.
- **kubernetes/kubernetes**: SUPPORT.md (редирект на Stack Overflow), SECURITY_CONTACTS (legacy), OWNERS, LICENSE Apache-2.0.
- **vercel/next.js**: AGENTS.md, CLAUDE.md (AI-instructions), DISCUSSION_TEMPLATE, issue forms, CODEOWNERS.
- **microsoft/vscode**: CODENOTIFY, CODEOWNERS, custom properties (activeRepoStatus, global-rulesets-opt-out).

### 7. Contributor Covenant v2.1
- **URL**: https://github.com/contributor-covenant/contributor-covenant
- **Паттерн**: Канонический текст CoC, распознаётся community profile как key `contributor_covenant`. GitHub Docs использует именно его.

### 8. SPDX License List
- **URL**: https://github.com/spdx/license-list-data
- **Паттерн**: Канонические SPDX-идентификаторы (MIT, Apache-2.0, CC-BY-4.0...); GitHub Licenses API conforms to SPDX specification.

### 9. Локальные анимированные SVG (visual README header/footer)
- **Канон**: никаких внешних сервисов-баннеров (`capsule-render` и аналоги) —
  README ссылается на собственные `assets/header.svg` + `assets/footer.svg`
  относительными путями, анимация — декларативный SMIL (`<animate>`,
  `<animateTransform>`), без `<script>`.
- **Паттерн «фон наплывает»**: цвет баннера вырезается `<mask>` (белый `<rect>`
  + чёрная волна = дыра), сквозь дыру виден фон страницы. Header: дыра снизу
  (волна до y≈245 при высоте 290), градиент `COLD→WARM` + 2 полупрозрачные
  белые волны (0.25 до y≈232, 0.5 до y≈220) поверх градиента. Footer: зеркало —
  дыра сверху (волна до y≈21 при высоте **60**), инверсия `WARM→COLD` +
  twinkling-текст `@USERNAME`; все патчи footer начинаются выше холста
  (`y=-12`/`-16`), чтобы при анимации не открывалась полоска градиента.
- **Рассинхрон волн**: вертикальное «дыхание» `translateY` с `calcMode="spline"`
  и задержками 30% периода (`0s` / `-1.8s` / `-3.6s` при `dur="6s"`) — слои
  никогда не совпадают по фазе; пики `d`-path каждого слоя смещены относительно
  других (иначе слои сливаются).
- **Встраивание**: `<p align="center"><a href="https://github.com/USERNAME" target="_blank"><img src="assets/header.svg" alt="header" /></a></p>`.
- **Паттерны**: градиенты тёплый+холодный, высокий контраст, текст `FFFFFF`
  на тёмном / `1A1A2E` на светлом + тёмный дубль-тень под текстом, запрет белого
  в середине градиента, инверсия палитры header→footer, относительные ссылки
  (работают в клонах/форках).
- **Ограничение GitHub**: в SVG внутри `<img>` запрещены скрипты — анимация
  только SMIL; SMIL-анимации работают в README (SRC через raw.githubusercontent.com).
  `<mask>` + SMIL-анимация внутри маски поддерживаются.

---

> **Сводка**: текущий скилл покрывает ~9 из 20+ канонических паттернов. Главные пробелы: Community Profile API (health_percentage), org-level .github, Pages API + health check, Custom Properties, Security & Analysis API, SPDX-валидация лицензии, Social preview (нет API), Archival/Transfer API, Enterprise custom properties, новые AI-файлы (AGENTS.md/CLAUDE.md), SECURITY_CONTACTS/SUPPORT.md-паттерны.