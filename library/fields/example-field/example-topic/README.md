---
id: library-topic-naming-things
type: topic
status: mature
description: Naming things. Use when naming a file, a folder, an identifier. Not for library filing rules (see library/doctrine/filing-ladder.md).
owner: human
updated: 2026-08-24
review_after: 2027-08-24
related:
  - type: composes_with
    ref: library/doctrine/claims.md
---

# Naming things

*A worked example. It is a real topic — short, honest, and citable —
kept here so the topic kit has a live referent. Replace it with your
own material.*

## What is it?

Choosing the string other people will search for, skim past, and
mispronounce in a meeting. A name is a routing surface: it is read far
more often than it is written, and almost always out of context.

## When should I use it / NOT use it?

- **guideline:** name for the **question the thing answers**, not for
  its implementation or its origin. Exception: an implementation detail
  that genuinely is the subject — a `sha256` helper is named for the
  algorithm because the algorithm is the point.
- **guideline:** if the name needs a parenthetical to be understood,
  the concept is two concepts. Exception: a term of art the audience
  already shares.

## What is my current opinion?

- **opinion:** a slightly-too-long name beats a clever one, because
  disambiguation is cheap and re-reading is not. Holds while names are
  read in flat lists — catalogs, search results, file trees — where no
  surrounding context disambiguates. What would change my mind: an
  environment where the name is always seen inside its own scope.

## Where is it used for real?

- **experience:** renaming a concept mid-project cost less than
  expected each time it was tried (n≈4), and the cost was concentrated
  in links, never in code. Stable identifiers plus cheap renames beat
  getting the name right up front.
