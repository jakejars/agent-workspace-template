# Agent Workspace Template

A small, plain starting point for folders that AI agents work in: one entrance file, three notes
files, one check script and git hooks. Optional memory for assistant workspaces. Bash and git only.

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
| **Assistant** | Project, plus `memory/` (`INDEX.md`, `topics/`, `log/`) and a gitignored `.scrub-patterns` for private terms |

## What is whose

- **Yours:** `AGENTS.md`, `build-notes/`, `memory/`, `scripts/local/` (your own checks, limits and the
  template's location) and `scripts/ceilings.json`. Upgrades never touch them.
- **The template's:** `scripts/*.sh`, `scripts/TEMPLATE_VERSION` and `.githooks/`. Upgrades replace them.

## Versions and upgrades

Each workspace records its version in `scripts/TEMPLATE_VERSION`. `scripts/check.sh full` notes when a
newer one exists; `bin/workspace status <dir>` shows what changed (from `CHANGELOG.md`) and which files
would be replaced; `bin/workspace upgrade <dir> --yes` applies it. Folders with the old layout from
before 3.0 are moved once instead: `docs/moving.md`.

## More

- `docs/checks.md`: what the gate checks and why.
- `docs/moving.md`: moving an old-layout workspace to 3.0.
- `tests/selftest.sh`: sets up both starts in a temporary folder and proves the checks.

MIT licensed.
