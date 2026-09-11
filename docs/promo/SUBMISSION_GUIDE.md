# 📬 Заявки в awesome-каталоги — готово к отправке за 2 минуты

> Токен Arena-интеграции ограничен репозиторием `agent-skills`, поэтому форки и PR
> во внешние репо нужно отправить вручную (или переподключить GitHub с полными
> правами — тогда всё сделает агент). Ниже — всё скопировано до последнего символа.

---

## 1. travisvn/awesome-claude-skills

### Куда вставить
`README.md` → секция **`### Collections & Libraries`** → в конец списка,
после блока `obra/superpowers-lab` (перед `### Individual Skills`).

### Что вставить

```markdown
- **[bestdeejay-design/agent-skills](https://github.com/bestdeejay-design/agent-skills)** - 59 CI-validated skills: frontend audits (Lighthouse/a11y/perf), security review & secret scanning, presentations (.pptx), 4-skill SEO pipeline, docs integrity, data & diagrams
  - Offline-first: scripts on Python stdlib, no API keys; CI validates all skills on every push
  - Bilingual docs (EN/RU); MIT; works with Claude Code, opencode, and Sisyphus-compatible agents
```

### PR: title

```
Add agent-skills collection to Collections & Libraries
```

### PR: body

```markdown
Adds one entry to **Collections & Libraries**.

- **Name/link:** [bestdeejay-design/agent-skills](https://github.com/bestdeejay-design/agent-skills)
- **Description:** 59 CI-validated skills covering frontend audits (real-Chrome Lighthouse, WCAG a11y, performance), security review orchestrating 13 scanners (semgrep, bandit, gitleaks, osv-scanner, trivy…), presentations with Playwright-verified slides shipped as real .pptx, a 4-skill SEO pipeline (audit / content / crawl / schema), documentation-integrity agents, and data & diagram tools.
- **Prerequisites:** Python 3.8+ (stdlib only for most skills; Playwright/Chrome optional for the frontend audit runners)
- **License:** MIT
- **Compatibility:** Claude Code, opencode, Sisyphus-compatible agents; bilingual docs (EN/RU)

Non-commercial, no SaaS dependency — standalone value.
```

---

## 2. VoltAgent/awesome-agent-skills

### Куда вставить
`README.md` → секция **`### Community Skills`** → блок
`<summary>Development and Testing</summary>` → последней строкой перед
закрывающим `</details>` этого блока.

### Что вставить

```markdown
- **[bestdeejay-design/agent-skills](https://github.com/bestdeejay-design/agent-skills)** - 59 CI-validated skills: frontend audits, security, presentations, SEO, docs, data
```

### PR: title

```
Add skill: bestdeejay-design/agent-skills
```

### PR: body

```markdown
Adds a community entry to **Development and Testing**.

**Repository:** https://github.com/bestdeejay-design/agent-skills

**What it is:** a collection of 59 agent skills — each a folder with `SKILL.md` + `skill.json` + Python scripts: frontend audits (Lighthouse/a11y/performance/testing/mobile), security review orchestrating 13 scanners, secret scanning, presentations (HTML → real .pptx with mandatory Playwright verification), a 4-skill SEO pipeline, documentation-integrity agents, and data/diagram tools.

**Why this category:** engineering/development skills; every skill is validated by a CI pipeline on each push (manifest + index cross-check), audit skills use exit-code gates for CI integration.

**License:** MIT · **Docs:** README (EN/RU) + per-skill SKILL.md + showcase examples (`docs/showcase/`)

I understand the "community usage" guideline — if this needs more maturity, I'm happy to resubmit later. Feedback welcome.
```

---

## 3. Как отправить (веб-интерфейс, ~1 минута на каталог)

1. Открой `https://github.com/<owner>/<repo>/edit/main/README.md` (кнопка-карандаш в README) — GitHub сам предложит сделать форк → **Fork this repository**.
2. Вставь блок из раздела «Что вставить» в указанное место (Ctrl+F по якорю: `Collections & Libraries` / `Development and Testing`).
3. **Commit changes** → ветка типа `add-agent-skills`.
4. **Create Pull Request** → вставь title и body из блоков выше → **Create PR**.
5. Через день-два проверь ответы мейнтейнеров (PR появятся в твоих уведомлениях).

> ⚠️ У VoltAgent в правилах: «brand new skills are not accepted, give your skill time to mature».
> Если PR отклонят по этому критерию — честно окей: вернись к заявке через 2–4 недели,
> когда наберутся звёзды/пользователи. У travisvn требование мягче («social proof»),
> шансы выше — начинай с него.

## 4. CLI-вариант (если удобнее терминалом, от своего аккаунта)

```bash
gh repo fork travisvn/awesome-claude-skills --clone
cd awesome-claude-skills && git checkout -b add-agent-skills
# …вставить блок в README.md…
git commit -am "Add agent-skills collection to Collections & Libraries"
git push -u origin add-agent-skills
gh pr create -R travisvn/awesome-claude-skills --title "Add agent-skills collection to Collections & Libraries" --body-file <(sed -n '/^```markdown$/,/^```$/p' ../agent-skills/docs/promo/SUBMISSION_GUIDE.md)
```
