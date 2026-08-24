---
id: kit-specimen
type: template
status: mature
description: Kit for a library specimen. Use when saving something made by someone else that is worth borrowing. Not for analytical knowledge that makes claims (see topic.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: composes_with
    ref: workspace/70_seams/library.md
---

# Kit — library specimen

**Copy to:**
`library/fields/{{FIELD}}/{{TOPIC}}/specimens/{{SPECIMEN}}/NOTE.md`
**Markers:** `{{FIELD}}` `{{SPECIMEN}}` `{{SPECIMEN_NAME}}` `{{TODAY}}` `{{TOPIC}}`

A specimen records taste, not claims. Route `mood` as feeling and `style` as
technique. Keep binary media external behind a seam; record links and rights.

```markdown
---
id: specimen-{{SPECIMEN}}
type: specimen
status: draft
description: >
  {{SPECIMEN_NAME}} — <what the artifact is, one line>. Use when <the
  situations its qualities help — this is the steal cue>. Not for <the
  near-miss taste> (see ../../README.md).
load: drill
owner: human
updated: {{TODAY}}
mood: [<feel>, <feel>]
style: [<technique>, <material>]
source: <url>
license: All-Rights-Reserved
related:
  - type: canonical
    ref: library/fields/<field>/<topic>/README.md
---

# {{SPECIMEN_NAME}}

**Why it resonates:** <specific differentiating quality>

**Steal this when:** <contexts, constraints, scale, audience>

**Do not steal when:** <near-miss contexts>

## What exactly to steal

<!-- The transferable moves, concrete beats admiring: "the grid survives
     contact with real content", "error copy names the fix, not the
     fault". -->

- <move one>
- <move two>

## Contents and rights

<!-- One row per linked asset. No row, no keep. Unknown means
     all-rights-reserved. -->

| File | Creator | License | Source |
| --- | --- | --- | --- |
| (remote) | <creator> | <SPDX id, or All-Rights-Reserved (study quotation)> | <url> |

## Provenance and context

<Creator, date, constraints, purpose.>
```

## Rules

- Keep `draft` until a real borrowing succeeds; only then mark `mature`.
- Keep binary media external through a seam and list every linked asset in the
  rights table.
- Never guess licenses, remove attribution, export specimen media, or promote
  one specimen into a category.
- Multiple related specimens trigger the filing ladder. Add a `canonical`
  edge to the topic.
