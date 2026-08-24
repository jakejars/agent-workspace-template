---
id: kit-memory-fact
type: template
status: mature
description: Promoted-fact kit. Use when a journal observation is stable enough to promote. Not for taste (see preference.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: contrast_with
    ref: _templates/preference.md
---

# Kit — memory fact

**Copy to:** `workspace/30_memory/facts/{{SLUG}}.md`
**Markers:** `{{HHMM}}` `{{REVIEW_DATE}}` `{{SLUG}}` `{{TODAY}}`

```markdown
---
id: fact-{{SLUG}}
type: memory-fact
status: draft
description: >
  <The fact, in one sentence.> Use when <the situation where not
  knowing this causes a wrong step>. Not for <the adjacent thing this
  is confused with> (see <ref>).
scope: workspace
load: cue
owner: agent
provenance: agent_proposed
support:
  - workspace/30_memory/journal/{{TODAY}}-{{HHMM}}-{{SLUG}}.md
claim: evidence
verified_on: {{TODAY}}
review_after: {{REVIEW_DATE}}
updated: {{TODAY}}
related:
  - type: canonical
    ref: workspace/30_memory/journal/{{TODAY}}-{{HHMM}}-{{SLUG}}.md
---

# <Short noun phrase naming the fact>

## Statement

<Present-tense fact; 1–2 sentences; no hedge or narrative.>

## How it was established

Claim kind: `evidence` | `experience(n=<count>)` | `reported`.

<What, where, when; raw journal/artifact; 1–2 lines.>

## Where it does and does not hold

- Holds: <machine, project, tool version, account — the boundary>
- Does not hold: <the case that looks the same and is not>

## What it changes

<Behaviour or decision changed by this fact.>

## Supersession

Newest first. Corrections create a new file with `supersedes` pointing here.

- {{TODAY}} — first promotion from journal.
```

## Rules

- Agents write `agent_proposed`; only humans promote.
- Record how the fact was established.
- Set `review_after`; the staleness gate detects moving-world decay.
