# agent-skills — skills for AI agents (systematic, verified, reusable)

> A home for skills that make agents (and humans) do **systematic, verifiable work** —
> starting with `docs-system`, the "documentation from an idea" skill. Every skill here
> follows the same spirit: explicit catalogs, fill order, levels, templates, and a
> completeness gate — so nothing is forgotten and results are checkable.

## Skills

| Skill | What it does | Install |
|-------|--------------|---------|
| [`docs-system`](docs-system/SKILL.md) | Systematic documentation for any project: from an idea to a complete documentation set (levels L1/L2/L3, catalog, fill order, 14 templates, completeness checklist). | copy `docs-system/` → `~/.config/opencode/skills/docs-system/` (opencode) |

> More skills land here over time (see `docs-system/ROADMAP.md` for the direction).

## Why skills, and why *this* style

An agent is only as good as the **system** it's given. A skill is that system:
named, loadable on demand, with rules that survive across sessions. This repo's
skills are built the way the best projects are built:

1. **Catalog first** — every artifact (doc/step/check) is listed with *why* and *when*.
2. **Order matters** — there is an explicit sequence (e.g. contracts before code,
   map last), so the result is coherent, not a pile.
3. **Right-sized** — levels (minimal → canonical → profile) mean a small project
   isn't drowned in process, and a big one isn't under-documented.
4. **Verifiable** — a completeness checklist closes the loop: "done" is provable.

## Install (opencode)

```bash
# from this repo
cp -R docs-system ~/.config/opencode/skills/docs-system

# or clone the skills repo and symlink
ln -s "$PWD/docs-system" ~/.config/opencode/skills/docs-system
```

Then trigger it by asking for "системная документация / docs catalog / полная
документация" or by loading the skill by name.

## Structure of a skill (the docs-system convention)

Every skill in this repo should follow the same shape (this is what makes the repo
predictable):

```
<skill>/
├── SKILL.md                  # interface: what, when, how to choose, order of use
├── references/               # the mechanics
│   ├── catalog.md            # all artifacts: name → purpose → when → level
│   ├── order.md              # the sequence (phases) to follow
│   ├── levels.md             # right-sizing (L1 minimal / L2 canonical / L3 profiles)
│   ├── completeness.md       # the gate: "nothing forgotten" checklist
│   └── templates/            # copy-paste skeletons
├── ROADMAP.md                # development plan (now → short → mid → long)
└── examples/                 # a real-world reference of the skill applied
```

This convention is itself documented and enforced by `docs-system` — the repo
practices what it preaches.

## Contributing

- New skills: follow the structure above; include a `ROADMAP.md` and at least one
  example; run the completeness gate on your own skill.
- See [CONTRIBUTING.md](CONTRIBUTING.md) (if not yet present, adding it is the
  first contribution).

## License

MIT © <!-- owner -->.

---

### Roadmap for this repo

- Add a `skills.json` inventory (machine-readable list of skills + versions).
- Add CI-style validation: every skill passes its own completeness gate.
- Grow the skill family: agent runbook, delivery-gate, test-design — same
  catalog/order/levels/checklist spine.