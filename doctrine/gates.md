---
id: gates
type: doctrine
status: draft
description: Gate-suite contract. Use when a gate fails or when wiring hooks or CI. Not for executable metadata rules (see doctrine/schema.json).
updated: 2026-08-24
related:
  - type: depends_on
    ref: LOOP.md
  - type: see_also
    ref: doctrine/frontmatter-spec.md
---

# Gates

## The three rules

1. Fail closed when a property cannot be proved.
2. Treat any non-zero result as a stop.
3. Emit deterministic `path:line: message` diagnostics.

Exit: **0** clean · **1** violation · **2** usage/runtime failure.

## The suite

| Tool | Checks | Fails on |
|---|---|---|
| `tools/build_catalog.py` | schema, filing, refs, tokens, edge fields, approvals, seams, limits, boot, provenance, journal entry shape, run-to-journal trace, stray sentinel; `--check` writes nothing | any violation; no output on failure |
| `tools/check_loop.py` | per-member three-hop reachability, links, door coverage, `lists` glob bounds, member boundaries | orphan, dead/illegal edge, unbounded glob, omission, excess hop |
| `tools/journal_guard.py` | existing journal entry mutation; agent writes to the private store, `tools/`, the entrance, the sentinel | mutation or sealed write; blocked mode exits 2 |
| `tools/scrub_check.py` | private terms, staged ignore config, text-only tracked content; redacted diagnostics | hit, binary/unreadable/config/private-list failure |
| `tools/agnostic_check.py` | runtime names and bounded pointer shape | leak or malformed pointer |
| `tools/test_gates.py` | planted core violations | a gate accepts a defect |
| `tools/test_gate_corrections.py` | regressions for corrected defects | regression |
| `tools/test_instance.py` | a fresh instance: fill, every kit, a session, a commit | anything a stranger would hit |

`test_instance.py` is the release gate, not a commit gate: it builds a whole
instance and commits inside it, so a commit hook would make every nested
test-commit pay for another one. CI runs it on every push.

Runtime-name exceptions: `workspace/70_seams/harness.md`; exact root/workspace
pointer files; `tools/hooks/`; and `tools/agnostic_check.py`.

## Fail direction, honestly

Runtime `journal_guard.py` deliberately allows internal failure (exit 1); exit 2
means a proven block. The staged pre-commit check is the fail-closed backstop.
Git hooks are opt-in per clone:

```sh
git config core.hooksPath .githooks
```

Other gates fail closed as ordinary processes.

## When they run

| Moment | Gates |
|---|---|
| Every write to `30_memory/journal/` | `journal_guard.py` (hook) |
| Session close | validator then loop; catalogs not required |
| Pre-commit | staged scrub first; then journal, validator, loop, agnostic, selftest, regressions |
| Egress/extraction | scrub + agnostic + full suite |
| CI, every push | full suite plus `build_catalog.py --stale`; stale is reported, not enforced |

CI must provision `.sett-private/never-share.txt` out-of-band for an
instantiated workspace, or deliberately run template (sentinel) mode; a
red scrub gate is never a reason to drop it.

## Adding a gate

Name the enforced law and observed failure; order cheapest-first and wire every
relevant run point.
