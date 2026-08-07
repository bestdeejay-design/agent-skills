## What does this PR do?

<!-- Short summary of the change and the problem it solves. -->

## Related
<!-- Link to the issue this closes, if any: fixes #123 -->

## Skill / scope
<!-- Which skill or repository area is affected. -->

## Checklist

- [ ] `SKILL.md` + `skill.json` present and valid (if adding/updating a skill)
- [ ] `index.json` updated (name, version, category, description, path, triggers, updated)
- [ ] `skill.json` version bumped (semver) and `updated` set to today's date
- [ ] `python3 -m json.tool index.json` passes
- [ ] README catalog row matches `index.json`
- [ ] No AI-slop wording, no stale/mismatched docs (README.md ↔ README.ru.md in sync)