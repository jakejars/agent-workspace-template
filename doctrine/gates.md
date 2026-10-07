---
id: gates
type: doctrine
status: draft
description: Gate-suite contract. Use when a gate fails or when wiring hooks or CI. Not for executable metadata rules (see doctrine/schema.json).
updated: 2026-10-07
related:
  - type: depends_on
    ref: LOOP.md
  - type: see_also
    ref: doctrine/frontmatter-spec.md
---

# Gates

Integrity gates return 0 only when the checked property holds. Nonzero stops a
clean completion claim or commit. Runtime tripwires are identified separately.

| Tool | Checked property |
|---|---|
| `tools/build_catalog.py --check` | Metadata, filing, IDs/refs, tokens, budgets, journal shape, run traces |
| `tools/skills.py check` | Agent Skills names, directory shape, cue descriptions, required template metadata |
| `tools/check_loop.py` | Per-member graph reachability, dead links, directory coverage |
| `tools/pipeline.py check` | Pipeline metadata, contiguous stages, contracts, executors, and stage budgets |
| `tools/scrub_check.py --staged` | Private literal terms and text-only distribution against Git index |
| `tools/journal_guard.py --staged` | Existing journal mutation against Git index |
| `tools/agnostic_check.py` | Runtime names remain in declared adapter/reference boundaries |
| `tools/check_staged.py` | Scrub/journal original index, then validate metadata/skills/pipelines/graph/neutrality in its isolated snapshot |
| `tools/context.py refresh` | Scrub source, validate metadata/skills/pipelines/graph, atomically cache routing metadata and edges |
| `tools/lifecycle.py status` | Configured Git path and observed lifecycle event results |

## Intervals

| Moment | What runs |
|---|---|
| Session start/resume | Neutral lifecycle start: validate and refresh if source changed |
| Prompt/task query | Cached cue routing, refresh only when stale |
| Successful write | Cheap dirty hint; full graph scan deferred |
| End of changed work / before compaction | Neutral close: validate/refresh changed source |
| Pre-commit | Exact staged integrity, independently of the context cache |
| Post-commit / checkout / merge | Refresh derived context and record the result |
| CI / release | Source gates, planted-defect suites, focused lifecycle tests, fresh instance, stale report |
| Egress | Scrub the actual outbound material and check its authorization |

Install/check project-local Git wiring with `tools/hooks/install.py`.
Session/prompt/write/close events require an adapter or explicit agent calls;
Git does not provide universal agent-session hooks. See
[lifecycle.md](lifecycle.md) for commands and receipt interpretation.

## Enforcement limits

The runtime journal guard is a tripwire for supported direct writes and common
shell mutations, not a sandbox. Internal runtime errors fail open; staged
journal validation is the fail-closed commit backstop. An uncommitted file can
still be damaged before that backstop, so Git history and checkpoints matter.

Schema validation checks approval shape, not the authenticity of human consent.
A checksum validates bytes, not trust or version history. Staleness is reported
and excluded from ordinary suggestions; records are not automatically deleted.

The source remains runtime-neutral. Exact pointer files, the harness seam,
`tools/hooks/shim.py`, `tools/hooks/settings-example.json`,
`tools/agnostic_check.py`, and Markdown with reciprocal
`runtime_subject: true` declarations are the bounded exceptions. This scan
is a drift detector, not a security boundary.

## Regression suites

`tools/test_gates.py`, `tools/test_gate_corrections.py`, `tools/test_context.py`,
`tools/test_staged.py`, `tools/test_onboarding.py`, `tools/test_hooks.py`,
`tools/test_new.py`, `tools/test_skills.py`, and `tools/test_pipeline.py`
exercise real failures. `tools/test_instance.py` fills a fresh instance, files
all kits, finalizes, works a session, and commits through the actual hooks.
`tools/test_upgrade.py` instantiates `main` with its own tools and executes the
upgrade block in [migrations.md](migrations.md), preserving legacy privacy and
journal protections while exercising context, skills, pipelines, and staged
gates. It reports an explicit skip if `main` is unavailable; CI fetches full
history and that ref so the upgrade runs.
Run suites when changing the template or making a release; ordinary commits
pay for integrity checks only. CI also reports `build_catalog.py --stale`.

Instantiated CI must provision the ignored private-term store out of band.
Template-mode CI has no private terms and must not claim to test a real
workspace's confidentiality from that result.
