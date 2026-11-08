---
name: exec-plan
description: Use when a task will touch many files or run longer than about an hour, or will span sessions. Not for small changes.
---
# Exec plan

A plan is a file the next session (or the same one after compaction) can resume from without guessing.
It lives in `build-notes/plans/<slug>.md` while the work runs and moves to `build-notes/plans/done/`
when it is finished. Point `build-notes/task.md` "Next action" at it.

Write it before the first change, keep it current as you go (it is the record, not a proposal), and
keep it short: a plan nobody can read in two minutes stops being read.

## Template

```markdown
# Plan: <what this delivers, one line>
Started: <date>. Status: <active | done | abandoned>.

## Done when
<Observable behaviour a check or a person can confirm, e.g. "`/export` writes a CSV the import reads
back unchanged". Never "code changed".>

## Context
<What a newcomer needs: the files involved, how they fit, terms defined. Facts only.>

## Steps
- [ ] <step>: <how it is verified>

## Decision log
- <date> <decision>, because <reason>; rejected <alternative> because <reason>.

## Surprises
- <what turned out different from the plan, and the evidence>

## Resume
<How to pick this up cold: the command to see where it stands, what is safe to re-run, what to undo
if a step half-ran.>
```

## Rules
- The decision log is required: after compaction it is what stops the work from swinging back to an
  approach already rejected. Log rejected alternatives with their reason.
- "Done when" is behaviour, written before the work, and changed only with the owner's yes.
- Tick a step only when its verification ran and passed; say what you saw.
- One plan per piece of work. If the scope changes, record it in the decision log.
