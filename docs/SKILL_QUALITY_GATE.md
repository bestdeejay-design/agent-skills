# Skill Quality Gate

Methodology for quality-controlling Agent Skills, grounded in two sources:

- **Layer A — Design**: [Claude Code Skills spec](https://code.claude.com/docs/en/skills) (the Agent Skills open standard + Claude Code extensions).
- **Layer B — Output verification**: Vercel Academy *Build Your Own AI Coding Agent Harness* → `verification-contract` lesson (plus `skills-system`, `descriptions-that-work`).

A skill passes the gate only when it satisfies Layer A **and** proves its output under Layer B.

---

## Layer A — Design audit (vs `code.claude.com/docs`)

Hard rules from the spec (non-negotiable):

- **A1 `name`** — ≤64 chars, pattern `a-z 0-9 -`, no double hyphens, MUST match the folder name.
- **A2 `description` + `when_to_use`** — describe *what* and *when*. `when_to_use` carries trigger phrases / example requests. The combined `description` + `when_to_use` text is truncated at **1,536 characters** in the skill listing — that is the real cap (not 1,024). `when_to_use` is recommended and is the single highest-leverage discoverability field.
- **A3 `body`** — concise. Claude Code has no hard line cap, but every loaded line is a recurring token cost, so keep it tight; `skill-forge` suggests <500 lines. Heavy reference material belongs in `references/` / `scripts/` (loaded on demand).
- **A4 Type** — Reference (knowledge) vs Task (action). Side-effecting Task skills should set `disable-model-invocation: true` so they run only on explicit `/name`.
- **A5 `allowed-tools` / `disallowed-tools`** — least privilege: pre-approve only what the skill needs; deny tools it must never call (e.g. `AskUserQuestion` in a background loop).
- **A6 Progressive disclosure** — bundle code in `scripts/`, docs in `references/`, outputs in `assets/`; reference files one level deep.
- **A7 Sharp triggers** — triggers must be "pushy": list synonyms and casual phrasings to fight undertriggering; add a **DO NOT USE FOR** negative steer so the skill is not auto-loaded for the wrong job.

---

## Layer B — Output verification (vs Vercel `verification-contract`)

A skill is not "done" on assertion; it must *prove* its result:

- **B1 Discover the gates** — read `package.json` / scripts: typecheck, lint, test, build. Run them; never claim success without running.
- **B2 Fail-fast order** — lint → typecheck → test → build. Stop at the first red.
- **B3 EVIDENCE, not assertion** — show the command, its output, and the exit status. A JSON report with an explicit `conformant`/pass field + a process exit code is the gold standard (see `api-contract-testing`).
- **B4 Scoped claims** — separate failures the change caused from pre-existing ones ("3 pre-existing failures, my change introduced none").
- **B5 Adversarial review** — have a fresh subagent try to break the output / find gaps before shipping.
- **B6 Deterministic gate** — for unattended runs, back the check with a Stop hook or a `/goal` evaluator so a turn cannot end on a false "done".
- **B7 Protective force = wording, not code** — bake the gate into the skill's instructions; the skill enforces quality by what it tells the model to do.

---

## How to apply

1. On touching any skill, run Layer A (frontmatter + structure) and Layer B (does it verify its own output?).
2. Log findings in `docs/skill-quality-audit.md` (per-skill snapshot).
3. Fix gaps: add `when_to_use` (highest leverage), tighten `description`, add a negative steer, wire a verification gate.

## Layer C — Continuous improvement (distributed, automatic)

Discovery is not enough; skills must get better as they are used — and **every
consumer of this collection can grow their own skills locally**, with no central
service and no dependency on the curator's repo.

### The portable loop
1. **Capture (automatic).** The agent logs near-miss triggers / manual corrections
   via `skill-feedback add` (JSONL in `feedback/<skill>/`). Make it automatic by
   adding the rule from `AGENTS_FRAGMENT.md` to your opencode `AGENTS.md` — then
   capture happens without an explicit nudge.
2. **Improve (one command).** Run `python3 skills/skill-forge/scripts/forge_from_feedback.py`
   (`--dry-run` to preview). It reads `feedback/`, calls your local LLM (DeepSeek
   key from `DEEPSEEK_API_KEY` or opencode `auth.json`), rewrites each flagged
   skill's `SKILL.md`, and commits locally — **no push**. You review and keep.
3. **Verify.** Re-run the Layer A/B audit (`docs/skill-quality-audit.md` generator)
   to confirm the edit moved the needle.

### Why it is distributed
- `feedback/` and the skills live in **your** clone/fork. `forge_from_feedback.py`
  resolves the repo it sits in, so it improves *your* skills, not the curator's.
- The curator (`best`) keeps `~/.config/opencode/skills` symlinked to this repo, so
  capture + improve are instantly live in opencode (live-reload for SKILL.md text).
- Others fork/clone, add the `AGENTS_FRAGMENT.md` rule, and run the same loop on
  their copy. Improvements stay with them unless they open a PR upstream.

This turns the Quality Gate into a living, self-improving loop for everyone.

## Pilot results (this repo)

- `api-contract-testing`: added `when_to_use` + **DO NOT USE FOR** steer (Layer A); Layer B already Strong (exit codes 0/1/2 + `conformant` JSON + CI gate).
- `skill-forge`: Layer B strengthened in Level 0 "Mandatory gates" (EVIDENCE, SCOPED CLAIMS, deterministic gate).
- `when_to_use` backfilled across all 46 remaining skills (2026-08-26); 47/47 now carry it.
