---
id: knowledge-index
type: doctrine
status: draft
description: Knowledge chamber map. Use when locating settled knowledge. Not for raw capture (see workspace/30_memory/INDEX.md).
scope: workspace
owner: agent
updated: 2026-08-24
related:
  - type: canonical
    ref: LOOP.md
  - type: depends_on
    ref: workspace/30_memory/INDEX.md
---

# 40_knowledge — what this workspace knows

Memory is what happened and what it suggests. Knowledge is what has
survived review and may be quoted without a caveat. The chamber holds
three things, and nothing enters any of them by accident.

| Sub-chamber | Holds | Entry route |
|---|---|---|
| [`canon/`](canon/README.md) | Mature, promoted knowledge — quotable | Promotion from `30_memory/` |
| [`references/`](references/README.md) | Pointers out — provenance, nothing fetched | Filed when first cited |
| [`decisions/`](decisions/README.md) | Decision records, supersede-only | Written when a choice is made |

**The boundary with the library.** What is true of *this* workspace's
work stays here. What would help the next workspace too — a technique,
a norm, a taste reference — crosses out through
[`../70_seams/library.md`](../70_seams/library.md) as a capture, never
as a promotion: the library's own ladder decides what becomes citable
there. Knowledge only one sett holds is knowledge that rots.

## The ladder

```text
journal entry ──► facts/preferences/procedures (candidate, agent_proposed)
              ──► human promotion (provenance: promoted)
              ──► canon/ when it is mature, cited, and stable
```

Status gates citation, everywhere in this chamber: `reserved` and
`stub` are never load-bearing, `draft` carries a caveat when cited,
`mature` is quotable and is the only status permitted `load: always`.

## Decisions are the atom

Facts can be superseded by the world; preferences yield; procedures
get rewritten. A decision is the one record that says *a human chose
this, knowing these options, for these reasons, at this date* — which
is why it is supersede-only and why nothing else in the sett is
allowed to overwrite one. Institutional trust is the ability to ask
"why is it this way?" six months later and get an answer that has not
been edited since. That answer lives in `decisions/`.

Every consequential choice made during a run lands there — the run
log cites the decision id, and the decision cites the approval in
`80_governance/approvals/` when one was required.
