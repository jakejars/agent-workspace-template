---
id: disclosure
type: doctrine
status: draft
description: Disclosure tiers and boot budgets. Use when setting load or reducing context. Not for metadata fields (see doctrine/frontmatter-spec.md).
updated: 2026-08-24
related:
  - type: depends_on
    ref: doctrine/frontmatter-spec.md
  - type: see_also
    ref: doctrine/gates.md
---

# Disclosure

## Tiers

| `load` | Meaning |
|---|---|
| `always` | Eligible for an entrance's explicit static manifest; requires `mature` |
| `cue` | Open when the task matches `description`; default |
| `drill` | Open only from an explicit, already-relevant link |

`load` never adds a file to boot by itself. For ordinary workspace sessions,
the `workspace/AGENTS.md` frontmatter manifest is the single source of truth.

## Ordinary workspace boot

| Part | Cap | Selector |
|---|---:|---|
| static | 7,000 chars | `boot_static`, in order |
| dynamic | 3,000 chars | greatest parsed UTC `closed_at` among `boot_dynamic` matches |
| total | 10,000 chars | static + selected dynamic |

Frontmatter counts. Every dynamic candidate is independently capped so an old
handover cannot become an oversized future boot. Every handover is capped,
including non-boot archives. Each match is a `YYYY-MM-DD-<slug>` run's
`type: handover` with UTC `closed_at`. The schema fixes all four limits;
entrance values must equal them. `build_catalog.py --check` accounts exact
characters and writes nothing.

Catalogs, registers, optional family members, and linked external stores are
not ordinary boot inputs. Their descriptions and links route on demand. Shared
truth needed every session is compacted into `workspace/70_seams/SHARED.md` by
an explicit refresh.

## Reading rules

- A cue must identify a situation visible before opening the file.
- Never bulk-read a drill directory; follow only justified links.
- Record a drill source when it changes durable work.
- Promote by moving the canonical file, not by copying its body upward.
- Disclosure tier is not confidentiality; governance controls access.

When a cap binds, reduce or demote content. Do not raise the cap to accommodate
unbounded state.
