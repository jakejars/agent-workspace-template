---
id: kit-skill
type: template
status: mature
description: Agent Skill kit. Use when packaging reusable task-cued behaviour. Not for an ordinary procedure (see ../procedure.md).
load: drill
owner: human
updated: 2026-10-07
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: composes_with
    ref: workspace/60_capabilities/skills/README.md
---

# Kit — skill

**Copy to:** `workspace/60_capabilities/skills/{{SLUG}}/SKILL.md`
**Markers:** `{{SLUG}}` `{{TODAY}}`

Folder: `SKILL.md`, optional `scripts/`, `references/`, and `assets/`.
Copy only the fenced record; this kit's README is not a skill payload.
The directory and `name` must match: lowercase letters, digits, and hyphens,
at most 64 characters; no leading, trailing, or consecutive hyphens.

```markdown
---
id: skill-{{SLUG}}
name: {{SLUG}}
type: skill
status: draft
description: >
  <What it does>. Use when <the recognisable task trigger>.
  Not for <the near-miss case> (see <ref>).
scope: workspace
load: cue
owner: agent
provenance: agent_proposed
updated: {{TODAY}}
---

# <Imperative naming the skill>

## When to use this

<Objective task trigger and the boundary with similar work.>

## Preconditions

<Required inputs, verified state, and any authority needed before execution.>

## Steps

1. <Action> — <observable result>.
2. <Action> — <observable result>.
3. <Action> — <observable result>.

## Verification

<Command, file, or result that detects silent failure; recovery or stop condition.>

## Supporting files

<Link optional scripts and references here; state when each should be loaded.
Delete this section when the skill is self-contained.>
```

## Rules

- Keep `description` in the house cue form and within its 180-character limit;
  this also satisfies the Agent Skills 1,024-character maximum.
- Package a proven procedure when it is reused, its trigger is recognisable
  from the task, and runtime-native loading helps. Procedures remain valid;
  packaging as a skill is optional. Link the source procedure when retained.
- Start `draft` + `agent_proposed` and record the local capability as
  `untrusted` in the lockfile. Apply the existing capability trust ladder;
  only a human promotes, and skill instructions grant no new permissions.
- Link from the [skills door](workspace/60_capabilities/skills/README.md).
  Markdown supporting files need house frontmatter and door coverage;
  use `type: capability` for package documentation. Deeper paths need an
  explicit bounded `lists` pattern.
- Run `python3 tools/skills.py check`. Optional export copies the skill with
  `python3 tools/skills.py export --to <dir> [--trusted-only]`; the
  [consumer contract](doctrine/consumers.md) owns output and ownership rules.
