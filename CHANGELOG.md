# Changes

One section per version, newest first. Each says what changed in plain words and what you need to do.
`bin/workspace status` prints the sections newer than the version a workspace is on.

## 3.4.1 (2026-11-20)

The README is rewritten in plain words for new and experienced users alike.
- Copy-paste messages that tell your agent to install the template, update a workspace, or move an
  existing workspace onto it.
- Short "by hand" steps for each, and a plain explanation of what the files are for.

What to do: nothing. No workspace file changed; `bin/workspace upgrade` only moves the version number.

## 3.4.0 (2026-11-20)

A place for what a harness learns about a project, readable by every agent and written by none of them.
- `.harness/`: made by `init` and `upgrade` when missing, never overwritten. It holds `README.md` (what
  the folder is and its rules) and a `.gitignore` with `*`, so the folder ignores itself: no noise in
  `git status`, and no change to the project's own `.gitignore`. A harness that learns from past work
  writes `memory.md`, `skills/` and `scripts/` there. To share it, delete `.harness/.gitignore`.
- Three owners now: yours, the template's, the harness's. See `docs/harness.md`.
- The before-tool hook blocks an agent's write into `.harness/`. A harness's own improver sets
  `HARNESS_IMPROVER=1`. Session start names the folder once a harness has written to it.
- Enforcement contract: new optional field `harness_owned` (`.harness/**`). A harness that can enforce
  locks the folder in every chat except its improver's. A harness that does not know the field ignores
  it; there the hook is the only guard.
- `AGENTS.md` starter: a "Read first" line for `.harness/README.md`; the Template section is one line.

What to do: `bin/workspace upgrade <dir> --yes` (it adds `.harness/` once). By hand, in `AGENTS.md`
under "Read first", add the `.harness/README.md` line from the starter (optional; keep the file under
40 lines).

## 3.3.0 (2026-11-08)

An enforcement contract any harness can read, docs agents can find, and a plan skill for long work.
- Enforcement contract, schema 2 (fields in `docs/checks.md`; qsh is the first harness to read it, from
  `.qsh/workspace.json`): locks and the pinned Rules apply at once; the gate (`scripts/check.sh
  --json`) and the hooks wait for the owner's OK. The gate is skipped when nothing outside
  `build-notes/` changed. `State: blocked` with a reason ends the task honestly; files changed with
  `task.md` untouched get one nudge to rewrite it. A harness that runs the gate itself needs no
  before-stop hook, so the contract has none. Session start leaves out the Rules when the harness
  pins them (`RULES_PINNED=1`).
- `docs/`, when a project has one: each doc carries frontmatter (`description`, `read_when`, optional
  `governs` + `reviewed`); `scripts/check-docs.sh` checks it, the links and the generated
  `docs/index.md`, and warns when governed code changed after a review. See `docs/project-docs.md`.
- `.agents/skills/exec-plan/SKILL.md`: when and how to keep a plan for long work in
  `build-notes/plans/`, with a required decision log.
- `AGENTS.md` Map names `docs/` and `build-notes/plans/`.

What to do: `bin/workspace upgrade <dir> --yes` (it also adds the exec-plan skill once). By hand, in
`AGENTS.md`'s Map, add the `docs/` row and the `plans/` note from the starter (optional).

## 3.2.0 (2026-11-08)

Gate results a harness can read, an honest way to stop when stuck, and a contract for qsh.
- `scripts/check.sh --json` prints one JSON object: the result, the tree hash, and each check with its
  status, warnings and (when it fails) the tail of its output. Every run also writes
  `last-check.json` beside the text receipt. `scripts/check.sh receipt --json` adds whether the tree
  still matches and exits 0 only when it does.
- Stuck is now a real outcome: `State: active | blocked | done` in `build-notes/task.md`. The
  before-stop hook lets an agent stop without a passing gate only when the state is `blocked` and the
  reason is written under "Open or risky".
- Session start re-shows the Rules section of `AGENTS.md` (also after a compaction, so a summary
  cannot drop it) and the task state.
- Agents can no longer change an existing `scripts/local/limits.env` or `scripts/ceilings.json`: the
  limits the gate enforces are the owner's call. Creating a first `ceilings.json` is still allowed.
- qsh: setup writes `.qsh/workspace.json`, which runs the same hooks and tells qsh what to enforce
  rather than ask: locked paths (template files, the limits files), the Rules section to pin, the
  JSON gate and receipt, and when "done" or "blocked" may be accepted.
- Starter `AGENTS.md` asks for one file up front (`task.md`); `project.md`, `taste.md` and the
  memory index are read when the task needs them. It adds a Done rule.

What to do: `bin/workspace upgrade <dir> --yes`. Your own files are not touched, so by hand:
in `AGENTS.md`, replace "Read first" with the starter's version and add its Done rule to Rules;
in `build-notes/task.md`, add the `State:` line under the Updated line. Both are optional; without
the State line an agent is treated as active.

## 3.1.0 (2026-11-04)

Long-horizon memory in three zoom levels (`docs/memory.md`).
- `memory/threads/<name>.md`: one file per through-line (goal, where it stands, decisions, dated run
  list), updated in place, 150-line ceiling, a row in the Threads table of `memory/INDEX.md`. A live
  thread untouched for 60 days is a gate warning until updated, paused or done.
- Runs with deliverables are folders in the log: `memory/log/YYYY-MM-DD-<slug>/run.md` (names its
  thread) plus the files beside it. Committed log content never changes; a run in progress may still
  edit its own uncommitted `run.md`.
- Checks: every thread indexed, every log folder has a `run.md`, thread ceiling; the agent hooks know
  about threads and treat only committed log content as frozen.

What to do: in an existing assistant workspace, add the Threads table and the rules text from
`assistant/memory/INDEX.md` to your `memory/INDEX.md` (it is yours, upgrades do not touch it), then
`mkdir memory/threads`. Nothing else changes.

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
