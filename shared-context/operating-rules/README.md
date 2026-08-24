---
id: commons-operating-rules-index
type: policy
status: draft
description: Shared operating rules. Use when work style must be consistent across workspaces. Not for disclosure bounds (see shared-context/boundaries/README.md).
scope: shared
owner: human
provenance: authored
updated: 2026-08-24
tokens: true
---

# Operating rules

How <<PRINCIPAL_NAME>> wants work done. A rule earns a place here by
being true across workspaces; a rule that only holds for one project
stays in that workspace and is not the commons' business.

## What files live here

One rule per file, `type: policy`, `owner: human`. Common shapes:

| File | Holds |
|---|---|
| `voice.md` | How output should read: register, length, what to never sound like |
| `working-style.md` | How to proceed: how much to ask, when to just do it, what "done" means |
| `escalation.md` | What is worth interrupting the principal for, and in what form |
| `defaults.md` | Standing answers to questions that would otherwise be asked every session |

Created on demand, listed in the table in the same edit.

## What makes a rule

Each file states, in this order:

1. **The rule**, one sentence, imperative.
2. **The cue** — when it applies, so a workspace can route on the
   description without loading the file.
3. **The exception**, if any. A rule with no stated exception is
   absolute and will be treated as such.
4. **The origin** — `provenance:`, and for a promoted rule, the
   calibration candidate it came from.

A rule that cannot be written this way is not a rule yet. It is an
observation, and it goes to
[`../calibration/README.md`](../calibration/README.md).

## Precedence

Shared outranks local *here*: a workspace's local working-style file
does not override this chamber. A workspace that finds a rule wrong in
practice files a candidate; it does not quietly stop following it, and
it does not write a local rule that contradicts one here.

The exception is scope: these rules govern *how* work is done, never
*whether* an action is permitted. Permission lives in the workspace's
own autonomy classes and in
[`../boundaries/README.md`](../boundaries/README.md), and no rule here
can loosen either.

## Compact-view discipline

Files here remain `cue`. Only a terse, promoted rule may be distilled into a
workspace's local boot view. That structural change follows
[`../_meta/governance.md`](../_meta/governance.md).
