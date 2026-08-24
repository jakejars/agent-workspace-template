---
id: kit-dead-end
type: template
status: mature
description: Dead-end kit. Use when an approach is disproven and costly to repeat. Not for a merely rejected option (see decision.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: contrast_with
    ref: _templates/decision.md
---

# Kit — dead end

**Copy to:** `workspace/30_memory/dead-ends/{{SLUG}}.md`
**Markers:** `{{SLUG}}` `{{TODAY}}` `{{REVIEW_DATE}}`

```markdown
---
id: dead-{{SLUG}}
type: dead-end
status: draft
description: >
  <Approach> does not work for <goal>, because <reason>. Use when
  considering <approach>. Not for the untested variant (see <ref>).
scope: workspace
load: cue
owner: agent
provenance: agent_proposed
tried: <the approach, in one line>
why_dead: <the one-clause reason it cannot work>
verified_on: {{TODAY}}
verified_by: agent
bounds: <the version, machine or contract this was tested under>
support:
  - workspace/90_runs/<run-id>/run.md
reopen_if: <what would make this worth trying again>
review_after: {{REVIEW_DATE}}
updated: {{TODAY}}
related:
  - type: canonical
    ref: workspace/90_runs/<run-id>/run.md
---

# <Approach> — dead end

## What was tried

<Concrete, recognizable approach; 2–3 sentences.>

## How far it got

<Furthest working point and reusable part.>

## Why it fails

<Inevitable failure mechanism, not symptom.>

## Evidence

- {{TODAY}} — `90_runs/<run-id>/` — <the run that hit the wall>
- <artefact, log line, upstream issue, or version that pins it>

## Cost

<hours / runs / tokens>

## What would reopen it

<Version/platform/permission/capability, or "nothing—structural".>
```

## Rules

- File verified failures only; hunches remain open loops.
- Scope to goal and conditions; leave untested variants open.
- Link from the originating procedure, decision, or intent.
