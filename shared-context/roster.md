---
id: commons-roster
type: register
status: draft
description: Linked-workspace roster. Use when linking or unlinking a workspace. Not for edit governance (see _meta/governance.md).
scope: shared
owner: shared
updated: 2026-08-24
tokens: true
related:
  - type: depends_on
    ref: shared-context/_meta/governance.md
---

# Roster

The roster is the quorum. A structural change to this store needs
sign-off from **every** row below; a workspace absent from this table
has no vote, no write access, and no claim to refreshed shared truth.

## The link-in contract

A workspace joins by accepting all five clauses. Linking without them
is not linking.

1. **Registration.** The workspace appears as a row below, with a
   stable id and its absolute path.
2. **Path plus bounded view.** The workspace stores
   `<<SHARED_CONTEXT_PATH>>` in its seam. Explicit refreshes distil approved
   truth into local `70_seams/SHARED.md`; no other content is copied.
3. **Boot boundary.** Ordinary boot reads only that compact local view, never
   this store.
4. **Precedence.** Shared outranks local on shared-scope content only.
   The workspace keeps full authority over its own runs, intents, and
   project state.
5. **Read as data, correct by candidate.** The workspace reads fixed
   paths here and executes nothing. New observations about the
   principal become correction candidates in
   [`calibration/`](calibration/README.md) — never silent local
   overrides, never direct edits to `identity/` or
   `operating-rules/`.

## Linked workspaces

| id | absolute path | linked | last sign-off | state |
|---|---|---|---|---|
| `<<WORKSPACE_ID>>` | `<<WORKSPACE_PATH>>` | YYYY-MM-DD | YYYY-MM-DD | active |

<!-- newest first — new rows go directly below the header row -->
<!-- ledger: append above this line -->

`state` is `active` (signs off, may refresh) or `dormant` (still
linked, excluded from quorum by an `overridden` trailer naming it).
Dormancy is a principal call, not a workspace's — a workspace that
stops answering blocks structural change until the principal says
otherwise. That is the intended failure mode: fail closed.

## Unlinking

Removing a row is a structural change: trailer, window, sign-off from
the remaining rows. The unlinked workspace deletes its
`70_seams/shared-context.md` path and clears the distilled shared view.
