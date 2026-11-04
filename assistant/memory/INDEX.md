# Memory index

What this workspace remembers, at three zoom levels. Read this first; open a thread or topic only when
the task needs it, then at most its last two runs. Never read the log whole.

Rules (checked by `scripts/check.sh`):
- **Threads** (`threads/<name>.md`) are long-horizon through-lines: goal, where it stands (dated), decisions,
  and a dated list of runs. Updated in place, at most 150 lines. Every thread has a row below. Header line:
  `State: live | paused | done. Updated: YYYY-MM-DD.` A live thread untouched for 60 days is warned about
  until it is updated, paused or done.
- **Topics** (`topics/<name>.md`) hold current facts about one subject, updated in place, at most 150
  lines each. Every topic has a row below; a topic with no row fails the check.
- **Log** (`log/`) holds what happened. A small event is one file, `log/YYYY-MM-DD-<slug>.md`. A session
  or run with deliverables is one folder, `log/YYYY-MM-DD-<slug>/` with `run.md` (thread, what was done,
  evidence, files, next step) and the deliverables beside it. Once committed, nothing in the log is edited
  or deleted; correct with a new entry.
- Decisions go in `build-notes/project.md`, preferences in `build-notes/taste.md`, current work in
  `build-notes/task.md` (which names the thread it serves). Memory is for what outlives a task.
- Private terms listed in `.scrub-patterns` (gitignored) may not appear in any file.
- Promote a fact to a topic the second time an agent needs it; don't copy history in ahead of need.

## Threads

| Thread | State | Where it stands | Updated |
| --- | --- | --- | --- |

## Topics

| Topic | What it holds |
| --- | --- |
