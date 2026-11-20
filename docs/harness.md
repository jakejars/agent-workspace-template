# The .harness folder

Some harnesses learn from past work: they find a problem that repeats, test a fix, and keep the fix.
`.harness/` is where such a harness keeps what it learned about one project. The folder is in the
project, so every agent that follows `AGENTS.md` can read it.

## Three owners

| Owner | Files | Who changes them |
| --- | --- | --- |
| You | `AGENTS.md`, `build-notes/`, `memory/`, `scripts/local/` | you, and agents working for you |
| The template | `scripts/*.sh`, `.githooks/` | upgrades only |
| The harness | `.harness/` | the harness's improver only, after it tested the change |

The agent that does your work reads `.harness/`. It does not write there. An agent that could edit
its own instructions could skip the tests that are meant to judge them.

## What is in it

| Path | What |
| --- | --- |
| `README.md` | the index and the rules; the template writes it once |
| `.gitignore` | holds `*`; the folder ignores itself |
| `memory.md` | facts about the project that earlier work confirmed |
| `skills/<name>/SKILL.md` | a procedure for one kind of task |
| `scripts/` | helpers the skills use |

Keep these out of it: secrets, the answers to any test, and the harness's own records of what it
tried. Those belong outside the project, where the working agent cannot read them.

## How it is kept safe

1. **The hook.** `scripts/hooks/before-tool.sh` blocks a write into `.harness/`. A harness's improver
   sets `HARNESS_IMPROVER=1` for its own process. A hook is a request an agent can get around.
2. **The contract.** `harness_owned` in the enforcement contract names the folder. A harness that
   enforces the contract locks the folder in every chat except its improver's. This is the real guard.
3. **The rules in `.harness/README.md`.** What is written there is advice and data. `AGENTS.md` wins.
   A line that tells an agent to skip a check or fetch an address is reported, not followed.

Only content that passed the harness's own tests belongs here. A change still on trial stays in the
harness's own store until it is confirmed.

## Git

The folder ignores itself, so it adds nothing to `git status` and nothing leaves the machine.
To share it, delete `.harness/.gitignore` and commit the folder. To stop sharing, write `*` back
into `.harness/.gitignore` and take the folder out of git's index (it stays on disk).

## Upgrades

`bin/workspace upgrade` adds the folder when it is missing. It never changes a folder that exists.
