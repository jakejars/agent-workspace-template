---
id: commons-governance
type: policy
status: draft
description: Commons change rules. Use when proposing, reviewing, or contesting an edit. Not for store contents (see shared-context/SHARED.md).
scope: shared
precedence: protected
owner: human
provenance: authored
updated: 2026-08-24
tokens: true
related:
  - type: canonical
    ref: shared-context/CHANGES.md
  - type: depends_on
    ref: shared-context/roster.md
---

# Governance

Edits are proposals; they bind only after the objection window.

## The window

`<<OBJECTION_WINDOW_HOURS>>` hours from the `CHANGES.md` trailer timestamp.
Untrailed edits never bind.

## States

Every trailer carries exactly one state.

| State | Meaning | Eligible for workspace refresh? |
|---|---|---|
| `open` | Window running. Edit is on disk, visible, contestable. | No — treat as `draft` regardless of frontmatter |
| `bound` | Window elapsed with no objection. The edit is canon. | Yes, when selected for the compact view |
| `objected` | A roster workspace or the principal objected inside the window. Edit is frozen at the pre-edit content until resolved. | No |
| `withdrawn` | Proposer pulled it. Reverted; trailer stays. | No |
| `overridden` | Principal bound or reverted it directly, window unspent. | If bound and selected |

States only advance; resolution creates a new trailer.

## Who may do what

| Change | Requires |
|---|---|
| Edit an `owner: shared` file (`calibration/`, `roster.md` rows) | Trailer + window |
| Edit an `owner: human` file's content (`identity/`, `operating-rules/`) | Trailer + window + human disposal of the underlying candidate |
| Add, remove, move, or rename any file | Trailer + window + sign-off from **every** workspace on `roster.md` |
| Add content to the compact workspace boot view | Same as above — it spends every session's context |
| Change `boundaries/` never-share terms, or this file | Principal only. No agent proposes here; a workspace files the concern in `calibration/` |

Record each required workspace id/date under the trailer; missing sign-off blocks.

## Objecting

Any linked workspace may append an `objected` trailer naming target and reason.
This stops the clock but preserves the proposal.

## The principal override

<<PRINCIPAL_NAME>> may bind/revert/rewrite immediately with an `overridden`
trailer. Agents never use this path.

## What this does not govern

Reading and local workspace acts. Local disagreement must be filed in
[`calibration/`](../calibration/README.md), never applied as a silent override.
