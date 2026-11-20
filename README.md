# Agent Workspace Template

A starting point for any folder you want an AI agent (Claude Code, Codex, Gemini and others) to work
in. It gives the agent a front door to read, a place to keep notes between chats, and a check it must
pass before it says "done".

## Why you might want this

AI agents forget everything when a chat ends. Each new chat starts from zero: the agent does not know
what the project is, what you decided last week, or how you like things done. It also tends to say
"finished" when it is not.

This template fixes that with plain text files that live in your folder:

- **`AGENTS.md`**: the front door. A short page that says what this folder is and the rules. Every
  agent reads it first.
- **`build-notes/`**: three notes. What the project is, what is being worked on now, and your taste
  (the look, tone and choices you like).
- **`memory/`** (assistant workspaces only): what the agent has learned over time, with an index so it
  finds things fast.
- **`scripts/check.sh`**: a check the agent runs before it says "done". If the check fails, the work is
  not done.

Everything is ordinary text and git. No app, no account, no database. You can read and edit every file
yourself, and any agent can use it.

## What you need

A Mac or Linux computer with `bash`, `git` and `python3`. Most already have them. Nothing else to
install.

## Install

### The easy way: ask your agent

Open your agent in any folder and paste this message. Change the folder path to the one you want.

```text
Set up a new workspace from the Agent Workspace Template for me.
1. If ~/Projects/agent-workspace-template does not exist, clone
   https://github.com/jakejars/agent-workspace-template.git to it.
2. Run: ~/Projects/agent-workspace-template/bin/workspace init project ~/Projects/my-app
   (Use "init assistant" instead of "init project" if this folder is for a personal assistant
   that needs memory, not for a code project.)
3. Ask me short questions to fill every <...> blank in AGENTS.md and build-notes/.
4. Run scripts/check.sh and fix what it reports.
5. Tell me in plain words what you made.
```

### By hand

```sh
git clone https://github.com/jakejars/agent-workspace-template.git ~/Projects/agent-workspace-template
~/Projects/agent-workspace-template/bin/workspace init project ~/Projects/my-app        # a code project
~/Projects/agent-workspace-template/bin/workspace init assistant ~/workspaces/my-agent  # an assistant, with memory
```

Then fill the `<...>` blanks in `AGENTS.md` and `build-notes/`, run `scripts/check.sh`, and tell your
agent: "Read AGENTS.md and help me with my current task."

Setup never overwrites a file that is already there, so it is safe to run in a folder that has work in
it.

**Which one?** Pick **project** for software or anything with code. Pick **assistant** for a
general helper (life admin, research, writing) that should remember things between chats.

## Update

The template gets new versions. Your workspace records the version it is on in
`scripts/TEMPLATE_VERSION`. An update replaces only the template's own files. It never touches your
notes, your memory, your rules or your own checks.

### The easy way: ask your agent

```text
Update this workspace to the latest Agent Workspace Template.
1. In ~/Projects/agent-workspace-template, run git pull.
2. Run: ~/Projects/agent-workspace-template/bin/workspace status .
3. Tell me in plain words what the new version changes and what I need to do. Wait for my yes.
4. After my yes, run: ~/Projects/agent-workspace-template/bin/workspace upgrade . --yes
5. Do any "What to do" steps from the changelog, run scripts/check.sh full, and commit.
```

### By hand

```sh
cd ~/Projects/agent-workspace-template && git pull
bin/workspace status ~/Projects/my-app          # what changed and which files it would replace
bin/workspace upgrade ~/Projects/my-app --yes   # apply it
```

`scripts/check.sh full` also tells you when a newer version exists. `CHANGELOG.md` explains each
version in plain words, with a "What to do" line.

## Move an existing workspace onto this template

You may already have a folder your agent works in, made some other way or made from an old version
of this template (once called Sett, with folders like `workspace/`, `20_intent/` and `tools/`). You can
move it onto this template without losing anything. Old files go into an `archive/` folder. Nothing is
deleted, and git keeps the full history.

### The easy way: ask your agent

```text
Move this folder onto the Agent Workspace Template. Do not change anything until I say yes.
1. If ~/Projects/agent-workspace-template does not exist, clone
   https://github.com/jakejars/agent-workspace-template.git to it.
2. Read ~/Projects/agent-workspace-template/docs/moving.md and follow it.
3. First show me a short plan: which files move to archive/, which open tasks look stale,
   and which facts are worth keeping in the new notes. Wait for my yes.
4. Make sure everything is committed and pushed before you move anything.
5. When done, run scripts/check.sh full, commit, and tell me in plain words what changed.
```

### By hand

Follow the nine steps in `docs/moving.md`. In short: commit and push, `git mv` the old layout into
`archive/`, run `bin/workspace init`, copy what is still true into `AGENTS.md` and `build-notes/`, then
run `scripts/check.sh full`.

## What you get

| Start | Files |
| --- | --- |
| **Project** | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `build-notes/` (project, task, taste), `scripts/check.sh` and its checks, `.githooks/` |
| **Assistant** | Everything in Project, plus `memory/` (`INDEX.md`, `threads/`, `topics/`, `log/`) and a private `.scrub-patterns` file for words that must never be shared. See `docs/memory.md` |

## Who owns which files

- **Yours:** `AGENTS.md`, `build-notes/`, `memory/`, `scripts/local/` (your own checks and limits) and
  `scripts/ceilings.json`. Updates never touch them.
- **The template's:** `scripts/*.sh`, `scripts/TEMPLATE_VERSION` and `.githooks/`. Updates replace them,
  so do not edit them. Put your own checks in `scripts/local/checks.sh`.
- **The harness's:** `.harness/`. A harness is the program that runs your agent. Some harnesses learn
  from past work and keep what they learn here. Agents read this folder but never edit it, and git
  ignores it. See `docs/harness.md`.

## For advanced users

### Agent hooks

Hooks are small scripts an agent runs at set moments. Setup writes hook settings for Claude Code
(`.claude/settings.json`), Codex (`.codex/hooks.json`), Antigravity (`.agents/hooks.json`) and qsh
(`.qsh/workspace.json`). They run `scripts/hooks/`:

- at session start: give the agent its context
- before a tool runs: block risky moves (skipping the git hooks, force-push, hard reset, deleting
  outside the project, editing an old log entry or a template file, writing a private term)
- after each edit: run a quick check
- before stopping: remind the agent to run the full check

Claude Code and Antigravity run them. Codex 0.166 did not run project-level hooks in our tests; there
the git hooks still enforce the check. An agent can get around hooks, so the check and its receipt are
the real proof.

### Enforcement contract

A harness that can enforce rules (not only ask for them) reads a contract. Its format is in
`docs/checks.md`, "Enforcement contract". It locks the template's files and the limits files, keeps the
Rules section of `AGENTS.md` in view through long chats, and accepts "done" only when
`scripts/check.sh --json` passes, or when `build-notes/task.md` says `State: blocked` with a reason.
Anything in it that runs project code waits for your OK in that harness.

### More reading

- `docs/checks.md`: what the check looks at and why.
- `docs/project-docs.md`: a project's own docs, the frontmatter agents use to find them, and the
  generated index.
- `docs/memory.md`: threads, topics and runs, the three levels of an assistant's memory.
- `docs/harness.md`: the `.harness/` folder, who writes it, who reads it, how it stays safe.
- `docs/moving.md`: moving an old-layout workspace onto this template.
- `tests/selftest.sh`: builds both kinds of workspace in a temporary folder and proves the checks work.

MIT licensed.
