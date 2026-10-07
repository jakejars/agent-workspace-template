---
id: execution
type: doctrine
status: draft
description: Execution choices. Use when choosing scripts, delegation, or a reusable process. Not for effect authorization (see workspace/80_governance/autonomy.md).
owner: human
updated: 2026-10-07
related:
  - type: depends_on
    ref: doctrine/disclosure.md
  - type: see_also
    ref: _templates/procedure.md
  - type: see_also
    ref: _templates/pipeline/README.md
---

# Execution

## Code for the deterministic

If the same inputs should give the same result every time, make the step a
script and have the model call it. Counting, renaming, format conversion,
fixed extraction, and validation belong in code. Model reasoning handles
ambiguity and judgement; a human handles an explicitly assigned decision.

Procedures declare an executor for each step. Pipeline stages declare
`executor: script | model | human`; a script stage names its deterministic
command. Executor choice grants no authority for the resulting effect.

## Sub-agent test

Delegate only when the work is clearly specifiable, mostly independent,
benefits from parallelism or context isolation, and returns a compact artifact.
Otherwise one agent with the right context does it. Give the delegate only
its required inputs and a bounded output contract. Delegated work returns a
file; the delegator verifies it before relying on it.

## Choosing a form

| Work | Form |
|---|---|
| One-off task | Intent + current checkpoint |
| Proven repeatable sequence | Procedure, or a skill when a suitable skills kit is available |
| Fixed multi-stage deliverable process | Pipeline |
| Consequential or audited execution | Run |

Forms compose: executing a pipeline creates an ordinary run that records the
pipeline version. Each stage loads only its declared Reference and Working
inputs, writes its named output to disk, and stops at a declared human
checkpoint before the next stage. Reference rules stay unchanged; Working
artifacts may be inspected and edited. Re-read the current artifact after
review. A bounded evaluator/revise loop states its stopping condition.

## Walk test

A fresh agent with no memory, starting at `workspace/AGENTS.md`, must be able
to orient, say what it can do, and report current state. Follow the chamber
doors and task-cued contracts rather than importing a previous agent's
context. Task checkpoints hold ordinary work's current state. For an in-flight
pipeline, `python3 tools/pipeline.py status --run <run-id>` reconstructs outputs,
pending human checkpoints, and the next stage from files on disk. Verify the
reported evidence before continuing.
