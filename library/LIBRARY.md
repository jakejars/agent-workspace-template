---
id: library-entrance
type: doctrine
status: draft
description: The library. Use when a task needs durable reference knowledge, examples, or taste. Not for its inventory (see library/INDEX.md).
owner: human
updated: 2026-08-24
review_after: 2027-08-24
related:
  - type: composes_with
    ref: library/INDEX.md
---

# The library

A cue-only reference store; nothing boots. Answer with 2–3 routed files.

It holds **two registers that never blur**:

- **Practice:** analytical topics with typed claims
  ([`claims.md`](doctrine/claims.md)).
- **Taste:** specimens with provenance, rights, and borrow boundaries
  ([`media-and-rights.md`](doctrine/media-and-rights.md)).

Separate argument from inspiration into linked files. Both live under
[`fields/`](fields/README.md): field → pillar → topic → specimen.

## The routing rule

1. Route by generated catalog descriptions or [`INDEX.md`](INDEX.md), not
   folder names.
2. Open at most three entries unless explicitly comparing or maintaining.
3. Follow deeper files only on a cue named by the current file.

Check `related`, especially `canonical`: one truth, one home, linked aliases.

## The trust rule

| Status | Means | Citable |
|---|---|---|
| `reserved` | Scaffolding: a name with nothing behind it | Never |
| `stub` | Intent to write | Never |
| `draft` | Usable, provisional | Yes, with the caveat said out loud |
| `mature` | Reviewed | Yes |

Carry claim type and opinion conditions into citations. Specimens confer taste,
not authority; honor exclusions and attribution.

## The rights rule

Before commit, every collected byte needs File/Creator/License/Source. Unknown
provenance = all-rights-reserved: do not keep, guess, or strip attribution.
Default to links. Never export specimen media; cite, describe, link, or borrow
moves in place.

## Adding to it

Past one minute, use [`inbox/`](inbox/README.md). Categories climb
[`filing-ladder.md`](doctrine/filing-ladder.md) one rung; no ad-hoc folders.
Kits: `_templates/topic.md`, `_templates/specimen.md`, `_templates/capture.md`.

Never hand-edit the generated catalogs, and never silently rewrite a
`status: mature` entry — propose the diff instead.
