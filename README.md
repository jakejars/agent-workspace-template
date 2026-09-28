# Sett

Sett gives AI agents a durable local workspace for tasks, memory, knowledge,
decisions and boundaries.

It is plain Markdown and stdlib Python. No daemon, no service, no account.

## Requirements

- Git
- Python 3

## Quick start

```sh
git clone https://github.com/jakejars/sett.git
cd sett
python3 tools/new.py ~/setts/my-workspace
```

Then open `~/setts/my-workspace` in your AI agent and say:

> Read `AGENTS.md` and help me with my current task.

That is the whole path. The wizard asks a few plain-English questions — what
your agent should call you, the workspace name, your first objective, and
whether any private terms must never leave the machine — then fills, checks,
and finalizes the workspace for you.

**The cloned `sett` repository is the template/source.** Do not onboard or use
it as your personal workspace; `tools/new.py` creates a standalone workspace
elsewhere, and the wizard refuses a destination inside the checkout. Prefer
manual, interrupted, or agent-led setup? The walk lives in
[`workspace/00_meta/ONBOARDING.md`](workspace/00_meta/ONBOARDING.md).

## How Sett works

One entrance, typed files, progressive disclosure, append-only history,
governed seams, and reachability that is mechanically checked rather than
hoped for.

Five laws:

1. **One entrance.** Sessions start at `AGENTS.md` in the workspace; its
   machine-readable manifest is the complete ordinary boot.
2. **Everything reachable, nothing ambient.** Every content file is within
   three human-authored link hops of its member's entrance. Generated catalogs
   grant no reachability.
3. **Frontmatter is the interface.** Metadata drives routing and traversal;
   evidence and human authorization establish factual trust and permissions.
4. **Current state and history differ.** Task checkpoints update in place;
   journals stay immutable. Provisional evidence is usable after verification;
   standing policy and preference promotion require human direction.
5. **Agent-agnostic.** Neutral files hold the logic. Runtime pointers, adapter
   exceptions, and per-file `runtime_subject` declarations are bounded and
   gate-checked.

## Ordinary work

One active intent with a current checkpoint is the default. Detailed runs,
review packets, and event journals are optional unless an effect or explicit
audit requirement needs them. Select context by task, never latest handover.

```sh
python3 tools/lifecycle.py start
python3 tools/context.py show --query "<task terms>"
python3 tools/context.py show --task <intent-id>
python3 tools/context.py checkpoint --task <intent-id> --text "<state; next step>"
python3 tools/lifecycle.py close
python3 tools/lifecycle.py status
```

Git hooks automatically validate staged changes and refresh context after
commits, checkouts, and merges. Runtime session events call the same neutral
commands through an optional adapter. The generated cache contains metadata
and knowledge-graph edges, with at most three cue suggestions per query.
See [lifecycle](doctrine/lifecycle.md) for precise intervals and observed receipts.

## Workspace structure

| Path | Owns |
|---|---|
| [`LOOP.md`](LOOP.md) | Flows and reachability |
| [`NAMESPACE.md`](NAMESPACE.md) | Reserved paths and the root marker |
| [`doctrine/`](doctrine/INDEX.md) | Mechanics |
| [`_templates/`](_templates/README.md) | Record kits |
| [`tools/`](tools/) | Validators, regressions, the fill, the wizard |

## Optional shared memory, registry, library

| Member | Purpose |
|---|---|
| [`workspace/`](workspace/AGENTS.md) | The sett itself — ten chambers, from identity to runs |
| [`shared-context/`](shared-context/SHARED.md) | Optional governed commons, shared across workspaces |
| [`registry/`](registry/README.md) | Optional checksummed capabilities |
| [`library/`](library/LIBRARY.md) | Optional reference shelf: knowledge and taste |

Keep the ones you want; an unlinked member's seam closes itself during
instantiation. Members are independently extractable, and cross-member
exchange only ever happens through a file in `workspace/70_seams/`.

## Validation and gates

Structural rules have gates and negative tests. Authority and evidence rules
also require judgment; the
[gate contract](doctrine/gates.md) states the limits. On top of that,
`tools/test_instance.py` builds a fresh instance from the current commit, files
one record from every kit, works a session, and commits through the hooks, so
the path a new user takes is the path CI walks on every push.

Read [`doctrine/gates.md`](doctrine/gates.md) for the suite and what each gate
refuses. Verify at any time:

```sh
python3 tools/build_catalog.py --check   # metadata, filing, limits, boot
python3 tools/check_loop.py              # reachability: no orphans, no dead links
python3 tools/test_instance.py           # a whole fresh instance, end to end
```

Health-check any workspace — the source checkout or a generated one:

```sh
python3 tools/doctor.py
```

## Developing the Sett template

Maintaining the template itself starts at the repo-root
[`AGENTS.md`](AGENTS.md), never at the workspace entrance. The two modes do not
combine, and the family checkout is never onboarded.

## Migration and extraction

Adopting an existing folder rather than starting clean? Import follows the
ladder in [`doctrine/installation.md`](doctrine/installation.md) — the source
stays put behind a seam until a rung genuinely fails. Moves, supersession, and
member extraction follow [`doctrine/migrations.md`](doctrine/migrations.md).

Lineage: FAW/OKF, Zettelkasten, Johnny.Decimal, ADRs, BagIt, lazy consensus,
and schema-first metadata systems. License: MIT.
