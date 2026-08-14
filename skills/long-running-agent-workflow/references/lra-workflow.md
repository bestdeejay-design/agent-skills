# LRA Workflow — Reference

Full reference for the Long-Running Agent (LRA) workflow skill. The skill
`SKILL.md` is the quick-start; this file is the deep dive: file structure,
JSON schemas, a worked example, the session checklist, and troubleshooting.

---

## 1. `.lra/` file structure

```
.lra/
├── feature-list.json   # machine-readable: all features + status
└── progress.txt        # human/agent-readable session log
```

Both live at the **project root** (the directory where you run `lra_cli.py`).
The CLI refuses to `init` if `.lra/` already exists, so an in-progress project
is never clobbered.

---

## 2. JSON schemas

### `feature-list.json`

```json
{
  "project": "Chat app with auth and history",
  "features": [
    {
      "id": "f1",
      "name": "User registration endpoint",
      "priority": "high",
      "criteria": "POST /api/auth/register accepts email+password; validates email; hashes password; returns JWT",
      "status": "todo",
      "added": "2026-08-14"
    }
  ],
  "created": "2026-08-14"
}
```

| Field | Type | Notes |
|---|---|---|
| `project` | string | Short project description (from `init`) |
| `features` | array | Ordered list of features |
| `created` | string | ISO date (`YYYY-MM-DD`) |
| `features[].id` | string | `f<N>`, auto-assigned, monotonic |
| `features[].name` | string | Feature name; must be unique (case-insensitive) |
| `features[].priority` | enum | `high` \| `medium` \| `low` |
| `features[].criteria` | string | Acceptance criteria — the verification gate |
| `features[].status` | enum | `todo` \| `wip` \| `done` |
| `features[].added` | string | ISO date the feature was added |

### `progress.txt`

```
# Long-Running Agent Progress Log
# Project: Chat app with auth and history
# Created: 2026-08-14
[2026-08-14T14:05:00] Initialized project
[2026-08-14T15:30:00] Implemented user registration: endpoint + validation + tests
```

Each `checkpoint` appends one timestamped line (`[ISO-time] message`).

---

## 3. Worked example

```bash
# --- Session 1: initialize ---
python3 scripts/lra_cli.py init "Chat app with auth and message history"

python3 scripts/lra_cli.py add "User registration endpoint" --priority high \
  --criteria "POST /api/auth/register; validates email; hashes password; returns JWT"
python3 scripts/lra_cli.py add "User login endpoint" --priority high \
  --criteria "POST /api/auth/login; verifies credentials; returns JWT; 401 on bad creds"
python3 scripts/lra_cli.py add "Message creation endpoint" --priority medium \
  --criteria "POST /api/messages; persists message; returns created entity"

python3 scripts/lra_cli.py status
# ID    NAME                                   PRIORITY   STATUS
# f1    User registration endpoint            high       todo
# f2    User login endpoint                    high       todo
# f3    Message creation endpoint              medium     todo

# Implement f1, run its tests, then:
python3 scripts/lra_cli.py mark f1 done
python3 scripts/lra_cli.py checkpoint "User registration: endpoint + validation + tests"

# --- Session 2: recover context, continue ---
python3 scripts/lra_cli.py recover
# shows last 10 progress lines + wip features (none yet)

python3 scripts/lra_cli.py status
# f1 ... done ; f2/f3 ... todo

# Implement f2, test, mark, checkpoint.
python3 scripts/lra_cli.py mark f2 done
python3 scripts/lra_cli.py checkpoint "User login + JWT generation"

# --- Session 3: discovered a sub-feature mid-work ---
python3 scripts/lra_cli.py add "Rate limiting for message endpoints" --priority medium \
  --criteria "Limit messages per user per minute; 429 when exceeded"
# f4 added; it will surface in the next session's status.
```

---

## 4. Session checklist

Run this loop every session:

- [ ] `recover` (or `status`) — read where the last session left off.
- [ ] Pick **one** feature: highest-priority `todo`, or an abandoned `wip`.
- [ ] Confirm it has **acceptance criteria**; if not, `add --criteria` first.
- [ ] Implement the feature.
- [ ] Test against the criteria (unit + integration + manual).
- [ ] `mark f<N> done` **only after** tests pass.
- [ ] `checkpoint "<what was done>"` — append to the log.
- [ ] Commit the working tree (a clean git state the next session can trust).
- [ ] Update `feature-list.json` notes / add discovered sub-features.

---

## 5. Troubleshooting

### `.lra/` already exists
`init` exits 1. You don't need to re-init — just `status` / `recover` and
continue. Only `init` a fresh project once.

### Stale `.lra/` (features don't match reality)
Edit `feature-list.json` directly (it's plain JSON) or use `add` / `mark`.
Never delete `.lra/` to "fix" it — you'd lose history. Prefer `recover` to
read the log and reconcile.

### Conflicting feature ids
IDs are auto-assigned as `f<N>` from the max existing numeric suffix, so they
never collide as long as you use `add`. If you hand-edit the file and create a
duplicate id, `mark`/`status` will still work but `recover` summaries may be
ambiguous — keep ids unique.

### Lost progress / broken state
1. `recover` — read the last 10 log lines and the `wip` summary.
2. `git log --oneline -10` and `git status` to see code state.
3. Fix or `git revert`/`git reset --soft` to a known-good commit.
4. Re-run tests, then `checkpoint` with a note about the recovery.

### Duplicate feature name
`add` rejects a name that already exists (case-insensitive). Rename or split
the feature instead of duplicating.

---

## 6. Design notes

- **Statuses are `todo` / `wip` / `done`** — three states keep the model
  simple. `wip` marks a feature started but not verified; `done` is only set
  after the acceptance criteria pass.
- **One feature per session** is the core discipline: it bounds context usage
  and guarantees each handoff is a complete, tested unit.
- Based on Anthropic's research on effective harnesses for long-running agents
  (continuity, atomic units of work, clean checkpoints).
