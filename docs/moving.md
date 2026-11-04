# Moving an old-layout workspace to 3.0

For folders made from this template before 3.0 (once called Sett): a `workspace/` folder with numbered
folders such as `20_intent/` and `30_memory/`, and Python tools in `tools/`. The move archives the old
files and starts the new shape beside them. Nothing is deleted or rewritten; git keeps the history.

1. **List first.** Show the owner the plan: which folders move to `archive/`, which open tasks look
   stale (they strike any to keep), and which facts look worth promoting. Wait for a yes.
2. **Check it is safe.** The working tree is clean and pushed; the other machines are in sync.
3. **Archive.** `git mv` the old layout into `archive/`: `workspace/`, `tools/`, the numbered folders,
   old entry files and caches. Move private stores (`.sett-private/`, `.workspace-private/`) to
   `archive/private/` and keep them gitignored. Commit: "Archive the pre-3.0 layout".
4. **Set up.** `bin/workspace init assistant <dir>`. It keeps any file that is already there.
5. **Fill the entrance.** Write `AGENTS.md` and `build-notes/project.md` from the old entry files; put
   the owner's preferences in `build-notes/taste.md`; carry live work into `build-notes/task.md`.
6. **Copy private terms.** Put the old never-share terms into `.scrub-patterns`.
7. **Promote only what is live.** Add a `memory/topics/` file only for facts an agent needs now, each
   with a row in `memory/INDEX.md`. Everything else stays readable in `archive/`; promote it the second
   time it is needed.
8. **Close stale tasks.** Old open tasks the owner struck are recorded as closed in one log entry
   (`memory/log/<date>-moved-to-3.0.md`) that lists them.
9. **Prove it.** `scripts/check.sh full` passes; an agent can answer "what is this and what is next"
   from `AGENTS.md` alone. Commit and push.

`archive/` is left out of the line ceilings and the memory checks by design: those check only the new
shape. The private-terms check covers every file, `archive/` included.
