---
id: capabilities-installed
type: capability
status: draft
description: Capability lockfile. Use when invoking, installing, or updating a capability. Not for registry crossing rules (see workspace/70_seams/registry.md).
scope: workspace
owner: agent
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/60_capabilities/INDEX.md
  - type: depends_on
    ref: workspace/70_seams/registry.md
---

# Installed capabilities (lockfile)

This file is the answer to "what is actually here, and can I trust
it?". It is a ledger, not a config: nothing reads it to decide
behaviour, but nothing is believed about a capability that this file
does not say.

## Row fields

| Field | Rule |
|---|---|
| **capability** | The stable capability name, not a filename. |
| **version** | Integer, monotonic, from the source manifest. `local` sources start at 1. |
| **sha256** | Of the installed payload, verified at install time against the manifest. Truncate to 12 chars in the table; the full digest lives in the manifest. |
| **source** | `registry` or `local`. |
| **installed** | ISO date of this row's event. |
| **trust** | `untrusted` · `probationary` · `trusted` · `withdrawn` (ladder in [INDEX.md](INDEX.md)). |
| **approval** | Ref into `../80_governance/approvals/` for anything above `untrusted`. Blank is only valid for `untrusted`. |

## Events that append a row

- **install** — first arrival. Always `trust: untrusted`.
- **update** — new version installed; new row, new checksum, trust
  resets to `untrusted` unless the approval explicitly covers future
  versions.
- **promote / demote** — trust state change, with approval ref.
- **withdraw** — trust revoked or files removed.
- **verify** — a drift check that found a mismatch; the row records
  what was found, and the capability is treated as `untrusted` until
  reinstalled.

A row is never edited. State is read as "the newest row for that
capability name".

## Drift

Recorded checksum versus checksum on disk is the whole drift test. A
file that differs from its row was changed outside the install path:
either pack the improvement back through the registry seam (version
bump, new row) or restore it. Silent local edits to installed
capabilities are how a supply chain stops being one.

## Ledger

Newest first. Append new rows directly above the marker.

| capability | version | sha256 | source | installed | trust | approval |
|---|---|---|---|---|---|---|

<!-- ledger: append above this line -->
