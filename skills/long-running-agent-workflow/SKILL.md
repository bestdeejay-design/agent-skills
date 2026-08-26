---
name: long-running-agent-workflow
description: "Structured protocol for AI agents working across many context windows: a .lra/ directory with an atomic feature list (id/priority/acceptance criteria/status) and a session progress log, plus a session protocol (read context → pick ONE feature → implement → test → checkpoint) and recovery from broken states. Based on Anthropic research on long-running agents. Triggers: 'lra', 'checkpoint', 'feature list', 'long running', 'продолжи работу', 'долгая сессия', 'план фич', 'статус проекта'."
license: MIT
metadata:
  author: best
  version: "1.0.0"
  compatibility: "Requires Python 3 stdlib only (scripts/lra_cli.py). Works inside any git repo."
when_to_use: "For large multi-session projects needing continuity, atomic checkpoints, and recovery from broken states. Triggers: 'lra', 'checkpoint', 'feature list', 'long running', 'продолжи работу', 'долгая сессия', 'план фич', 'статус проекта'. Example: 'Help me track features across many sessions.'"
---

# Long-Running Agent (LRA) Workflow

Load this skill when you are about to work on a **large project that will span
multiple sessions / context windows** and you need continuity, atomic
handoffs, and recovery from broken states.

The skill gives you a tiny CLI (`scripts/lra_cli.py`) that maintains a `.lra/`
directory: a machine-readable `feature-list.json` (atomic features with
acceptance criteria and status) and a human/agent-readable `progress.txt`
(session log). The protocol turns "one big vague task" into a sequence of
small, fully-tested, check-pointed features.

---

## Overview — the problem

AI agents working across many context windows hit three failure modes:

- **Context amnesia** — each new session has no memory of prior work.
- **One-shot tendency** — trying to do too much at once, leaving half-done
  features.
- **Incomplete features** — work spans sessions with no clear acceptance
  gate, so "done" is never verified.

LRA fixes this with: structured init, one atomic feature per session, an
explicit test gate before `done`, and a checkpoint after every feature so the
next session can recover.

---

## When to use

- Long, multi-session projects (hours/days, many context windows).
- Any task where you might lose context between runs.
- Triggers: `lra`, `checkpoint`, `feature list`, `long running`,
  `продолжи работу над проектом`, `долгая сессия`, `план фич`, `статус проекта`.

If the task is small and finishes in one session, you do **not** need this
skill — just do the work.

---

## Prerequisites

- A **git repository** (so checkpoints can be committed and recovered).
- **Python 3** on `PATH` (the CLI is pure stdlib, no dependencies).
- Run the CLI from the **project root** (it creates/reads `.lra/` there).

---

## Instructions

### Phase 1 — Init

```bash
python3 scripts/lra_cli.py init "Short project description"
```

Creates `.lra/feature-list.json` (`{"project": ..., "features": [], "created": <date>}`)
and `.lra/progress.txt` with a header. Refuses (exit 1) if `.lra/` already
exists, so you never clobber an in-progress project.

### Phase 2 — Plan features

Add atomic, testable features. Each gets an `id` (`f1`, `f2`, …), a `name`,
a `priority` (`high`/`medium`/`low`), and `criteria` (acceptance criteria).

```bash
python3 scripts/lra_cli.py add "User registration endpoint" --priority high \
  --criteria "POST /api/auth/register accepts email+password; validates email; hashes password; returns JWT"
```

Rule: a feature must be completable in **one session** and have concrete
acceptance criteria. "Build the user system" is too big — split it.

### Phase 3 — Session protocol (repeat every session)

1. **Read context** — `status` and read `.lra/progress.txt` to see where you are.
2. **Pick ONE feature** — the highest-priority `todo` (or `wip` you abandoned).
3. **Implement** it.
4. **Test** it against its acceptance criteria (unit + integration + manual).
5. **Mark done** — `mark f<N> done` only after verification passes.
6. **Checkpoint** — `checkpoint "Implemented X and Y; tests green"`.

```bash
python3 scripts/lra_cli.py mark f1 done
python3 scripts/lra_cli.py checkpoint "User registration: endpoint + validation + tests"
```

### Phase 4 — Checkpoint / recover

- `checkpoint "<message>"` appends a timestamped line to `progress.txt`.
  Always checkpoint at the end of a session, even for partial work.
- `recover` prints the last 10 progress lines plus a summary of `wip`
  features — use it at the start of a session or after a broken state to see
  what was in flight.

### Phase 5 — Status

`status` prints a table of all features (id, name, priority, status) sorted
`todo → wip → done`, so you always know the current state at a glance.

---

## Best practices

- **One feature per session.** Finish it fully (code + tests) before moving on.
- **Always leave the codebase working.** No broken builds, no failing tests at
  a checkpoint.
- **Commit after each feature.** A checkpoint is a clean git state the next
  session can trust.
- **Update `feature-list.json` before closing** the session — mark status,
  add notes, add newly discovered sub-features with `add`.
- **Atomic features only.** Small, testable, single-purpose.

---

## Constraints and warnings

- **Never start a feature without acceptance criteria.** If none exist, write
  them first via `add --criteria`.
- **Never skip tests.** A feature is not `done` until its criteria are
  verified end-to-end.
- **Don't mark `done` without verification.** Marking `done` on unverified
  work poisons the next session's context.
- **Don't clobber `.lra/`.** `init` refuses if it exists; recover from the
  log instead of recreating.

---

## Files

- `SKILL.md` — this file
- `skill.json` — manifest
- `scripts/lra_cli.py` — the stdlib CLI (`init`, `add`, `mark`, `checkpoint`,
  `status`, `recover`)
- `references/lra-workflow.md` — full reference: `.lra/` file structure, JSON
  schemas, a worked example, the session checklist, and troubleshooting

## Installation

```bash
# For opencode
cp -r skills/long-running-agent-workflow ~/.config/opencode/skills/

# For other agents: copy the folder to your skills directory; requires Python 3.
```

---

> **Key principle**: leave the codebase in a testable, working state at the end
> of every session. The next session (and the next agent) picks up from the
> last checkpoint, not from amnesia.
