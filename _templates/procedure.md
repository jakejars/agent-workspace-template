---
id: kit-procedure
type: template
status: mature
description: Procedure kit. Use when a proven sequence should be reusable. Not for a one-off execution plan (see _templates/run/README.md).
load: drill
owner: human
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: composes_with
    ref: _templates/dead-end.md
---

# Kit — procedure

**Copy to:** `workspace/30_memory/procedures/{{SLUG}}.md`
**Markers:** `{{SLUG}}` `{{TODAY}}` `{{REVIEW_DATE}}`

```markdown
---
id: proc-{{SLUG}}
type: procedure
status: draft
description: >
  <What it does, in one sentence.> Use when <the trigger condition>.
  Not for <the near-miss case> (see <ref>).
scope: workspace
load: cue
owner: agent
provenance: agent_proposed
version: 1
verified_on: {{TODAY}}
verified_by: agent
preconditions:
  - <what must already be true before step 1>
review_after: {{REVIEW_DATE}}
updated: {{TODAY}}
---

# <Imperative naming the procedure>

## When to run this

<Objective trigger.>

## Preconditions

Check before step 1; stop on any failure.

- <state that must already be true>
- <access or approval that must already exist>

## Inputs

Name the load set before step 1, split by how each file is read.

- Working (this run): `<path>` — <the artifact this run acts on>
- Reference (every run): `<path>` — <the standing rule that constrains it>
- Excluded: `<path>` — <why it looks relevant here and is not>

## Steps

1. <action> — <what you should see>
2. <action> — <what you should see>
3. <action> — <what you should see>

One action + observable result per step.

## Verification

<Post-step command/file/output that detects silent failure.>

## Failure modes

| Symptom | Cause | What to do |
|---|---|---|
| <what you see> | <why> | <the recovery, or "stop and file a packet"> |

## Autonomy

Class A | B | C + reason. External effects are at least B; name approval.

## Version

Newest first; changed steps add a version line.

- v1 · {{TODAY}} — first promotion from run `90_runs/<run-id>/`.
```

## Rules

- Require two successful runs before promotion and a verification step.
- Working inputs belong to this run; reference inputs provide standing
  constraints and are re-read when changed. An input that is neither belongs in `related`, not in Inputs.
- File failed steps as linked dead ends.
