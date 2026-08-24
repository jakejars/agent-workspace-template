---
id: library-index
type: doctrine
status: draft
description: Library map. Use when routing to a library area. Not for reading rules (see library/LIBRARY.md).
owner: human
updated: 2026-08-24
related:
  - type: canonical
    ref: library/LIBRARY.md
---

# The library — what is where

The entrance is [`LIBRARY.md`](LIBRARY.md); it carries the routing,
trust, and rights rules. This file is the map.

## Doors

| Door | Holds |
|---|---|
| [`LIBRARY.md`](LIBRARY.md) | The entrance: four rules and the rationale |
| [`fields/`](fields/README.md) | The knowledge itself — fields, pillars, topics, specimens |
| [`inbox/`](inbox/README.md) | Captures whose home is not yet decided |
| [`boards/`](boards/README.md) | Non-canonical views across fields; links only |

## Doctrine

| File | Answers |
|---|---|
| [`doctrine/filing-ladder.md`](doctrine/filing-ladder.md) | Where does this go, and when may a new category exist? |
| [`doctrine/claims.md`](doctrine/claims.md) | How much does this claim weigh, and who says so? |
| [`doctrine/media-and-rights.md`](doctrine/media-and-rights.md) | May this byte be here, and what travels with it? |

The validator enforces metadata, ids, and paths. The local doctrine above
governs library semantics, keeping this member self-contained on extraction.

## The shape

```text
library/
├── LIBRARY.md                the entrance
├── INDEX.md                  this map
├── doctrine/                 the three member rules
├── inbox/<slug>.md           ceremony-free captures; expire unpromoted
├── boards/<through-line>.md  playlists over existing entries
└── fields/<field>/[<pillar>/]<topic>/
    ├── README.md             the topic: typed claims, the ten questions
    ├── DEEP-DIVE-<concept>.md    one concept, loaded on a stated cue
    ├── RESOURCES.md          curated reading
    ├── examples/<name>/       runnable prior art
    └── specimens/<name>/NOTE.md  taste: provenance, rights, what to steal
```

Every rung below `topic` is optional and most topics never grow one. A
folder that exists because the shape allows it, rather than because
something lives in it, costs a reader attention on every visit.

## Choosing a home

```text
a reusable concept, method, or decision guide ─► a topic README
an artifact worth stealing from ──────────────► a specimen under that topic
a link or half-thought, home unclear ─────────► inbox/
a through-line across existing entries ───────► boards/
true only of one piece of work ───────────────► not the library at all
```

The last line is the boundary that keeps this store worth reading: the
library holds what transfers. Work-specific knowledge stays where the
work is.

## Adding a file

Copy the kit (`_templates/topic.md`, `_templates/specimen.md`,
`_templates/capture.md`), file it per
[`doctrine/filing-ladder.md`](doctrine/filing-ladder.md), link it from
the door above it, then rebuild the family catalog and run the loop
check. An unlisted file is an orphan and the gate says so.
