---
id: register-decision-queue
type: register
status: draft
description: The Decision Packet ledger. Use when a class-B or class-C action is wanted. Not for recording the answer (see ../80_governance/approvals/).
scope: workspace
owner: agent
updated: 2026-08-24
related:
  - type: composes_with
    ref: workspace/80_governance/autonomy.md
  - type: composes_with
    ref: workspace/80_governance/approvals/README.md
---

# Decision queue

A Decision Packet makes a consequential action answerable. File it, apply its
default, and continue independent work.

## What a packet must contain

| Field | Rule |
|---|---|
| **action** | exact one-line effect, approvable verbatim |
| **class** | A, B, or C per [autonomy.md](../80_governance/autonomy.md). A packet exists because the action is not class A. |
| **evidence** | links to journal, run, or knowledge records |
| **default** | reversible option, in force from filing |
| **expiry** | date default becomes permanent and packet closes |

Optional: real `options`, `blast_radius`, `intent`.

## Packet shape

```yaml
id: DP-2026-001
opened: 2026-08-24
action: <one line, approvable verbatim>
class: B
evidence:
  - 30_memory/journal/2026-08-24-1412-forwarding-rule-proposed.md
  - 90_runs/2026-08-24-<slug>/run.md
options:
  - <option 1>
  - <option 2>
default: <the reversible option — in force from `opened`>
expiry: 2026-09-07
state: open
```

## States

`open` → `approved` · `declined` · `expired-to-default` · `superseded`

Approval binds the exact action text; changed action requires a new packet.

## Ledger

Newest first; state changes append a superseding row above the marker.

| id | opened | action | class | default in force | expiry | state |
|---|---|---|---|---|---|---|

<!-- ledger: append above this line -->
