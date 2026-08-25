---
id: seams
type: doctrine
status: draft
description: Seam-file semantics. Use when the workspace must cross a boundary. Not for effect governance (see workspace/80_governance/policies.md).
updated: 2026-08-24
related:
  - type: depends_on
    ref: LOOP.md
  - type: see_also
    ref: doctrine/migrations.md
---

# Seams

A seam records any boundary with a sibling member, machine, harness, or network.
Never reach directly; follow what its seam names.

## The five questions

Use these exact ordered headings:

1. **What crosses** — concrete files/fields.
2. **Direction** — in/out/both per artifact.
3. **Inspect point** — observable path, command, or log.
4. **Control point** — flag, gate, credential, or policy that stops crossing.
5. **What never crosses** — non-empty denylist.

Unknown means `stub`; never guess. Inbound material is `agent_proposed` and may
not overwrite human-owned content.

## Opening a seam

1. Copy `_templates/seam.md`; fill id/type/situation cue.
2. Answer all five headings from observed evidence.
3. Link it from `70_seams/INDEX.md` and its consumers.
4. For external effects, name the autonomy class at the control point.

Opening documents permission checks; it grants none.

## Lifecycle

| Status | Means | May be relied on |
|---|---|---|
| `stub` | unanswered heading(s); closed | no |
| `draft` | five evidence-backed answers | only after inspect-point verification |
| `mature` | running system verified; control exercised; `verified_on` set | yes, until stale |

On closure, retain and demote to `stub`; replace answers with closure date/reason.

## Unopened seams

Family-member seams ship `draft`; other expected seams ship `stub` with one line:

```markdown
This seam is not open. Nothing crosses it. To open it, answer the five
questions in doctrine/seams.md from evidence.
```

Do not include five empty headings in a stub; they falsely resemble answers.

## Vendor names

Runtime names are limited to:

| Where | Why |
|---|---|
| `workspace/70_seams/harness.md` | runtime is the subject |
| exact pinned pointer files | runtime is the filename |
| `tools/hooks/shim.py`, `tools/hooks/settings-example.json` | adapter translation; these two files exactly, not the directory |
| `tools/agnostic_check.py` | checked term list |
| markdown declaring `runtime_subject: true` | subject declared in frontmatter |

Other doctrine and content remain runtime-neutral.

The declaration is frontmatter only, at column 0, in a `.md` file, and it is
reciprocal: a file that declares it must name a runtime, and a file that names
one without declaring it still fails.
`grep -rn '^runtime_subject: true$' --include='*.md' .` lists every candidate
declaration — only those inside a terminated frontmatter block count. The
path exceptions above are not
declarations and never surface in that grep; they are the `ALLOWED` and
`POINTERS` sets in `tools/agnostic_check.py`. Adapter code cannot declare; it
stays on the checked list.
