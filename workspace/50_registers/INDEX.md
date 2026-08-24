---
id: registers-index
type: register
status: draft
description: Registers chamber map. Use when routing unresolved state. Not for settled rulings (see workspace/40_knowledge/decisions/README.md).
scope: workspace
owner: agent
updated: 2026-08-24
---

# 50_registers — what is still open

Registers hold unresolved state, remain append-only, and never load at ordinary
boot; a handover points to required rows.

## The four registers

| File | Holds | Closed by |
|---|---|---|
| [decision-queue.md](decision-queue.md) | Decision Packets: prepared decisions awaiting a human answer | An approval record in `../80_governance/approvals/` |
| [open-loops.md](open-loops.md) | Questions that cannot vanish, each with a default already applied | The question being answered, or the default being ratified |
| [tensions.md](tensions.md) | Cross-cutting contradictions between two positions both asserted somewhere | A decision record in `../40_knowledge/decisions/` |
| [risks.md](risks.md) | Known exposures being carried, with the mitigation in force | The risk retiring, or converting into a decision packet |

Mutable computed boards use `boards/` and `_templates/board.md`; they may rewrite
in place and are pattern-covered.

<!-- lists: boards/*.md -->

## Conventions all four share

1. Append newest rows above the ledger marker; corrections supersede by new row.
2. Every row has stable prefixed id, date, and state.
3. Blocking rows apply a reversible default immediately; otherwise default to
   no action and class B/C.
4. Keep rows terse; narrative belongs in journal/run evidence.

## Where rows come from

```text
work blocked by a consequential action ──► decision-queue.md (packet)
work blocked by an unanswered question ──► open-loops.md (+ default)
two sources disagree ────────────────────► tensions.md
something could go wrong and is accepted ► risks.md
```

Anything else is a journal event.
