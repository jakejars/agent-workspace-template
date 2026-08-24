---
id: governance-approvals
type: doctrine
status: draft
description: Approval record contract. Use when recording or checking human approval. Not for framing the request (see workspace/50_registers/decision-queue.md).
scope: workspace
owner: human
precedence: protected
updated: 2026-08-24
related:
  - type: composes_with
    ref: workspace/50_registers/decision-queue.md
---

# Approvals

One `YYYY-MM-DD-<packet-id>.md` per human answer. It binds only the packet's exact
action; no matching file means no approval.

## Record format

```yaml
---
id: approval-2026-001
type: approval
status: mature
description: >
  Approval of <action, restated in one line>. Use when checking whether
  <action> is covered. Not for <the adjacent thing it does not cover>.
scope: run:<id> | project:<slug> | workspace
what: <the exact action, copied verbatim from the packet>
packet: 50_registers/decision-queue.md#DP-2026-001
class: B | C
granted_by: <the human, named>
granted: 2026-08-24
expiry: 2026-09-24
conditions: <any preconditions that must hold at execution time>
updated: 2026-08-24
---
```

## Binding fields

| Field | Rule |
|---|---|
| **what** | packet action verbatim |
| **packet** | exactly one Decision Packet |
| **scope** | precise bound; single-use unless stated otherwise |
| **granted_by** | A named human. An agent never appears here. |
| **expiry** | required; expiry authorizes nothing |

## Rules

1. Withdraw by superseding record; retain old.
2. Action edits void approval and require a new packet.
3. One instance unless scope explicitly counts or stands until expiry.
4. Class B/C effects cite the approval in the run log.
5. Silence/default expiry never grants approval.

## Files here

Use `_templates/approval.md`; records are pattern-covered.

<!-- lists: *.md -->
