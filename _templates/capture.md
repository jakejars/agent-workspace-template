---
id: kit-capture
type: template
status: mature
description: Kit for a library capture. Use when filing takes longer than a minute. Not for a topic that has earned a home (see topic.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: workspace/70_seams/library.md
---

# Kit — library capture

**Copy to:** `library/inbox/{{SLUG}}.md`
**Markers:** `{{SLUG}}` `{{TITLE}}` `{{TODAY}}`

Catalogued capture with four optional prompts; filing comes at promotion.

```markdown
---
id: capture-{{SLUG}}
type: knowledge
status: stub
description: >
  {{TITLE}} — <one line, what this is>. Use when <the question it might
  answer>. Not for citation until promoted (see library/inbox/README.md).
load: drill
owner: human
provenance: authored
updated: {{TODAY}}
---

# {{TITLE}}

Source:
Why I saved this:
Possible homes:
What question might this answer:

---

<the material — a link, a quote, a screenshot path, a half-thought>
```

## Rules

- Prompts may be empty; never guess. Keep one capture per file.
- No claim typing, rights table, or `review_after`; link remote artifacts but do
  not commit their bytes. Promotion supplies those fields.
- Captures remain uncited `stub`s. Promote on use/reuse/convergence; otherwise
  move to topic resources or delete.
