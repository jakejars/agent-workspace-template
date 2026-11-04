# Memory: three zoom levels

For an assistant workspace (`memory/` present). Each level is one file an agent reads whole, with a
ceiling, so neither the agent nor the owner is handed the whole history.

| Level | File | Read when | Ceiling |
| --- | --- | --- | --- |
| Top | `memory/INDEX.md`: Threads and Topics tables | every session (the session-start hook prints it) | 150 lines |
| Middle | `memory/threads/<name>.md` | the task names this thread | 150 lines each |
| Session | `memory/log/YYYY-MM-DD-<slug>/run.md` + deliverables | the thread's run list points at it | none; append-only |

A thread file:

```markdown
# Thread: <name>
State: live. Updated: 2026-11-04.

## Goal
<one paragraph>
## Where it stands
<two or three lines, dated>
## Decisions
- <date>: <decision>, because <why>
## Runs
- 2026-11-04 [first pass](../log/2026-11-04-first-pass/run.md): <one line>
```

A run note (`run.md`) starts with `Thread: <name>` and says what was done, the evidence, the files beside
it, and the next step. Small events (a handover, a dead end, a saved note) stay single log files.

Checks: every thread and topic has an index row and the row points at a real file; every log folder has a
`run.md`; a run note names its thread; nothing committed under `log/` changes; a live thread with no update
for 60 days is a warning in the gate until it is updated, paused or done.
