---
id: kit-pipeline
type: template
status: mature
description: Pipeline definition kit. Use when a deliverable has fixed stages. Not for an execution record (see _templates/run/README.md).
load: drill
owner: human
updated: 2026-10-07
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: composes_with
    ref: _templates/run/README.md
---

# Kit — pipeline

**Copy to:** `workspace/60_capabilities/pipelines/{{SLUG}}/PIPELINE.md`
**Markers:** `{{SLUG}}` `{{TODAY}}`

Copy the first fence to PIPELINE.md and the next two to their named stage folders. Fill for the actual process and link from the [pipeline door](workspace/60_capabilities/pipelines/README.md); this fenced example is not installed.

```markdown
---
id: pipeline-{{SLUG}}
type: pipeline
status: draft
description: Deliverable pipeline. Use when producing the defined deliverable. Not for run state (see workspace/90_runs/INDEX.md).
owner: agent
provenance: agent_proposed
version: 1
updated: {{TODAY}}
---

# Deliverable pipeline

Prepare material and review a deliverable through inspectable files.

## Stages

1. [Prepare](01_prepare/STAGE.md)
2. [Review](02_review/STAGE.md)
```

**Stage target:** `workspace/60_capabilities/pipelines/{{SLUG}}/01_prepare/STAGE.md`

```markdown
---
id: stage-{{SLUG}}-prepare
type: stage
status: draft
description: Prepare working material. Use when beginning this pipeline. Not for final review (see ../02_review/STAGE.md).
load: drill
owner: agent
provenance: agent_proposed
executor: model
checkpoint: false
output: artifacts/prepared.md
updated: {{TODAY}}
---

# Prepare

## Purpose

Turn this run's source material into a compact working draft.

## Inputs

### Reference

The intent's acceptance criteria; internalise them as constraints, unchanged.

### Working

The source material named in this run's Context loaded section.

## Process

Read only these inputs. Resolve ambiguity and write the prepared draft to this stage's output path in the run.
Preserve source references and identify unresolved questions for review.
```

**Stage target:** `workspace/60_capabilities/pipelines/{{SLUG}}/02_review/STAGE.md`

```markdown
---
id: stage-{{SLUG}}-review
type: stage
status: draft
description: Review the prepared draft. Use when preparation has produced an output. Not for source preparation (see ../01_prepare/STAGE.md).
load: drill
owner: agent
provenance: agent_proposed
executor: model
checkpoint: true
revision_limit: 2
output: artifacts/deliverable.md
updated: {{TODAY}}
---

# Review

## Purpose

Produce a deliverable that meets the intent's acceptance criteria.

## Inputs

### Reference

The intent's acceptance criteria; internalise them as constraints, unchanged.

### Working

This run's `01_prepare/artifacts/prepared.md`, including human edits.

## Process

Read only these inputs. Evaluate the draft against the criteria and write
the deliverable to this stage's output path in the run.

## Evaluation

### Evaluator

Check each acceptance criterion against a cited part of the deliverable.

### Revise

Fix failed criteria in this stage's output and evaluate again.

### Stop

Stop when every criterion passes, or when `revision_limit` is reached. At the bound, record unresolved failures and pause for the human checkpoint.
```

## Rules

- Number stages contiguously from `01_` with a kebab-case name; use PIPELINE.md and STAGE.md.
  Bump the positive integer `version` when the definition or a contract changes.
- Cap each STAGE.md at 3,000 characters including frontmatter, matching the [dynamic context budget](doctrine/disclosure.md).
  `pipeline.py check` enforces it. Load only the current contract and its named inputs.
- Declare `executor: script`, `model`, or `human`; scripts add `command: <deterministic command>`.
  Tools validate but never execute commands. Follow [execution guidance](doctrine/execution.md).
- `output` names one safe file under `artifacts/` in the stage's run folder; finish it before continuing.
  A human may inspect/edit it. `checkpoint: true` requires review, including after the final stage.
- Optional Evaluation has Evaluator, Revise, and Stop subsections with success criteria and a positive integer `revision_limit` in frontmatter.
  Failed evaluation pauses. Execute through the [ordinary run kit](../run/README.md).
