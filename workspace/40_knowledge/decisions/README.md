---
id: knowledge-decisions
type: doctrine
status: draft
description: Settled decision records. Use when a consequential choice has been made. Not for pending choices (see workspace/50_registers/decision-queue.md).
scope: workspace
owner: human
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/40_knowledge/INDEX.md
  - type: composes_with
    ref: _templates/README.md
  - type: contrast_with
    ref: workspace/30_memory/dead-ends/README.md
---

# decisions/ — the atom of institutional trust

One monotonic, never-reused `NNNN-slug.md`, `type: decision`; the sole numeric
filename exception. Copy the `_templates/` decision kit.

Fields the kit carries: **context** (what forced a choice) ·
**options** (what was actually considered, including the ones
rejected) · **choice** · **rationale** · **scope** (what this binds) ·
**date** · **decided_by** · **status**.

## Supersede-only

Never edit accepted records. Changed choice creates a new record with
`supersedes`; demote, link, and retain the old unchanged. Bad outcomes append to
journal and may trigger supersession. Wider scope is a new decision.

## Who writes, who accepts

Agents propose `draft` + `agent_proposed` with a Decision Packet. Humans accept,
promote, and set `decided_by`. Minimum class B; constitution, boundaries, or
external effects are C.

## Wiring

- The run that produced the decision cites its id; the decision cites
  the run.
- A decision that required an approval cites the approval file in
  `80_governance/approvals/` — the approval binds the packet's content,
  so the decision must be the content that was approved.
- A decision that closes an open loop names it; the loop is closed in
  `50_registers/open-loops.md` with the decision id.
- A decision that rules an approach out cites the dead-end file, or
  creates one.
