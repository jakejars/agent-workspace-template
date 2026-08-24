---
id: governance-autonomy
type: policy
status: draft
description: The full autonomy table. Use when classifying any action before taking it. Not for the list of pre-cleared class-A actions (see policies.md).
scope: workspace
owner: human
provenance: authored
precedence: protected
updated: 2026-08-24
related:
  - type: composes_with
    ref: workspace/80_governance/policies.md
---

# Autonomy classes

Classify by undo path, not importance, cost, or confidence.

| | Class A | Class B | Class C |
|---|---|---|---|
| **Test** | Fully reversible inside this workspace, by the agent, in one step | Reversible, but not by the agent alone — or it changes what future sessions believe | Irreversible, externally visible, or constitutional |
| **Who acts** | Agent, immediately | Agent proposes, human disposes | Human decides through a named ritual |
| **Record** | Journal entry | Decision Packet → approval record | Decision Packet → approval record, plus an entry in the run log naming it |
| **Blocked?** | No | Not blocked — file the packet, apply the default, continue other work | Yes. Blocked until the approval exists |
| **Undo cost** | An edit | A human's attention | Cannot be undone, only compensated |

## Class A — proceed and log

Proceed only under the exact [policies allowlist](policies.md): undoable by one
local edit with no external observer.

## Class B — propose, human disposes

- promotion; commons edits; capability install/update/trust/pack;
- human-owned edits; rulings/decisions; non-effect seam opening;
- high-impact risk acceptance; any uncertain classification.

File a packet, apply its default, continue other work.

## Class C — never without ritual

- external send/publish/pay/sign;
- principal-data deletion or journal mutation;
- constitution or [boundaries](boundaries.md) change;
- opening a [`world`](../70_seams/world.md) destination;
- anything only compensable, not undoable.

Require exact packet, scoped/expiring human approval, and run-log citation. No
current approval, no effect; single-use unless scoped otherwise.

## Escalation and its absence

Escalation is allowed; de-escalation, repetition, and volume never lower class.
