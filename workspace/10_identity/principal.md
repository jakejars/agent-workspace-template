---
id: principal
type: identity
status: draft
description: The human this workspace serves. Use when addressing the principal, attributing work. Not for their organisation (see organisation.md).
scope: workspace
owner: human
tokens: true
updated: 2026-10-07
related:
  - type: canonical
    ref: workspace/10_identity/INDEX.md
---

# Principal

| Field | Value |
|---|---|
| Name | `<<PRINCIPAL_NAME>>` |
| Referred to as | `<<PRINCIPAL_NAME>>` in prose; "the principal" in doctrine and gate output |
| Pronouns | *unstated — use `they`* |
| Identifying address | `<<PRINCIPAL_EMAIL>>` |
| Time zone | *unfilled* |
| Working hours | *unfilled* |

## Address rules

- `<<PRINCIPAL_EMAIL>>` **identifies**; it does not authorise contact.
  Use it for attribution and for filtering the principal's own work.
  Sending to it — or including it in any outbound payload, header, or
  URL — is an external effect under constitution law 1 and needs a
  recorded approval.
- Pronouns are recorded only if the principal states them. Unstated
  means `they`. Do not infer from the name, and do not ask again once
  the field says unstated.

## Authority

The principal decides what is built. They alone may:

- promote anything from `provenance: agent_proposed` to `promoted`;
- answer a Decision Packet in `50_registers/decision-queue.md`;
- grant an approval in `80_governance/approvals/`;
- change the constitution or `80_governance/boundaries.md` (class C,
  ritual only).

Silence is not approval. An unanswered packet stays open; work routes
around it.

## What belongs here

Stable facts about the person: how to name them, how to reach them,
what they hold authority over. Everything that changes with the work —
current priorities, active projects, mood about a decision — belongs
in `20_intent/` or `50_registers/`. Taste and standing preferences
belong in `30_memory/preferences/`, promoted, not here.

Where a commons is linked, its identity record for the principal
outranks this file; this file then holds only what is local to this
workspace, and observed corrections go to the commons as candidates.

An agent may faithfully record the principal's explicit instruction or approval
and enact its authorized scope. Recording is not self-approval. Do not request
the same authorization again solely to create a record.
