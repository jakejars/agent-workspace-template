---
id: kit-run
type: template
status: mature
description: Kit for a run folder. Use when starting any session of work that will change something. Not for what is wanted (see ../intent.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: composes_with
    ref: _templates/handover.md
---

# Kit — run

**Copy to:** `workspace/90_runs/{{RUN_ID}}/run.md`
**Run id:** `YYYY-MM-DD-{{SLUG}}`, minted at start, never reused.
**Markers:** `{{HHMM}}` `{{INTENT_SLUG}}` `{{RUN_ID}}` `{{TODAY}}`

Folder: `run.md`, optional continuing-work `handover.md`, evidence artifacts.

```markdown
---
id: run-{{RUN_ID}}
type: run
status: draft
description: >
  Run against {{INTENT_SLUG}} — <outcome in five words>. Use when
  tracing what was done. Not for the intent itself (see
  workspace/20_intent/active/{{INTENT_SLUG}}.md).
scope: run:{{RUN_ID}}
load: drill
owner: agent
updated: {{TODAY}}
related:
  - type: canonical
    ref: workspace/20_intent/active/{{INTENT_SLUG}}.md
---

# Run {{RUN_ID}}

**Intent:** `intent-{{INTENT_SLUG}}` · **Started:** {{TODAY}}
**Outcome:** in progress | satisfied | blocked | abandoned

## Context loaded

Log loaded and deliberately excluded context.

- Boot set: workspace entrance, compact shared view, selected handover
- Loaded on cue: <file> · <file>
- Excluded despite matching: <file> — <why>

## Actions

Append during work; never rewrite.

| time | action | class | effect |
|---|---|---|---|
| HH:MM | <what was done> | A | <what changed, or "read only"> |
| HH:MM | <what was done> | B | approval `80_governance/approvals/<id>.md` |

## Approvals used

Each class B/C effect cites approval, scope, and expiry.

- `<approval-id>` — <what it permits> — expires <date>

## Evidence

Produced artifacts by path.

- `<path>` — <what it shows>

## Outcome

Evaluate each intent criterion.

- [x] <criterion> — met, see <evidence>
- [ ] <criterion> — not met, because <reason>

## Spawned

New durable records:

- Journal: `30_memory/journal/{{TODAY}}-{{HHMM}}-<slug>.md`
- Open loops: <ref or "none">
- Decisions: <ref or "none">
- Handover: `90_runs/{{RUN_ID}}/handover.md` or "none — work complete"
```

## Rules

- One intent per run. Log work as it happens.
- After a terminal outcome, append corrections to the journal; do not edit.
