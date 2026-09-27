---
id: runs-index
type: doctrine
status: draft
description: Runs chamber map. Use when starting work or closing a session. Not for durable extracted truth (see workspace/30_memory/INDEX.md).
scope: workspace
owner: agent
updated: 2026-09-06
related:
  - type: composes_with
    ref: workspace/50_registers/decision-queue.md
  - type: composes_with
    ref: _templates/run/README.md
  - type: composes_with
    ref: _templates/handover.md
---

# Runs and historical handovers

Detailed runs are optional. Standard work uses one active intent record and
its current checkpoint; see [intent](../20_intent/INDEX.md). Use a run for
an external effect, substantial evidence bundle, or an explicit audit profile.

Each run traces exactly one intent and has a journal entry citing it. Copy
[the run kit](_templates/run/README.md); optional historical handovers use
[the handover kit](_templates/handover.md).

<!-- lists: */*.md -->

## Layout

```text
90_runs/YYYY-MM-DD-<slug>/
  run.md         required if a detailed run is created
  handover.md    optional historical close summary
  work/          ignored scratch; arbitrary formats
  artifacts/     ignored deliverables/evidence; arbitrary formats
```

Cite artifacts by relative path and, where integrity matters, checksum. A
small typed Markdown evidence note is the durable index; generated artifacts
need no frontmatter. Keep required external sources behind a seam. Ignoring a
file does not grant permission to share it or make it a backup.

## Current state versus history

Update the active task checkpoint during meaningful work and before a pause.
A historical handover is bounded to 3,000 characters and never implicitly
selected for a new task. Old claims require re-verification. Do not edit a
closed-session handover; correct in the next task checkpoint or journal entry.

## Close

State outcome and evidence in the task. For detailed runs, finish `run.md`,
append its journal trace, and optionally write a handover. Run the neutral
lifecycle close command unless an adapter already did so. Changed metadata
and graph are validated; unchanged sources reuse the checked cache.
