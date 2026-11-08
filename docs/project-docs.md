# Project docs: findable, owned, checked

For a project's own `docs/` folder (none at the start: add it when a topic needs more than a line in
`AGENTS.md`). One topic per doc. Agents find docs from their frontmatter, so they read the one a task
needs instead of a reading list.

```yaml
---
description: Session lifecycle, expiry and refresh rules     # one line, at most 150 characters
read_when: changing auth, sessions, tokens or middleware      # the tasks that need it, not keywords
governs: [src/auth/**, src/middleware/session.*]              # optional: the code it describes
reviewed: 2026-11-08                                          # needed with governs
---
```

| What | How |
|---|---|
| The index | `docs/index.md` is generated: `scripts/check-docs.sh --write`. Never edit it by hand. |
| The gate | `scripts/check.sh` fails on a doc without `description` or `read_when`, a broken relative link, or a stale index. |
| Freshness | When code a doc `governs` changed after its `reviewed` date, the gate prints a WARN line (never a failure). Check the doc against the code, fix it, and move `reviewed`. |
| In qsh | The workspace plugin lists the docs (description, read when) in the chat's first message, and the first time the agent touches a file a doc governs it adds a one-line pointer to that doc. qsh's `/garden` (docs-garden plugin) asks the agent to propose fixes for stale docs. |
| Elsewhere | Claude Code, Codex and Antigravity see the index like any file; `AGENTS.md` points at `docs/`. |

Keep references one level deep: a doc may link to another doc, not to a chain of them. Long work
gets a plan instead (`build-notes/plans/`, skill `.agents/skills/exec-plan`).
