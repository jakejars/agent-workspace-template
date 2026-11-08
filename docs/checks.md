# What the gate checks

`scripts/check.sh` is the one gate. The pre-commit hook runs it fast; the pre-push hook runs it full.
Every run writes a receipt (a hash of the working tree, the mode, the result, the time) to the git
folder; `scripts/check.sh receipt` shows it and says whether the files have changed since.

| Check | Where | Fails when |
| --- | --- | --- |
| Stack checks | `check.sh` | format, lint or tests fail for the stack it finds (Rust, Node, Python, C) |
| Ceilings | `check-ceilings.sh`, only with `scripts/ceilings.json` | a count that may not rise (ignored tests, lint suppressions, TODOs) rises |
| Line ceilings | `check-lines.sh`, always | `AGENTS.md` passes 40 lines, `project.md` 120, `task.md` 80, `memory/INDEX.md`, a topic or a thread 150 |
| Private terms | `check-memory.sh`, with `memory/` | a line of `.scrub-patterns` appears in any file, or `.scrub-patterns` is missing or not gitignored |
| Append-only log | `check-memory.sh`, with `memory/` | anything committed under `memory/log/` (entries, run folders, deliverables) was edited or deleted (full mode also checks unpushed commits) |
| One hop | `check-memory.sh`, with `memory/` | a topic or thread has no row in `memory/INDEX.md`, or the index links to a missing file |
| Runs and threads | `check-memory.sh`, with `memory/` | a log folder has no `run.md`; a thread has no `State:` line. Warns (never fails) when a run names no thread or a live thread is 60 days untouched |
| Your checks | `scripts/local/checks.sh` | whatever you add there |
| Template version | `template-status.sh`, full mode | never fails; prints a note when a newer template exists |

`scripts/check.sh --json` (and `receipt --json`) give the same results as one JSON object for harnesses:
each check's name, status, warnings and failing output, the tree hash, and whether the tree still matches.

Stopping: the before-stop hook asks for a passing gate when files changed. The other honest exit is
`State: blocked` in `build-notes/task.md` with the reason under "Open or risky".

Line limits can be changed in `scripts/local/limits.env`, with the reason in the same commit. Agents
cannot change that file or an existing `scripts/ceilings.json`; the owner does. The
checks are rules a tool can see; anything that needs judgement belongs in `AGENTS.md` or a review.

## Enforcement contract

Hooks ask an agent to follow the rules; a harness that can enforce them reads one JSON file instead, written
by `bin/workspace` into that harness's own folder (today `agents/qsh.json` → `.qsh/workspace.json`; another
harness gets its own `agents/<name>.json`). Same fields for every harness:

| Field | Meaning |
|---|---|
| `hooks` | the `scripts/hooks/` scripts to run (session start, before a tool, after an edit) |
| `hook_env` | variables the hooks get, e.g. `AGENT_HARNESS`, and `RULES_PINNED=1` when the harness pins the Rules itself |
| `gate` | the checks that decide "done" (`scripts/check.sh --json`), skipped when nothing outside `build-notes/` changed |
| `blocked` | the honest way out: `State: blocked` in `build-notes/task.md`, reason under "Open or risky" |
| `notes` | the file to rewrite before stopping when other files changed |
| `locked_paths`, `append_only_once_committed` | files the agent may read but never change |
| `review_on_change` | files whose changes the owner should see (`scripts/local/checks.sh` decides what the gate runs) |
| `pinned_rules` | the `AGENTS.md` section that goes with every request, whatever a summary drops |
| `docs` | the docs folder, for a harness that lists docs and points at the one governing a file |

What only takes rights away (locks, pinned rules) can apply at once; anything that runs project code (hooks,
the gate) should wait for the owner's OK in that harness.
