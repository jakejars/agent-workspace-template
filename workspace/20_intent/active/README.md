---
id: intent-active
type: register
status: draft
description: Active intents. Use when recording or reviewing current wants. Not for completed intents (see ../satisfied/README.md).
scope: workspace
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/20_intent/INDEX.md
---

# active/ — what is open

**This folder is the enumeration.** "What is open?" is answered by
listing it, never by remembering. An intent that is live and not here
does not exist; an intent that is here and dead is a lie the next
session will act on.

## Adding one

1. Copy the intent kit from `_templates/` to
   `active/<slug>.md` — a short, stable, kebab-case slug.
2. Fill the four sections the kit requires: **objective**,
   **constraints**, **success definition**, **delegation deltas**.
3. Set `lifecycle: captured`. Capture first, clarify second — a want
   half-written here beats a want remembered nowhere.
4. Capture the current checkpoint. Journal only if the event needs a durable audit trail.

## Working one

- Move it up the lifecycle in `../INDEX.md` one state at a time, and
  recording explicit authorization already supplied by the principal; never invent approval.
- Runs cite it by id, in their frontmatter. The intent does not list
  its runs — that link is one-directional, and `check_loop` walks it
  from the run.
- Decisions taken along the way go to `40_knowledge/decisions/`.
  Questions that must not vanish go to `50_registers/open-loops.md`
  with a default already applied.
- Editing the objective of an `approved` intent drops it back to
  `clarified`. Approval binds content.

## Closing one

When it reaches `satisfied`, `abandoned`, or `superseded`: set
`lifecycle:`, name the evidence or the reason, `git mv` the file to
`../satisfied/`, and record the outcome and evidence in its checkpoint. The move is the record; do not
delete, do not rewrite history in place.

## Hygiene

Every intent carries `review_after`. An intent nobody has touched past
its date is either dead or being avoided — both are findings. The
staleness list surfaces them; a human decides which.

<!-- lists: *.md -->

The current checkpoint is replaceable working state. Historical handovers
never choose this task for a new session. Select it explicitly by ID.
