---
id: memory-index
type: doctrine
status: draft
description: Memory chamber map. Use when capturing events or promoting memory. Not for system flows (see LOOP.md).
scope: workspace
owner: agent
updated: 2026-09-06
related:
  - type: canonical
    ref: LOOP.md
  - type: composes_with
    ref: workspace/40_knowledge/INDEX.md
---

# Memory

Memory holds evidence and reusable context. A task's latest working state lives
in its active intent record; journals and old runs are history.

| Kind | Home | Use |
|---|---|---|
| Historical event | [journal/](journal/README.md) | Immutable record; correct with a new entry |
| Fact | [facts/](facts/README.md) | Evidence, scope, verification date, expiry |
| Preference | [preferences/](preferences/README.md) | Human-directed standing preference |
| Procedure | [procedures/](procedures/README.md) | Reusable sequence with verification |
| Failed approach | [dead-ends/](dead-ends/README.md) | Evidence and explicit reopening conditions |

## Evidence is not authority

A journal establishes what was recorded, not that its claim is correct or
current. On disagreement, compare sources, scope, verification, and corrections.
An older observation does not override a current verified fact or the user's
explicit correction. Shared facts have precedence only within their shared
scope and remain subject to current evidence.

Agents may use `agent_proposed` factual evidence provisionally with the caveat
and re-verification visible. This never promotes policy, preferences, or
permissions. Human promotion grants standing authority; agents never promote
their own instructions. `mature` still excludes `agent_proposed`.

Expired and superseded candidates remain reachable evidence but leave ordinary
cue suggestions. Query history deliberately if needed. No background process
silently deletes or promotes records.

For ordinary work, update one task checkpoint. Journal only events whose
history matters; use detailed run logs when audit requirements justify them.
