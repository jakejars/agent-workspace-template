---
id: intent-index
type: doctrine
status: draft
description: Intent chamber map. Use when capturing or checking authorised work. Not for standing rules (see workspace/80_governance/policies.md).
scope: workspace
updated: 2026-10-07
related:
  - type: canonical
    ref: workspace/AGENTS.md
  - type: composes_with
    ref: workspace/20_intent/active/README.md
fields:
  - name: lifecycle
    values: [captured, clarified, approved, delegated, satisfied, abandoned, superseded]
    for: intent
    required: true
  - name: superseded_by
    for: intent
---

# 20_intent — what is wanted

One wanted outcome, its bounds, and its falsifiable completion per file. Optional runs
cite intents; each intent contains its own current checkpoint.

| Where | Holds |
|---|---|
| [`active/`](active/README.md) | Every intent that has not reached a terminal state. This folder **is** the answer to "what is open?" |
| [`satisfied/`](satisfied/README.md) | Every intent that has. Named for the common case; also holds abandoned and superseded |

Copy the `_templates/` intent kit; do not hand-roll.

## The lifecycle

```text
captured ─► clarified ─► approved ─► delegated ─► satisfied
                                          └────► abandoned
                                          └────► superseded
```

| State | What is true | Who moves it |
|---|---|---|
| `captured` | principal's words; authorization follows the actual request | anyone |
| `clarified` | objective, bounds, falsifiable success; ambiguities resolved or defaulted open loops | agent + principal |
| `approved` | principal approves current content/scope; material edits revert to clarified | principal |
| `delegated` | citing run exists; authority deltas recorded | agent |
| `satisfied` | success met; evidence named | agent verifies requested criteria and records evidence |
| `abandoned` | deliberately dropped with reason | principal |
| `superseded` | replacement named in `superseded_by` | principal |

Terminal records move from `active/` to `satisfied/` with lifecycle intact;
never delete.

## Rules

1. Link standing identity/preferences/policies/boundaries; do not embed them.
2. Keep unfalsifiable success in `clarified`.
3. `status` is trust; `lifecycle` is process state.
4. Each run cites exactly one intent; capture non-housekeeping work first.
   Onboarding's required first intent is the user's first real objective, not
   a "set up the workspace" task; setup housekeeping never becomes the first intent.
5. Approval binds content and scope at approval time; widening needs approval.
6. Record terminal state and evidence/reason in the checkpoint. Journal consequential outcomes or audit-profile work.
