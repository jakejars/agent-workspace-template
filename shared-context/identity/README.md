---
id: commons-identity-index
type: identity
status: draft
description: Shared identity. Use when a workspace needs durable principal facts. Not for working-style rules (see shared-context/operating-rules/README.md).
scope: shared
owner: human
provenance: authored
updated: 2026-08-24
tokens: true
---

# Identity

Who <<PRINCIPAL_NAME>> is, stated once. Low churn by construction: a
fact belongs here only if it would still be true if every workspace
were deleted tomorrow.

## What files live here

One concept per file, `type: identity`, `owner: human`. The usual
shape:

| File | Holds |
|---|---|
| `principal.md` | The person: name, role, how they are addressed, standing context an agent needs before its first sentence |
| `organisation.md` | The entity: legal name, what it does, who it serves |
| `machines.md` | Named machines and what each is for — hardware truth stays in the workspace's machine seam; this is only which machines exist and their roles |
| `agents.md` | The standing agent roles this principal runs, described by function, never by vendor |

None of these are pre-created. A chamber file exists when there is
something true to put in it, and appears in the table above in the
same edit that creates it.

## Filing rules

1. **Durable or nothing.** A fact with an expiry date is not identity;
   it is workspace state.
2. **Human-owned.** An agent never writes here directly. It files a
   correction candidate in [`../calibration/README.md`](../calibration/README.md)
   and a human disposes.
3. **Sourced.** A fact carries `provenance:` — `authored` when the
   principal wrote it, `promoted` when it came up through calibration
   (naming the candidate it came from).
4. **No boundaries here.** What must not leave lives in
   [`../boundaries/README.md`](../boundaries/README.md), because that
   file is the one the scrub gate derives from. Restating a
   never-share term here creates a second copy that will drift.
5. **No secrets.** Identity is not credentials. See the law in
   [`../SHARED.md`](../SHARED.md).

## Promotion into the compact view

Identity files remain `cue`. A workspace refresh may distil a small promoted
fact into its local boot view; adding it is a structural change under
[`../_meta/governance.md`](../_meta/governance.md).
