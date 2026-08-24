---
id: kit-topic
type: template
status: mature
description: Library-topic kit. Use when a subject earns a durable home. Not for a collected artifact (see specimen.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: composes_with
    ref: workspace/70_seams/library.md
---

# Kit — library topic

**Copy to:** `library/fields/{{FIELD}}/[{{PILLAR}}/]{{TOPIC}}/README.md`
**Markers:** `{{FIELD}}` `{{PILLAR}}` `{{REVIEW_DATE}}` `{{TODAY}}` `{{TOPIC}}` `{{TOPIC_NAME}}`

No pillar: omit the whole optional segment →
`library/fields/{{FIELD}}/{{TOPIC}}/README.md`.

Delete unanswered questions; do not leave empty headings.

```markdown
---
id: topic-{{TOPIC}}
type: topic
status: stub
description: >
  {{TOPIC_NAME}} — <what it covers, in concrete nouns>. Use when <the
  task shapes that should route here>. Not for <the near miss> (see
  <path>).
load: cue
owner: human
updated: {{TODAY}}
review_after: {{REVIEW_DATE}}
related:
  - type: see_also
    ref: library/fields/<field>/<topic>/README.md
---

# {{TOPIC_NAME}}

## What is it?

## What problem does it solve?

## How does it work?

## What properties and trade-offs does it have?

## When should I use it?

## When should I NOT use it?

## What are the alternatives?

## What does it compose well with?

## Where is it used for real?

## What is my current opinion?
```

## Rules

- Type actionable claims per `library/doctrine/claims.md`: `rule`, `guideline`
  with exceptions, `opinion` with change conditions, `experience` with setting
  and rough n, or linked `evidence`.
- `stub` is intent; `draft` usable with caveat; `mature` reviewed. Cite only
  `draft` or `mature`. File taste as a specimen, not a topic.
- Add this load table only after four deeper files:

  | File | Contains | Load when |
  |---|---|---|
  | `DEEP-DIVE-<concept>.md` | one concept | the concrete cue this row names |
  | `RESOURCES.md` | curated reading | asked for reading |
  | `examples/<name>/` | working prior art | about to copy or adapt it |
  | `specimens/<name>/` | taste | about to borrow the look, or checking rights |

- Deeper files load only on a cue named here.
