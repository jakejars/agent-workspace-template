---
id: lifecycle
type: doctrine
status: draft
description: Neutral lifecycle commands. Use when installing hooks or finding task context. Not for gate semantics (see doctrine/gates.md).
owner: human
updated: 2026-09-06
related:
  - type: composes_with
    ref: doctrine/disclosure.md
  - type: composes_with
    ref: doctrine/gates.md
---

# Lifecycle and context

Every agent can use the same local commands. No runtime, daemon, account,
network service, or model API is required. Run from the sett root.

```sh
python3 tools/hooks/install.py          # local Git hook installation
python3 tools/hooks/install.py --check  # configuration and executability
python3 tools/lifecycle.py status       # observed event receipts
```

Installation preserves an existing different hooks directory and reports how
to chain commands. It never edits account or runtime settings. Configuration
proves a command is connected; a receipt proves that an invocation happened.
Neither alone proves all future events will fire.

## Event contract

| Event | Call | Work performed |
|---|---|---|
| Session starts/resumes | `python3 tools/lifecycle.py start` | Validate source and graph if changed; offer active tasks |
| Task/request arrives | `python3 tools/lifecycle.py prompt --query "<terms>"` | Return at most three relevant cue pointers |
| Successful source write | `python3 tools/lifecycle.py changed` | Cheap dirty hint; no graph rebuild |
| Meaningful work ends / before compaction | `python3 tools/lifecycle.py close` | Validate changed metadata/graph and refresh cache |
| Before Git commit | `.githooks/pre-commit` | Validate the exact staged snapshot |
| After Git commit, checkout, merge | respective `.githooks/post-*` | Refresh source-derived context; record success/failure |

Unchanged source reuses the checked cache. Fingerprinting detects changes even
if a runtime missed a write event; freshness does not depend on a dirty hint.
Graph validation runs at boundaries or the next context request after a change,
not on every edit.
Regression suites run in CI and before releases, not on every ordinary commit.

Runtime adapters should call these commands at the matching events. A caller
can send neutral JSON through `python3 tools/lifecycle.py --json`:

```json
{"event":"prompt","query":"build cache","task":"intent-build-cache"}
```

`event` is start, prompt, changed, close, or status. Query and task are optional.
Exit 0 means successful handling; nonzero means the check could not establish
a valid state. A close failure must be repaired before claiming clean work.
Post-Git hooks report failure without pretending to undo the completed Git act.

## Selecting and checkpointing work

```sh
python3 tools/context.py show --task <id>
python3 tools/context.py show --query "<task terms>"
python3 tools/context.py show --from <relevant-id> --query "<terms>"
python3 tools/context.py checkpoint --task <id> --text "<state; next step>"
```

The current user request selects a task, never a recency heuristic. Only active
intent records load as current context. Completed/abandoned/superseded tasks
and historical handovers never silently resume. Update a checkpoint after a
meaningful step, not only on graceful shutdown: a hook cannot infer unfinished
work after a crash. Single writer per workspace; use isolation for parallel work.

Cue routing scores descriptions and IDs, returns pointers rather than bodies,
and excludes expired, superseded, historical, and unopened records. A drill
record is suggested only if directly linked by the explicit `--from` source.
Proposed factual evidence is labelled provisional; proposed policy never
becomes injected authority. Optional family stores are entered through seams.

## Cache and artifacts

`.sett-cache/context.json` contains validated metadata and graph edges;
`.sett-cache/lifecycle.json` stores only latest event receipts. Both are ignored,
replaceable derived data. No prompts or transcripts are persisted in receipts.
The source graph and dates determine validity; deleting the cache is safe.
Validation failure never serves the previous cache as current.

Use root `work/` and `artifacts/`, or a detailed run's corresponding ignored
subdirectories, for arbitrary generated formats. Typed knowledge records hold
pointers and evidence summaries; artifacts need no frontmatter. Ignored files
are excluded from normal source checks, never from authorization to export.

## Hook coverage

Git events are wired by the installer. Session/prompt/write/close events require
the chosen runtime to call the neutral contract. The existing adapter example
in `tools/hooks/` illustrates one integration; it is not universal installation.
Without an adapter, the entrance instructs an agent to call start and close.
No heartbeat or scheduled watcher is needed, and none is silently installed.
