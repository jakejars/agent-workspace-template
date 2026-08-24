---
id: register-risks
type: register
status: draft
description: Accepted-risk register. Use when tracking exposure that remains open. Not for action approvals (see decision-queue.md).
scope: workspace
owner: agent
updated: 2026-08-24
---

# Risks

A risk row exists to make acceptance explicit. An exposure nobody
wrote down is not accepted — it is unnoticed. Filing the row is
cheap; the row's job is to come back on its review date and ask
whether the mitigation is still true.

## What belongs here

- Exposures the workspace is knowingly carrying (single copy of
  something, an unverified assumption in a live path, a capability
  installed but untrusted, a seam left open wider than needed).
- Consequences of a default in [open-loops.md](open-loops.md) that
  could cost more than the loop itself.

Not here: a risk that can be removed this session — remove it. A
theoretical risk with no reachable trigger — omit it.

## Row fields

| Field | Rule |
|---|---|
| **id** | `RK-YYYY-NNN`, stable forever. |
| **opened** | ISO date. |
| **risk** | One line: what could go wrong, and what it costs if it does. |
| **likelihood / impact** | `low` · `med` · `high` each. Two words, no scoring theatre. |
| **mitigation in force** | What is actually done today, not what is planned. "None" is a legitimate and useful entry. |
| **owner** | `human` or `agent` — who must act if it fires. |
| **review** | ISO date. Overdue rows surface with the staleness sweep. |
| **state** | `open` · `mitigated` · `accepted` (deliberately carried, no further action) · `retired` · `superseded` |

## Closing

Append a new row naming the id it supersedes. `retired` means the
exposure no longer exists; `accepted` means it does and the workspace
has decided to live with it — which is a class-B decision if the
impact is `high`, and therefore gets a Decision Packet.

## Ledger

Newest first. Append new rows directly above the marker.

| id | opened | risk | L/I | mitigation in force | owner | review | state |
|---|---|---|---|---|---|---|---|

<!-- ledger: append above this line -->
