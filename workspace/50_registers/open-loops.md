---
id: register-open-loops
type: register
status: draft
description: Open-question register. Use when work must proceed around an unknown. Not for approval-bound actions (see decision-queue.md).
scope: workspace
owner: agent
updated: 2026-08-24
related:
  - type: contrast_with
    ref: workspace/50_registers/decision-queue.md
---

# Open loops

An open loop is a question the work depends on, that nobody can answer
right now, and that would otherwise be silently resolved by whatever
the agent happened to assume. Writing it down converts an invisible
assumption into a visible, dated, revisable one.

## The rule: no loop without a default

Every row states the default **already applied**. There is no such
thing as an open loop that pauses work:

- If a safe default exists, apply it and record it.
- If no safe default exists, the default is "do nothing on this path"
  and the row also gets a Decision Packet in
  [decision-queue.md](decision-queue.md).

The row is honest about consequence: `if wrong` names what has to be
undone when the answer arrives and contradicts the default.

## Row fields

| Field | Rule |
|---|---|
| **id** | `OL-YYYY-NNN`, stable forever. |
| **opened** | ISO date the loop was first recorded. |
| **question** | One line, answerable. "Which mailbox is canonical?" not "email is unclear". |
| **default applied** | What the agent is doing meanwhile. Present tense, in force now. |
| **if wrong** | What must be undone or redone when the answer contradicts the default. |
| **revisit** | ISO date. A loop with no revisit date is a loop that will be forgotten. |
| **state** | `open` · `answered` · `ratified` (default confirmed as the answer) · `superseded` |

## Closing a loop

Append a new row with the same question and state `answered` or
`ratified`, naming the id it supersedes and the source of the answer
(a journal entry, an approval, a decision record). If the answer
changes durable behaviour, it becomes a memory promotion candidate or
a decision record — the loop row is the receipt, not the home.

## Ledger

Newest first. Append new rows directly above the marker.

| id | opened | question | default applied | if wrong | revisit | state |
|---|---|---|---|---|---|---|

<!-- ledger: append above this line -->
