---
id: library-filing-ladder
type: doctrine
status: draft
description: Where library material goes. Use when filing something, when two homes look plausible. Not for how much a claim weighs (see library/doctrine/claims.md).
owner: human
updated: 2026-08-24
review_after: 2027-08-24
related:
  - type: canonical
    ref: library/INDEX.md
---

# The filing ladder

File by the question answered. Past sixty seconds, use the inbox.

## The layers

| Layer | Holds | Rule |
|---|---|---|
| `NAMESPACE.md` (family root) | Every path that has a meaning | Named before the folder exists |
| `CATALOG.md` (generated) | What exists right now | Never hand-edited; route by its descriptions |
| [`inbox/`](../inbox/README.md) | Captures whose home is unclear | Under a minute, or it lands here |

Retrieve via catalog, file via namespace, defer via inbox.

## The algorithm

1. Use the primary question, not source context.
2. Prefer reusable concepts; use technology homes only when mechanics depend
   on that technology.
3. Taste is a specimen under its topic, never a one-item category.
4. Choose one canonical home; other plausible homes use `canonical` edges.
5. After sixty seconds, note candidates in `inbox/` and continue.

## The 60-second rule

> If you cannot pick a home in sixty seconds, write the capture to
> `inbox/<slug>.md` and keep working.

Library captures are uncitable until promoted and may expire; workspace content
must instead be filed wrong-but-reachable.

## The ladder

No category fits? Climb exactly one rung at a time.

### Rung 0 — capture

**Bar:** none. Copy `_templates/capture.md` to `inbox/<slug>.md`. Revisit on
decision influence, reuse, or a second related capture.

### Rung 1 — a topic inside an existing pillar

**Bar:** the pillar fits and more than one capture is expected.

1. Add the topic to `NAMESPACE.md`.
2. Copy `_templates/topic.md` to `fields/<field>/<pillar>/<topic>/README.md`.
3. Start `status: stub`; fill routed description; delete unused sections.
4. Link from the parent door; rebuild catalog and run loop check.

### Rung 2 — a pillar inside an existing field

**Bar:** three visible future topics, or repeated misfiling across two pillars.

**Recipe:**
1. Add kebab name and boundary to `NAMESPACE.md`.
2. Create a one-line reserved `type: pillar` INDEX.
3. Add a boundary row if ambiguous; seed at least one real topic.

### Rung 3 — a whole new field

**Bar:** a distinct practice domain with at least three named pillars.

Add the field to `NAMESPACE.md`; create a reserved `type: field` INDEX; seed a
real pillar/topic; add any boundary row. Commit namespace and content separately.

## Anti-rules

- **No ad-hoc directories.** The member holds `doctrine/`, `fields/`,
  `inbox/`, and `boards/`. Nothing else is a filing destination.
- **No category without a namespace entry first**, and none for a
  single capture — the inbox absorbs those.
- **No duplicate canonical homes.** Link; never copy.
- **Reserved is not content.** Scaffolding may exist; it is never cited.

## Boundaries decided once

Add a row when a filing question costs two readers sixty seconds twice.
Never re-argue a row — supersede it.

| If it is about | It goes to | Not |
|---|---|---|
| A technique general to any stack | the concept pillar | a technology pillar |
| That technique's mechanics in one stack | that stack's pillar | the concept pillar |
| An artifact to learn *from* (poster, UI, frame) | a specimen under the topic it informs | a new topic |
| A principle *implemented in code* | the pillar that implements it | the field it came from |
| A through-line across many entries | a board | a topic |
