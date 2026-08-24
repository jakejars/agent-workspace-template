---
id: knowledge-references
type: doctrine
status: draft
description: External references. Use when citing a document or specification. Not for copying source content (see workspace/70_seams/world.md).
scope: workspace
owner: agent
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/40_knowledge/INDEX.md
  - type: depends_on
    ref: workspace/70_seams/world.md
fields:
  - name: url
    for: knowledge
    required: true
  - name: accessed
    kind: date
    for: knowledge
    required: true
  - name: asserts
    for: knowledge
    required: true
  - name: used_by
    kind: list
    for: knowledge
---

# references/ — pointers out, nothing fetched

A reference is an address and a claim about what is at that address.
It is not the thing at that address. This chamber holds no copied
pages, no mirrored docs, no scraped text.

One file per source: `<slug>.md`, `type: knowledge`,
`provenance: imported`.

## Fields

```yaml
url: https://…                   # or an absolute path for local sources
accessed: YYYY-MM-DD             # when a human or agent last looked
asserts: <what this source is claimed to say, in one sentence>
used_by: [<id>, ...]             # what in this workspace rests on it
```

- **accessed** — the date the claim in `asserts` was checked against
  the source. Sources change under their URLs; the date is what makes
  the citation falsifiable.
- **asserts** — one sentence, in this workspace's words. Enough to
  tell whether re-fetching is worth it. Not a summary of the source,
  and never a substitute for reading it.
- **used_by** — the canon files, decisions, or facts that cite it. A
  reference nothing uses is deleted, not kept "in case".

## Why nothing is mirrored

1. **Provenance stays honest.** A mirrored page silently becomes a
   local claim with no clock; the original moves on and no one knows.
2. **The copy is not ours.** Copyright and licence live with the
   source; the sett keeps the address.
3. **Verified knowledge belongs in canon anyway.** When this workspace
   has confirmed something an external source says, that becomes a
   canon file in this workspace's own words, citing this reference.
   The reference remains the provenance, not the content.

The one exception is a source that is genuinely unavailable otherwise
(a dead link with an archived copy, a licence that permits it) — that
is a Class B call, filed as a Decision Packet, with the licence noted
in the file.

## Fetching

Filing a reference requires no network access — the address is enough.
Actually retrieving anything crosses the world seam
(`70_seams/world.md`) and obeys whatever that seam says; when the seam
is closed, references are still filed, just not followed.
