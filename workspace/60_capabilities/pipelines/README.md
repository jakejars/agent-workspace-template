---
id: pipelines-index
type: doctrine
status: draft
description: Pipeline definition door. Use when choosing or defining a staged process. Not for its execution state (see workspace/90_runs/INDEX.md).
scope: workspace
owner: agent
updated: 2026-10-07
related:
  - type: composes_with
    ref: _templates/pipeline/README.md
  - type: see_also
    ref: doctrine/execution.md
---

# Pipelines

Each `<slug>/PIPELINE.md` defines a reusable deliverable process and its
version. Its `01_<stage>/STAGE.md`, `02_<stage>/STAGE.md`, and later contracts
define ordered, inspectable transformations. Create one with the
[pipeline kit](_templates/pipeline/README.md); none is installed by default.
Choose the form and executor with [execution guidance](doctrine/execution.md).

A model stage may set `skill: <name>` for a directory in [skills/](../skills/README.md); `check` verifies that directory exists.

<!-- lists: */PIPELINE.md -->
<!-- lists: */[0-9][0-9]_*/STAGE.md -->

## Execute and resume

Run `python3 tools/pipeline.py check` after editing a definition. Start an
ordinary run with `python3 tools/pipeline.py start --pipeline <slug> --run
YYYY-MM-DD-<slug>`; add `--intent <id-or-slug>` unless exactly one intent is
active. Existing run folders are refused.

Only load the current stage contract, its Reference constraints, and its
Working artifacts. Log those inputs in run.md. Write each output in that
run's numbered stage folder; the next stage reads it from disk, including
any human edits. Runs retain the selected pipeline version, content digest,
and stage plan. Bump the version on definition changes; start a new run to
use the changed definition.

`python3 tools/pipeline.py status --run <run-id>` reconstructs output and
checkpoint state without changing files or executing commands. Keep the
[intent checkpoint](workspace/20_intent/INDEX.md) current for broader state.

## Human checkpoint

For `checkpoint: true`, pause once the output exists. The human inspects or
edits that file before the next stage. Record the confirmed review in
`<run-id>/<stage>/checkpoint.json`:

```json
{
  "approved": true,
  "output_sha256": "<sha256 of the reviewed output bytes>",
  "reviewed_by": "<human name>",
  "reviewed_on": "YYYY-MM-DD"
}
```

Transcribe only an actual human review. Changed output bytes invalidate the
receipt and require another review. Outputs and receipts record progress;
they grant no action authority. Follow the existing
[autonomy rules](workspace/80_governance/autonomy.md) for every effect.
