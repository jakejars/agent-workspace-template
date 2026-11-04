# Memory index

What this workspace remembers. Read this first; open a topic only when the task needs it.

Rules (checked by `scripts/check.sh`):
- **Topics** (`topics/<name>.md`) hold current facts about one subject, updated in place, at most 150
  lines each. Every topic has a row below; a topic with no row fails the check.
- **Log** (`log/YYYY-MM-DD-<slug>.md`) holds what happened: sessions, handovers, dead ends, approvals.
  Add a new file; never edit or delete an old one.
- Decisions go in `build-notes/project.md`, preferences in `build-notes/taste.md`, current work in
  `build-notes/task.md`. Memory is for facts that outlive a task.
- Private terms listed in `.scrub-patterns` (gitignored) may not appear in any file.
- Promote a fact to a topic the second time an agent needs it; don't copy history in ahead of need.

| Topic | What it holds |
| --- | --- |
