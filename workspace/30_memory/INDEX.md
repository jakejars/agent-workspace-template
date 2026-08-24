---
id: memory-index
type: doctrine
status: draft
description: Memory chamber map. Use when capturing events or promoting memory. Not for system flows (see LOOP.md).
scope: workspace
owner: agent
updated: 2026-08-24
related:
  - type: canonical
    ref: LOOP.md
  - type: composes_with
    ref: workspace/40_knowledge/INDEX.md
---

# 30_memory — what this workspace remembers

## The loop, in ten lines

```text
1  anything worth keeping        → journal/ (append, ceremony-free)
2  journal entries are immutable → a correction is a new entry
3  a pattern recurs              → an agent proposes a promotion
4  proposals land in facts/, preferences/, procedures/, dead-ends/
5  every proposal is provenance: agent_proposed — never load-bearing
6  a human promotes              → provenance: promoted, status may rise
7  promoted preferences are routed on cue; compact standing rules live in SHARED
8  promoted facts and procedures are cited, not re-derived
9  dead-ends stop the next agent re-walking a path already proven dead
10 unpromoted candidates expire; journal entries never do
```

Full spec: `LOOP.md` §2 (repo root). Knowledge that matures past
memory is promoted again, into `40_knowledge/canon/`.

## The five kinds

| Kind | Lives in | Mutation rule |
|---|---|---|
| Event | [`journal/`](journal/README.md) | Append-only. Never edited, moved, or deleted. |
| Fact | [`facts/`](facts/README.md) | Needs provenance; superseded by a new fact, never edited in place. |
| Preference | [`preferences/`](preferences/README.md) | Scoped, carries confidence and the rule that produced it. |
| Procedure | [`procedures/`](procedures/README.md) | Versioned like code: bump, changelog, keep the old version readable. |
| Dead end | [`dead-ends/`](dead-ends/README.md) | Verified-on date; re-opened only by a new verification. |

## Two laws

1. **The journal is truth; everything else is a projection.** On
   conflict, the journal entry wins and the projection is wrong.
2. **Promotion is a human act.** An agent proposes with
   `provenance: agent_proposed`; it never flips its own provenance.
   Class B — see `80_governance/autonomy.md`.

Observations about the principal are shared-scope: they become
correction candidates for the commons via `70_seams/shared-context.md`,
not local memory. Local memory holds what is true of *this workspace's
work*.
