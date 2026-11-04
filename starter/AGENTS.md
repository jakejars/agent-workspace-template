# AGENTS.md: <project>

**<project>** is <one sentence: what it is and for whom>. This is the one entrance for every agent;
`CLAUDE.md` and `GEMINI.md` point here. Facts only; keep it under 40 lines.

## Read first
1. `build-notes/task.md`: what exists, what was verified, the next action. Check it against the repo
   before acting; rewrite it before you stop.
2. `build-notes/project.md`: what this is, how it is built, what is decided and why.
3. `build-notes/taste.md`: the owner's standing preferences, in their words.
4. `memory/INDEX.md`, if present: what is remembered and where; its rules are at its top.

## Commands
| Do this | Run this |
|---|---|
| Run it | `<command>` |
| Fast gate, before every commit | `scripts/check.sh` |
| Full gate, before a push or a handover | `scripts/check.sh full` |
| Show what was last checked | `scripts/check.sh receipt` |

## Rules
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
| `build-notes/` | current truth: project, task, taste |
| `scripts/` | the gate and its checks; `scripts/local/` is this project's own |
| `<src>` | <what lives there> |
