---
id: filing
type: doctrine
status: draft
description: Deterministic filing. Use when you have something to write down and do not know where it goes. Not for what the frontmatter must say (see doctrine/frontmatter-spec.md).
updated: 2026-10-07
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: see_also
    ref: doctrine/naming.md
---

# Filing

Choose `type`; [`schema.json`](schema.json) selects the path and validates it.
This file defines semantics and edge cases, not a duplicate map.

## Type → chamber

See `filing` in [`schema.json`](schema.json).

## The universal types

- `doctrine`: directory door (`INDEX.md` or subtree `README.md`); contains no
  chamber knowledge.
- `register`: append-only, newest-first ledger carrying
  `<!-- ledger: append above this line -->`.

These types describe shape, not a fallback for uncertain filing.

## Bindings that are decisions, not derivations

- Journal: one `YYYY-MM-DD-HHMM-slug.md` per event, minimal
  `date`/`kind`/`refs` header, no OKF frontmatter.
- Board: human-owned rendered state in workspace or library board paths; never
  the only source of a fact.
- Registry capability files are distribution artifacts, not workspace chamber
  content; `60_capabilities/` binding applies only inside a workspace.

## Filing outside the workspace

Optional-member bindings also live in the schema. Library field/pillar/topic/
specimen are tree positions under `library/fields/`; captures move via the
library filing ladder, not `review_after`.

## The 60-second rule

After sixty seconds, file a linked `draft` in the best chamber and add the
question/default to `50_registers/open-loops.md`. Workspaces have no inbox:
reachable-and-movable beats unfiled. Move later under
[`migrations.md`](migrations.md).

## Boundary table

Decided ambiguities. Add a row when a filing question costs two agents
sixty seconds twice; never re-argue a row, supersede it.

| Ambiguity | Goes to | Because |
|---|---|---|
| Tool vs instructions | executable manifest+checksum → `capability`; performed sequence → `procedure` | distribute one; follow the other |
| Runtime-loadable behaviour | `skill` → `60_capabilities/skills/<name>/SKILL.md` | optional packaging of reused procedures; capability trust still applies |
| Principal preference | commons candidate if cross-workspace; local preference if workspace-only; identity if factual | shared truth must not become a silent local override |
| Choice | journal event; decision only if future-binding; queue if unsettled | event and authority differ |
| Failed approach | dead-end only with evidence, paid cost, and reopen condition; else journal | avoid unsupported permanent blocks |
| Reusable knowledge | workspace knowledge if local; library capture if transferable | crossing is proposal, not promotion |

## Filing is not promotion

Agent filing is `agent_proposed`; correct placement grants reachability, not
authority. Human class-B promotion makes it binding.
