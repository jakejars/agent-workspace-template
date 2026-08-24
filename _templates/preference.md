---
id: kit-preference
type: template
status: mature
description: Preference kit. Use when corrections show what the principal consistently prefers. Not for facts (see memory-fact.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: contrast_with
    ref: _templates/memory-fact.md
---

# Kit — preference

**Copy to:** `workspace/30_memory/preferences/{{SLUG}}.md`
**Markers:** `{{HHMM}}` `{{REVIEW_DATE}}` `{{SLUG}}` `{{TODAY}}`

```markdown
---
id: pref-{{SLUG}}
type: preference
status: draft
description: >
  <The preference in one sentence.> Use when <the moment of choice it
  settles>. Not for <the case it explicitly does not cover> (see
  <ref>).
scope: workspace
load: cue
owner: human
provenance: agent_proposed
confidence: 0.6
rule: <the rule this preference sets, in one line>
support:
  - workspace/30_memory/journal/{{TODAY}}-{{HHMM}}-{{SLUG}}.md
review_after: {{REVIEW_DATE}}
updated: {{TODAY}}
---

# <Short imperative naming the preference>

## Preference

<Unambiguous instruction; 1 sentence.>

## Scope

Where it binds and where it stops.

- Applies to: <domain, artefact kind, audience, project>
- Does not apply to: <the neighbouring case that keeps the default>

## Confidence and rule

`confidence: 0.8` · `rule: >=3 consistent corrections, none contrary`

<Rule producing the number.>

## Evidence

Newest first; cite journal/run corrections, never recollection.

- {{TODAY}} — `30_memory/journal/{{TODAY}}-{{HHMM}}-<slug>.md` — <correction>
- <date> — <ref> — <correction in a line>

## What it changes

<Concrete next-task behavioural delta.>

## Contrary evidence

<Every contrary correction, or "none observed".>
```

## Rules

- Only `mature` preferences may be `always`; drafts load on cue.
- Send cross-workspace preferences to the commons as correction candidates.
- Constitution, policies, and boundaries override preferences.
