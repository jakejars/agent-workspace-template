---
id: memory-dead-ends
type: doctrine
status: draft
description: Verified dead ends. Use when reconsidering a failed approach. Not for choices between live options (see workspace/40_knowledge/decisions/README.md).
scope: workspace
owner: agent
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/30_memory/INDEX.md
  - type: composes_with
    ref: workspace/40_knowledge/decisions/README.md
fields:
  - name: tried
    for: dead-end
    required: true
  - name: why_dead
    for: dead-end
    required: true
  - name: verified_on
    kind: date
    for: dead-end
    required: true
  - name: verified_by
    values: [human, agent]
    for: dead-end
    required: true
  - name: bounds
    for: dead-end
    required: true
  - name: support
    kind: list
    for: dead-end
    required: true
  - name: reopen_if
    for: dead-end
    required: true
---

# dead-ends/ — what not to try again

One verified failure per `<slug>.md`, `type: dead-end`.

## Required beyond the OKF core

```yaml
tried: <what was actually attempted>
why_dead: <the mechanism, not the mood>
verified_on: YYYY-MM-DD
verified_by: human | agent
bounds: <version / platform / contract the verdict holds under>
support:                          # the journal entries that show it
  - 30_memory/journal/2026-08-21-1105-headless-capture-blocked.md
reopen_if: <what would make this worth retrying>
```

- `tried`: recognizable concrete approach.
- `why_dead`: mechanism, not tuning symptom.
- `verified_on` + `bounds`: conditions under which the verdict holds.
- `reopen_if`: reopening condition or `nothing — structural`.

## Mutation rule

Re-verify, never delete. Reopened paths create a draft superseding dead-end or a
decision citing the prior verdict.

## When to write one

File immediately on proof (Class A), then continue. Agent records remain
`agent_proposed` until promoted.

Agent-proposed factual evidence may guide reversible work provisionally after
checking its source, scope, and freshness. It grants no policy or permissions.
Human promotion remains required for standing authority and mature status.
