---
id: commons-changes
type: register
status: draft
description: Commons change ledger. Use when landing or contesting an edit. Not for change rules (see _meta/governance.md).
load: drill
scope: shared
owner: shared
updated: 2026-08-24
tokens: true
related:
  - type: canonical
    ref: shared-context/_meta/governance.md
---

# CHANGES

Every edit to this store appends one trailer here. No trailer, no
edit: an unrecorded change never binds and is treated as a defect by
the next workspace that finds it.

**Append-only.** Trailers are never edited, reordered, or deleted —
not to fix a typo, not to resolve an objection, not to correct a wrong
state. A correction is a **new trailer** naming the one it corrects.
Newest first: new trailers go directly under the heading below.

## Trailer format

```text
YYYY-MM-DDTHH:MMZ | <workspace-id> | <path(s) touched> | <one-line summary> | state: open|bound|objected|withdrawn|overridden | binds: YYYY-MM-DDTHH:MMZ
  sign-off: <workspace-id> YYYY-MM-DD, <workspace-id> YYYY-MM-DD   # structural changes only
  re: <timestamp of the trailer this corrects or objects to>       # corrections and objections only
```

- **timestamp** — when the window opened, not when the file was saved.
- **workspace-id** — the id from [`roster.md`](roster.md). A workspace
  that is not on the roster does not edit this store.
- **binds** — timestamp + <<OBJECTION_WINDOW_HOURS>> hours. Fill it at
  proposal time so the deadline is a fact, not a calculation.
- **state** — one of the five in
  [`_meta/governance.md`](_meta/governance.md). Moving `open` → `bound`
  is itself an append: a new trailer, `re:` the original.

## Trailers

<!-- newest first — new trailers go directly below this comment -->

`YYYY-MM-DDTHH:MMZ | <<WORKSPACE_ID>> | SHARED.md | example trailer — delete on instantiation | state: bound | binds: YYYY-MM-DDTHH:MMZ`

<!-- ledger: append above this line -->
