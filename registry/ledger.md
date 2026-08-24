---
id: registry-ledger
type: register
status: draft
description: Capability publication ledger. Use when checking versions or publication history. Not for capability behaviour (see registry/README.md).
load: drill
scope: shared
owner: shared
updated: 2026-08-24
related:
  - type: canonical
    ref: registry/README.md
---

# Registry ledger

Append-only. Newest first. Rows are never edited or deleted — a
mistaken row is corrected by a new row with action `correct` naming
the date and capability it corrects. Nothing is ever written below the
marker line.

`action` is one of: `publish` (version 1), `pack` (version bump from a
workspace), `correct`, `withdraw` (capability no longer installable;
the folder stays, the ledger says why).

`approved_by` names the human who answered `--yes`, or `n/a` when the
command needed no override.

| date | capability | version | action | files | approved_by | note |
|---|---|---|---|---|---|---|
| 2026-08-24 | example-capability | 1 | publish | 1 | n/a | worked example shipped with the template; not a real capability |

<!-- ledger: append above this line -->
