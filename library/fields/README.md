---
id: library-fields
type: doctrine
status: draft
description: The fields root. Use when looking for a topic. Not for the ladder's recipes (see library/doctrine/filing-ladder.md).
owner: human
updated: 2026-08-24
related:
  - type: canonical
    ref: library/INDEX.md
  - type: depends_on
    ref: library/doctrine/filing-ladder.md
fields:
  - name: mood
    kind: list
    for: specimen
    required: true
  - name: style
    kind: list
    for: specimen
    required: true
  - name: source
    for: specimen
    required: true
  - name: license
    for: specimen
    required: true
---

# Fields

A **field** is a domain of practice. A **pillar** is a division inside
it. A **topic** is the unit that answers a question, and **specimens**
sit under the topic they inform.

```text
fields/<field>/INDEX.md                type: field    the field door
        [<pillar>/INDEX.md]            type: pillar   once the field earns one
          <topic>/README.md            type: topic    where knowledge lives
            specimens/<name>/NOTE.md   type: specimen taste, with rights
```

Those four types bind by **path**: they are depth positions in one
tree, and they are legal nowhere else in the family.

The pillar level is not skipped, it is **earned**: a pillar's bar is
three or more topics already visible, so a young field holds its topics
directly and grows the middle rung when the material asks for it.

**This is a namespace, not a mandate.** A field with two populated
topics and four reserved doors is a correct field. A field filled out
to look complete is a landfill with a table of contents — and every
empty door costs a reader attention on the way past.

## Fields here

| Field | Holds |
|---|---|
| [`example-field/`](example-field/INDEX.md) | The worked example that ships with the template: one topic, so a kit has a live referent. Delete it, or rename it into your first real field. |

The template ships one field on purpose. Yours arrive from captures,
not from planning.

## How a field is born

Only at the top of the ladder, and only when all three hold:

1. It is an entire **domain of practice**, not a subdiscipline of a
   field you already have.
2. It **fits no existing field** — checked against the boundary rows in
   [`../doctrine/filing-ladder.md`](../doctrine/filing-ladder.md), not
   from memory.
3. You can name **three or more pillars** it would eventually hold.

Then: the field block into the family `NAMESPACE.md`, an `INDEX.md`
here at `status: reserved`, and the first pillar and topic seeded from
captures you already have. A field that opens empty stays empty.

Everything below that bar climbs a lower rung — a topic in an existing
pillar, or the inbox. Nothing is filed by inventing a folder.

## Reading a field

Route by description, not by folder name: the field door says what the
field covers and what it pointedly does not. Open the topic, then go
deeper only on a cue the topic states. Three files is the usual budget
for a question.
