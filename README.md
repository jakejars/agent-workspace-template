# Agent Workspace Template

A small, plain starting point for folders that AI agents work in: one entrance file, three notes
files, one check script and git hooks. Optional memory for assistant workspaces. Needs bash, git and
python3 (the hooks and the ceilings check use it to read JSON); nothing to install.

## Two ways to start

```sh
git clone <this repository> ~/Projects/agent-workspace-template
~/Projects/agent-workspace-template/bin/workspace init project ~/Projects/my-app       # a code project
~/Projects/agent-workspace-template/bin/workspace init assistant ~/workspaces/my-agent  # adds memory/
```

Then fill the `<...>` brackets in `AGENTS.md` and `build-notes/`, run `scripts/check.sh`, and tell your
agent: "Read AGENTS.md and help me with my current task." Setup never overwrites a file that exists.

| Start | You get |
| --- | --- |
| **Project** | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `build-notes/` (project, task, taste), `scripts/check.sh` and its checks, `.githooks/` |
| **Assistant** | Project, plus `memory/` (`INDEX.md`, `threads/`, `topics/`, `log/`) and a gitignored `.scrub-patterns` for private terms. Three zoom levels: `docs/memory.md` |

## What is whose

- **Yours:** `AGENTS.md`, `build-notes/`, `memory/`, `scripts/local/` (your own checks, limits and the
  template's location) and `scripts/ceilings.json`. Upgrades never touch them.
- **The template's:** `scripts/*.sh`, `scripts/TEMPLATE_VERSION` and `.githooks/`. Upgrades replace them.

## Versions and upgrades

Each workspace records its version in `scripts/TEMPLATE_VERSION`. `scripts/check.sh full` notes when a
newer one exists; `bin/workspace status <dir>` shows what changed (from `CHANGELOG.md`) and which files
would be replaced; `bin/workspace upgrade <dir> --yes` applies it. Folders with the old layout from
before 3.0 are moved once instead: `docs/moving.md`.

## Agent hooks

Setup also writes hook configs for Claude Code (`.claude/settings.json`), Codex (`.codex/hooks.json`),
Antigravity (`.agents/hooks.json`) and qsh (`.qsh/workspace.json`, the enforcement contract). They run `scripts/hooks/`: context at session start, guards before a
tool runs (skipping the git hooks, force-push, hard reset, deleting outside the project, editing an old
log entry or a template file, writing a private term), a check after each edit, and a reminder to run
the gate before stopping. Claude Code and Antigravity are seen to run them. Codex 0.166 did not run
project-level hooks in our tests; there the git hooks still hold the gate. Hooks are a convenience an
agent can bypass; the gate and the receipt are the proof. A harness that can enforce rules instead of
asking for them reads a contract (format: `docs/checks.md`, "Enforcement contract"): the template's files
and the limits files locked, the Rules section of `AGENTS.md` pinned through compaction, and "done"
accepted only when `scripts/check.sh --json` passes, or from `State: blocked` with a reason in
`build-notes/task.md`. Anything in it that runs project code waits for your OK in that harness.

## More

- `docs/checks.md`: what the gate checks and why.
- `docs/project-docs.md`: a project's own docs: frontmatter agents route by, the generated index, freshness.
- `docs/memory.md`: threads, topics and runs: the three zoom levels of an assistant's memory.
- `docs/moving.md`: moving an old-layout workspace to 3.0.
- `tests/selftest.sh`: sets up both starts in a temporary folder and proves the checks.

MIT licensed.
