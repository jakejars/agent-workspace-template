---
id: kit-intent
type: template
status: mature
description: Intent-record kit. Use when something is wanted and a run will attempt it. Not for standing rules (see workspace/80_governance/policies.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: composes_with
    ref: _templates/run/README.md
---

# Kit — intent

**Copy to:** `workspace/20_intent/active/{{INTENT_SLUG}}.md`
**Markers:** `{{INTENT_SLUG}}` `{{INTENT_TITLE}}` `{{TODAY}}`

```markdown
---
id: intent-{{INTENT_SLUG}}
type: intent
status: draft
description: >
  {{INTENT_TITLE}} — what is wanted, and why now. Use when deciding
  whether a task belongs to {{INTENT_SLUG}}. Not for a neighbouring
  intent (see workspace/20_intent/INDEX.md).
scope: workspace
lifecycle: captured
load: cue
owner: human
updated: {{TODAY}}
related:
  - type: canonical
    ref: workspace/30_memory/preferences/<preference>.md
---

# {{INTENT_TITLE}}

## Objective

<Changed-world outcome, not plan; 1 paragraph.>

## Constraints

Task bounds only; link standing rules.

- <constraint, stated as a bound: "never <x>", "stay within <y>">
- <constraint>

## Success definition

Falsifiable conditions:

- [ ] <observable condition, checkable by someone who was not here>
- [ ] <observable condition>

## Delegation deltas

<Added/withheld authority. Empty = standing classes unchanged.>

- <class B action> is pre-approved for this intent until <date>
- <class A action> is withheld for this intent

## Not in scope

<Named exclusions.>

- <excluded thing>

## Runs

Newest first; one line each.

- {{TODAY}} — `90_runs/<run-id>/` — <outcome in five words>
```

## Rules

- Link standing identity, preferences, and policy; do not embed them.
- Each run cites exactly one intent; many runs may share it.
- `status` is trust; `lifecycle` is captured → clarified → approved →
  delegated → satisfied | abandoned | superseded. Move terminal records to
  `20_intent/satisfied/` with `git mv`; never delete them.
