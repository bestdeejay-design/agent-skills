---
name: repo-community-files
description: "Create and maintain repository community/legal files: LICENSE, CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, SUPPORT.md, issue/PR templates, FUNDING.yml. No scripts — template-driven. Triggers: 'license file', 'code of conduct', 'contributing guide', 'security policy', 'support file', 'issue template', 'pr template', 'funding yml', 'community files', 'repo legal files', 'contributor covenant'."
license: MIT
metadata:
  author: bestdeejay-design
  version: "1.0.0"
compatibility: "No scripts; gh CLI optional for org-level defaults"
---

# Repo Community Files — legal & community health files

Use this skill to **create or update the community/legal files** of a repository:
LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, issue/PR templates, FUNDING.

These files drive the GitHub **Community Standards** checklist (the "Community Health"
percentage). Missing files lower the score and block contributions.

## When to use

- A new repository needs its legal/community files set up.
- A file is missing or outdated (e.g. SECURITY contact changed, CONTRIBUTING process changed).
- User asks for "license file", "code of conduct", "contributing guide", "security policy",
  "issue template", "pr template", "funding".

## Do NOT use

- For README content/visuals — use `repo-readme-assets`.
- For description/topics/Pages/community-health audit — use `repo-metadata-health`.
- For social preview PNG — use `repo-social-preview`.

## Files

- `SKILL.md` — this file (template-driven; no scripts)

## Required / desirable files

| File | Purpose | When to update |
|------|-----------|-----------------|
| `LICENSE` | MIT license (owner/year) | on creation, owner change |
| `CODE_OF_CONDUCT.md` | Contributor Covenant 2.1 (full text + contact) | rarely |
| `CONTRIBUTING.md` | Contributor instructions | on process/convention change |
| `SECURITY.md` | Security policy | on contact/policy change |
| `SUPPORT.md` | UPPERCASE filename; "Support" link in issue helper | rarely |
| `.github/ISSUE_TEMPLATE/*.yml` | Issue forms (bug_report, feature_request) — drive the Community Health check | on process change |
| `.github/pull_request_template.md` | PR template (root/`docs/`/`.github/`, `.md`/`.txt`) | on process change |
| `.github/release.yml` | Auto-generated release notes config | on first release |
| `FUNDING.yml` | Optional: "Sponsor" button | rarely |
| `CHANGELOG.md` | Optional: Keep a Changelog format | on each release |

> `LICENSE` must NOT be moved into `.github/` — GitHub recognizes it only at the repo
> root or `docs/` (default files in `.github/` are NOT scanned for license).

## Org-level defaults

GitHub supports **organization-level** community health files via a special `.github`
repository. Files not found in a repo are inherited from the org `.github` repo — except
`LICENSE` (never inherited). Prefer org-level defaults for boilerplate, keep repo-level
copies for repo-specific policies.

## Anti-patterns

- Public repo without a LICENSE.
- Accepting contributions without SECURITY.md.
- `LICENSE` placed under `.github/` (not detected).
- Outdated contacts in SECURITY.md / CODE_OF_CONDUCT.md.
- Issue templates as `.md` instead of `.yml` forms (forms add the Community Health check).
