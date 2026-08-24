---
id: knowledge-canon
type: doctrine
status: draft
description: Canonical workspace knowledge. Use when citing settled truth. Not for candidate memory (see workspace/30_memory/INDEX.md).
scope: workspace
owner: human
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/40_knowledge/INDEX.md
  - type: depends_on
    ref: workspace/30_memory/facts/README.md
---

# canon/ — mature knowledge only

One file per subject: `<slug>.md`, `type: knowledge`. Canon is small
by construction. If everything is canon, citing canon means nothing.

## Admission

A file enters canon only when all of these hold:

1. `status: mature` — it has been used, and using it did not reveal
   it was wrong.
2. It was **promoted**, not written here. Canon is the destination of
   the ladder in `40_knowledge/INDEX.md`, never the first home of a
   thought. `provenance: promoted`, with the promoting human recorded.
3. Its support survives the trip: the journal entries, facts, or
   decisions it rests on are cited by `related` refs and still resolve.
4. It carries a `review_after` date. Mature is a claim about now.
5. It is one subject. A canon file that needs a table of contents is
   two canon files behind an INDEX (`doctrine/frontmatter-spec.md`,
   rule 7).

An agent may propose promotion — that is a Decision Packet in
`50_registers/decision-queue.md`, Class B — and may never perform one.
`owner: human` on this sub-chamber is literal.

## Mutation rule

Canon is edited only to stay true to what it already asserts:
clarification, a refreshed `review_after`, a corrected link. Any
change to what it claims is a **supersession** — a new file with
`supersedes: <old-id>` and the old one demoted to `status: draft`, so
that anything citing the old id still lands somewhere honest.

Demotion is normal and is not a failure. Knowledge that stops being
true drops out of canon; that is the mechanism working. The journal
entry recording the demotion says why.

## Citation contract

- `mature` canon may be quoted flat, with the id.
- `draft` (demoted or newly written) is cited with the caveat attached.
- Canon never cites an unpromoted memory candidate as support. If the
  support is still `agent_proposed`, the canon file is premature.
- Canon never mirrors an external source. Point at it through
  `40_knowledge/references/` and state here only what this workspace
  has verified for itself.
