---
id: register-tensions
type: register
status: draft
description: Cross-source tensions. Use when credible sources conflict. Not for one unanswered question (see open-loops.md).
scope: workspace
owner: agent
updated: 2026-08-24
related:
  - type: contrast_with
    ref: workspace/50_registers/open-loops.md
---

# Tensions

A tension is not a bug and not a question. It is two positions, each
asserted with authority somewhere the agent can reach, that cannot
both govern the same case. Left unrecorded, the winner is whichever
file loaded first — which makes behaviour depend on load order rather
than on doctrine.

## When to file one

- Two sources in scope disagree (commons vs local, policy vs
  procedure, one seam file vs another).
- A rule is stated in two places with different edges.
- The same term means different things in two chambers.

Not a tension: a source being merely stale (refresh it), or a source
being wrong with the correct answer known (correct it, append a
journal entry).

## Row fields

| Field | Rule |
|---|---|
| **id** | `TN-YYYY-NNN`, stable forever. |
| **opened** | ISO date. |
| **tension** | One line naming the incompatibility, not one side of it. |
| **position A / where** | The claim and the file that asserts it. |
| **position B / where** | The rival claim and the file that asserts it. |
| **tie-break in force** | Which side the agent is currently following, and why. Never blank — if nothing is chosen, precedence rules in `doctrine/` decide, and that is the entry. |
| **state** | `open` · `ruled` · `dissolved` (the conflict stopped existing) · `superseded` |

## How a tension closes

A ruling, not an argument. The resolution lands as a decision record
in `../40_knowledge/decisions/` (supersede-only, human-accepted); the
tension row is then superseded by a new row in state `ruled` that
names the decision. If the ruling changes what is loaded at boot, it
also changes the source files — a ruling that only lives in this
ledger has not been applied.

Rulings are class B: the agent frames the tension and proposes; the
human rules.

## Ledger

Newest first. Append new rows directly above the marker.

| id | opened | tension | A (where) | B (where) | tie-break in force | state |
|---|---|---|---|---|---|---|

<!-- ledger: append above this line -->
