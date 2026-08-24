---
id: kit-board
type: template
status: mature
description: Board kit. Use when a session needs a current-state view. Not for append-only event history (see workspace/30_memory/journal/README.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: contrast_with
    ref: _templates/decision.md
---

# Kit — board

**Copy to:** `workspace/50_registers/boards/{{BOARD_SLUG}}.md`
**Markers:** `{{BOARD_SLUG}}` `{{BOARD_NAME}}` `{{TODAY}}`

A board is rewritable current state; history stays in journal/source register.

```markdown
---
id: board-{{BOARD_SLUG}}
type: board
status: draft
description: >
  {{BOARD_NAME}} — open items and what each waits on. Use when
  reviewing state or closing a session. Not for how they got here
  (see workspace/30_memory/journal/README.md).
scope: workspace
load: cue
owner: human
updated: {{TODAY}}
related:
  - type: canonical
    ref: workspace/50_registers/INDEX.md
---

# {{BOARD_NAME}}

**Rewritten in place; journal every change. Journal wins conflicts.**

## Open

Newest first; every item has a default.

| id | item | waiting on | default if unanswered | since |
|---|---|---|---|---|
| {{BOARD_SLUG}}-001 | <the question or loop, one line> | human | <what happens by default> | {{TODAY}} |
| {{BOARD_SLUG}}-002 | <...> | <external system> | <...> | <date> |

## Waiting on a human

Human-answer items cite their packet; continue other work.

| id | packet | asked | expires |
|---|---|---|---|
| {{BOARD_SLUG}}-001 | `50_registers/decision-queue.md#DP-<id>` | {{TODAY}} | <date> |

## Closed since last review

Clear each review; journal retains history.

| id | item | resolution | closed |
|---|---|---|---|
| {{BOARD_SLUG}}-000 | <item> | <one line> | <date> |

## Review

Reviewed {{TODAY}}. Next review <date>. An item open past its expiry
without an answer takes its default and is closed with that noted.
```

## Rules

- Mint ids once; never reuse them.
- Journal every mutation in the same session; the board is only a view.
- Every open item states its default.
