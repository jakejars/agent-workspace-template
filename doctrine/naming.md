---
id: naming
type: doctrine
status: draft
description: Naming. Use when creating any file or minting an id. Not for which chamber a file belongs to (see doctrine/filing.md).
updated: 2026-10-07
related:
  - type: see_also
    ref: doctrine/filing.md
  - type: see_also
    ref: doctrine/migrations.md
---

# Naming

## Paths are kebab-case

Files use lowercase ASCII kebab-case and `.md`; no spaces, underscores, or
capitals. A date may prefix a file only when the record itself is an event or
period; never merely to impose ordering. Door-defined examples include journal
events, runs, approvals, and calibration candidates.

```text
30_memory/procedures/rotate-api-credentials.md      yes
30_memory/procedures/Rotate API Credentials.md      no
30_memory/journal/2026-08-24-1412-registry-fail.md  yes  (an event)
80_governance/approvals/2026-08-24-dp-001.md         yes  (an event)
shared-context/calibration/2026-08-24-tone.md        yes  (an event)
30_memory/facts/2026-08-24-build-times.md            no   (gratuitous order)
30_memory/journal/2026-08.md                        no   (not a period)
```

Exceptions: `AGENTS.md`, pointer files, `README.md`, `INDEX.md`, `LOOP.md`,
`NAMESPACE.md`, `CATALOG.md`, `SHARED.md`, `LICENSE`; numeric chamber directories
retain underscores.

## The machine-read subset

Machine syntax: inline Markdown links; `related`/`supersedes` refs; restricted
frontmatter; private-list line terms (`.workspace-private/never-share.txt`);
`lists` and ledger comments; `<<TOKEN>>` and `{{marker}}`. Reference-style
links confer no edge.

## Where the root is

The workspace root is the nearest ancestor containing `NAMESPACE.md`. Bare paths
resolve there; `./` and `../` resolve from the source. Members never link into
siblings except through `70_seams/`; family-level files are not siblings.

## Minting an id

Mint once from the initial filename: kebab-case, repo-unique, no chamber prefix.
Never change or reuse it; replacements mint a new id and name `supersedes`.
Prefer ids in frontmatter because they survive moves; use paths for clickable
prose.

## No numeric prefixes inside chambers

The spine is numbered. Nothing below it is.

```text
50_registers/open-loops.md            yes
50_registers/01-open-loops.md         no
30_memory/facts/03-build-times.md     no
40_knowledge/decisions/0003-cache.md  yes  (the one exception, below)
```

Only `40_knowledge/decisions/NNNN-slug.md` may use a numeric child prefix:
four-digit, monotonic, never renumbered. Other ordering belongs in data:

- chronological ordering → `updated:` and the ledger convention
  (append-only, newest-first, `<!-- ledger: append above this line -->`);
- deliberate ordering → the chamber's `INDEX.md`, which lists files in
  the order a reader should meet them;
- precedence → `scope:` and `precedence: protected`.

## Why the chambers are numbered

Chamber numbers encode the fixed dependency spine, make lexical order semantic,
and leave insertion gaps. These conditions do not apply below chambers.
