---
id: governance-policies
type: policy
status: draft
description: The class-A allowlist. Use when checking whether an action is pre-cleared, before taking it. Not for how classes are decided (see autonomy.md).
scope: workspace
owner: human
provenance: authored
precedence: protected
updated: 2026-08-24
related:
  - type: depends_on
    ref: workspace/80_governance/autonomy.md
---

# Policies

Class A is this closed allowlist; absence means B. Additions require a bounded
proposal.

## Class-A allowlist (starter set)

| # | Permitted without asking | Bound by |
|---|---|---|
| A1 | Read any file in this workspace, respecting `load:` tiers | Never bulk-read `drill` files; follow links, do not sweep folders |
| A2 | Append entries to `30_memory/journal/` | Append only; never edit, move, or delete an existing entry |
| A3 | Create and edit files in `20_intent/`, `40_knowledge/` (non-decision), and `90_runs/` for the current run | Own run only; decision records are class B |
| A4 | Add rows to any register in `50_registers/` | Append above the marker; never rewrite a row |
| A5 | Apply a default recorded in `open-loops.md` and continue | The default must be reversible and already written down |
| A6 | Write memory candidates with `provenance: agent_proposed` | Never flip provenance; candidates are never load-bearing |
| A7 | Run read-only tooling: catalog rebuild, validators, loop check, staleness sweep | Read-only; a failing gate is a stop, not a suggestion |
| A8 | Move a file within the workspace per the filing ladder | Ids are stable; a move is never a rewrite |
| A9 | Produce drafts of anything — messages, posts, commits, patches | Producing is class A; **sending, publishing, or committing is not** |
| A10 | Read a seam file and act within a seam already marked open | An unopened seam is a closed seam |

## Standing rules

1. Journal every class-A file change.
2. Undo must be one local step.
3. Seam crossings classify separately.
4. Drafting is A; sending is C.
5. Volume/repetition never upgrades permission.
6. Additions are class-B packets; removals take effect immediately.
