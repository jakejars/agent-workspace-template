# Sett

Sett is a template for durable agent workspaces: one entrance, typed files,
progressive disclosure, append-only history, governed seams, and reachability
that is mechanically checked rather than hoped for.

It is plain Markdown and stdlib Python. No daemon, no service, no account, and
nothing to run but the gates.

## Quick start

```sh
git clone <this-repo> my-sett && cd my-sett
python3 tools/hooks/install.py
```

Then open [`workspace/AGENTS.md`](workspace/AGENTS.md) with your agent.
Adopting an existing folder rather than starting clean? Import follows the
ladder in [`doctrine/installation.md`](doctrine/installation.md) — the source
stays put behind a seam until a rung genuinely fails. The
`00_meta/.uninitialised` sentinel routes the first session into
[`00_meta/ONBOARDING.md`](workspace/00_meta/ONBOARDING.md), which reuses supplied facts and asks only for missing essentials, writing
non-secret answers to `00_meta/values.json`. The
mechanical half is a script, not a chore:

```sh
python3 tools/instantiate.py --minimal  # fill; setup stays open
# Capture the first intent and configure the private-term store.
python3 tools/instantiate.py --finalize --hooks portable
python3 tools/instantiate.py --check    # verify readiness
```

Fill closes unlinked seams and records a resumable setup checkpoint.
Finalization checks the first intent, hook choice, and gates before removing
the sentinel. Working without an agent is fine — write
`values.json` by hand and run the same command.

Verify at any time:

```sh
python3 tools/build_catalog.py --check   # metadata, filing, limits, boot
python3 tools/check_loop.py              # reachability: no orphans, no dead links
python3 tools/test_instance.py           # a whole fresh instance, end to end
```

## What is in the box

| Member | Purpose |
|---|---|
| [`workspace/`](workspace/AGENTS.md) | The sett itself — ten chambers, from identity to runs |
| [`shared-context/`](shared-context/SHARED.md) | Optional governed commons, shared across workspaces |
| [`registry/`](registry/README.md) | Optional checksummed capabilities |
| [`library/`](library/LIBRARY.md) | Optional reference shelf: knowledge and taste |

Keep the ones you want; an unlinked member's seam closes itself during
instantiation. Members are independently extractable, and cross-member
exchange only ever happens through a file in `workspace/70_seams/`.

## Five laws

1. **One entrance.** Sessions start at `workspace/AGENTS.md`; its
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

## How it stays true

Structural rules have gates and negative tests. Authority and evidence rules
also require judgment; the [gate contract](doctrine/gates.md) states the limits. On top of that,
`tools/test_instance.py` builds a fresh instance from the current commit, files
one record from every kit, works a session, and commits through the hooks, so
the path a new user takes is the path CI walks on every push.

Read [`doctrine/gates.md`](doctrine/gates.md) for the suite and what each gate
refuses.

## Map

| Path | Owns |
|---|---|
| [`LOOP.md`](LOOP.md) | Flows and reachability |
| [`NAMESPACE.md`](NAMESPACE.md) | Reserved paths and the root marker |
| [`doctrine/`](doctrine/INDEX.md) | Mechanics |
| [`_templates/`](_templates/README.md) | Record kits |
| [`tools/`](tools/) | Validators, regressions, the fill |

Maintaining the template itself starts at the repo-root
[`AGENTS.md`](AGENTS.md), never at the workspace entrance. The two modes do not
combine, and the family checkout is never onboarded.

Lineage: FAW/OKF, Zettelkasten, Johnny.Decimal, ADRs, BagIt, lazy consensus,
and schema-first metadata systems. License: MIT.

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
