---
id: library-inbox
type: doctrine
status: draft
description: The capture chamber. Use when filing takes more than sixty seconds. Not for anything citable (see library/doctrine/filing-ladder.md).
owner: human
updated: 2026-08-24
related:
  - type: canonical
    ref: library/INDEX.md
  - type: depends_on
    ref: library/doctrine/filing-ladder.md
---

# Inbox

Drop links, snippets, and half-thoughts here without ceremony. **One
file per capture**, `<slug>.md`. No classification is required at
capture time — that is the entire point.

Ceremony-free is not frontmatter-free: a capture carries the five
required OKF fields (`type: knowledge`, `status: stub`) so the catalog
can route it, and it is covered by this door's declared glob so the
loop check can reach it. An inbox nothing points at is the staging area
the family forbids.

The four prompts below the frontmatter are optional
(`_templates/capture.md`):

```text
Source:
Why I saved this:
Possible homes:
What question might this answer:
```

"Possible homes" is a guess, not a commitment. Writing "new category?"
is a legitimate answer.

## Promotion

A capture graduates into a topic when one of three things happens: it
**influences a decision**, it **gets reused**, or it **meets a second
capture** on the same subject. Then it climbs rung 1 of
[`../doctrine/filing-ladder.md`](../doctrine/filing-ladder.md) and the
capture file goes away.

Otherwise it joins a topic's `RESOURCES.md`, or it is deleted.
**Unpromoted captures expire** — that is what keeps the inbox a
staging area rather than a second library nobody promoted.

## What this chamber is not

- **Not knowledge.** Nothing here is cited, quoted as a claim, or
  treated as the library's position. Captures sit at `status: stub` and
  go no higher — the ladder starts when the material earns a topic.
- **Not reviewed.** No `review_after`, and the staleness report skips
  this chamber. A capture is promoted or dropped, never refreshed.
- **Not a filing destination for anything you already placed.** If the
  home is obvious, file it; the inbox is for the sixty-second failure,
  not for avoiding the decision.
- **Not a media store.** Collected files live under a specimen with a
  rights record (see
  [`../doctrine/media-and-rights.md`](../doctrine/media-and-rights.md)).
  A capture may carry a link to one; it never carries the bytes.

<!-- lists: *.md -->
