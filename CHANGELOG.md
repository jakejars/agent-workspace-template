# Changes

One section per version, newest first. Each says what changed in plain words and what you need to do.
`bin/workspace status` prints the sections newer than the version a workspace is on.

## 3.0.1 (2026-11-04)

Small fixes after a review.
- The private-terms guard checks what an agent writes, not the shell commands it runs, so it can still
  search for a term. The gate still checks every file.
- Notes templates say "the owner" instead of a name.
- README says what is needed (bash, git, python3) and which agents are seen to run the hooks.

What to do: nothing; upgrade when convenient.

## 3.0.0 (2026-11-04)

A rebuild: one small template with two ways to start, instead of the old ten-folder layout.
- One entrance: `AGENTS.md` (under 40 lines, facts only), with `CLAUDE.md` and `GEMINI.md` pointing to it.
- Three notes files in `build-notes/`: `project.md` (what it is and why), `task.md` (what is happening
  now), `taste.md` (the owner's preferences).
- One gate, `scripts/check.sh`, with a receipt that proves which exact files passed.
- Assistant start adds `memory/`: an index, topics updated in place, and an append-only log.
- Kept from the old layout as short checks: private terms never committed, the log only grows, every
  topic reachable from the index, entry files under a line limit.
- Dropped: the numbered folders, record kits, doctrine files, frontmatter schema, catalog and all the
  Python tools.
- New: this version number, upgrade notices, and `bin/workspace upgrade`.

What to do:
- From the old layout: follow `docs/moving.md`. Old files are archived, not deleted.
- From a pre-3.0 project starter: run `bin/workspace upgrade <dir> --yes`, then move any lines you added
  to `scripts/check.sh` into `scripts/local/checks.sh` (the upgrade keeps your old copy beside it).
