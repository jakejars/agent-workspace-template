---
id: runs-index
type: doctrine
status: draft
description: Runs chamber map. Use when starting work or closing a session. Not for durable extracted truth (see workspace/30_memory/INDEX.md).
scope: workspace
owner: agent
updated: 2026-08-24
related:
  - type: composes_with
    ref: workspace/50_registers/decision-queue.md
  - type: composes_with
    ref: _templates/run/README.md
  - type: composes_with
    ref: _templates/handover.md
---

# 90_runs — the session record

A run is bounded work against exactly one intent, ending complete or with a
handover. Events go to the journal. Copy `_templates/run/README.md` and, when
continuing, `_templates/handover.md`; do not hand-roll them.

No handover means zero dynamic boot. Otherwise boot reads only the
`*/handover.md` with the greatest parsed UTC `closed_at` (max 3,000 chars).

Run folders are pattern-covered, not enumerated here.

<!-- lists: */*.md -->

## Run folders

```text
90_runs/YYYY-MM-DD-<slug>/
  run.md         the run record (required)
  handover.md    written only if the work continues (see below)
  <artefacts>    drafts, outputs, evidence produced by this run
```

Name each immutable folder `YYYY-MM-DD-<work-slug>`; the slug identifies but
does not order runs. Use one folder per run, including two runs on one day.
`closed_at: YYYY-MM-DDTHH:MM:SSZ` records chronology.

## What a run records

| Section | Content |
|---|---|
| **intent** | exactly one intent id |
| **started / ended** | ISO timestamps. |
| **what was done** | terse chronology; link journal entries |
| **effects** | external changes; class B/C cite approval id |
| **evidence** | executed check and result |
| **open** | unfinished work plus register id |

## Closing a session

1. Append a terse journal digest: work, changes, stop point. The validator
   refuses a run folder that no journal entry traces.
2. Complete `run.md`.
3. If the work continues, write `handover.md`.
4. Run the gates. A failing gate is a stop, not a suggestion.

## The handover contract

Four ordered blocks:

1. **State:** max five lines plus first file/command.
2. **Re-verify:** mandatory commands and expected results; under one minute.
3. **Unfinished:** each item cites its packet/loop/tension/risk id.
4. **Traps:** failed or false-obvious paths; promote verified dead ends.

### Claims are not ground truth

Every handover statement is a claim. Re-verify before work; journal drift.
Never edit a closed-session handover; corrections belong to the next run.
