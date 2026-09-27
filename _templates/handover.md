---
id: kit-handover
type: template
status: mature
description: Kit for a handover. Use when a session ends with work still open. Not for the record of what was done (see _templates/run/README.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: composes_with
    ref: _templates/run/README.md
---

# Kit — handover

**Copy to:** `workspace/90_runs/{{RUN_ID}}/handover.md`
**Markers:** `{{RUN_ID}}` `{{INTENT_SLUG}}` `{{TODAY}}` `{{CLOSED_AT}}`

```markdown
---
id: handover-{{RUN_ID}}
type: handover
status: draft
description: >
  Handover from {{RUN_ID}} — <where the work stopped>. Use when
  picking up {{INTENT_SLUG}}. Not for the run record (see run.md).
scope: run:{{RUN_ID}}
load: cue
owner: agent
updated: {{TODAY}}
closed_at: {{CLOSED_AT}}
related:
  - type: canonical
    ref: workspace/90_runs/{{RUN_ID}}/run.md
---

# Handover — {{RUN_ID}}

**Claims, not ground truth. Re-verify before acting.**

## Start here

<Single next command/file/step; no decision required.>

## State

<Present state; 3–4 lines.>

- Done: <what is finished and verified>
- In flight: <what is half-done, and which half>
- Not started: <what remains of the intent>

## Re-verify before continuing

Run first; detect stale state.

| Check | Expected | If it differs |
|---|---|---|
| `<command>` | <what you should see> | <what it means, what to do> |
| `<file exists / state>` | <expected> | <...> |

## Blocked on

<Blocker + owner. Human blockers must cite a queued packet with an applied
default.>

- <blocker> — waiting on <human | external system> — packet `<ref>`

## Traps

<Near/failures. Link confirmed dead ends; do not restate.>

- <trap>

## Open threads

Newest-first non-blockers. Durable items must cite `50_registers/open-loops.md`.

- <thread>
```

## Rules

- Write before close validation; maximum 3,000 characters.
- Claims require the re-verification block.
- One per run; historical evidence only. Select current task context explicitly.
