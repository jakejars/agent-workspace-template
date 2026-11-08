# AGENTS.md: <project>

**<project>** is <one sentence: what it is and for whom>. This is the one entrance for every agent;
`CLAUDE.md` and `GEMINI.md` point here. Facts only; keep it under 40 lines.

## Read first
`build-notes/task.md`: what exists, what was verified, the next action. Check it against the repo
before acting; rewrite it before you stop. Read the rest only when the task needs it:
- `build-notes/project.md` for a design or scope decision (what is decided and why);
- `build-notes/taste.md` for anything the owner will see or use (their standing preferences);
- `memory/INDEX.md`, if present, for anything worked on before (open a topic only when needed).

## Commands
| Do this | Run this |
|---|---|
| Run it | `<command>` |
| Fast gate, before every commit | `scripts/check.sh` |
| Full gate, before a push or a handover | `scripts/check.sh full` |
| Show what was last checked | `scripts/check.sh receipt` |

## Rules
- Done: the gate passes and task.md is rewritten. Stuck: set `State: blocked` in task.md, with why.
- Invariants: <rules a change may never break, or "none yet">.
- Ask the owner first before: <actions on real data, releases, accounts, money, anything irreversible>.
- Project checks go in `scripts/local/checks.sh`; `scripts/*.sh` belong to the template (see Template).

## People
<Who owns product and taste decisions, and how they want to be told things.>

## Template
Agent Workspace Template, version in `scripts/TEMPLATE_VERSION`. `scripts/check.sh full` says when
a newer version exists; upgrade with `<template>/bin/workspace upgrade .`.

## Map
| Path | What |
|---|---|
| `build-notes/` | current truth: project, task, taste; `plans/` for long work (skill `exec-plan`) |
| `docs/` | when needed: one topic per doc, frontmatter `description`, `read_when`; index generated |
| `scripts/` | the gate and its checks; `scripts/local/` is this project's own |
| `<src>` | <what lives there> |
