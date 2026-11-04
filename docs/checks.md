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

Line limits can be changed in `scripts/local/limits.env`, with the reason in the same commit. The
checks are rules a tool can see; anything that needs judgement belongs in `AGENTS.md` or a review.
