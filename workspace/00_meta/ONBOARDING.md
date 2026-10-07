---
id: onboarding
type: doctrine
status: draft
description: Instance setup walk. Use when `.uninitialised` exists. Not for token definitions (see placeholders.md).
scope: workspace
owner: human
updated: 2026-10-07
related:
  - type: canonical
    ref: workspace/00_meta/placeholders.md
  - type: depends_on
    ref: workspace/AGENTS.md
---

# Onboarding

Most users create a workspace with the source checkout's `tools/new.py`
wizard; this document owns manual, interrupted, and agent-led instance setup.
While `.uninitialised` exists, finish or resume setup. The `.initializing`
checkpoint distinguishes a mechanical fill from a ready workspace. Family
maintenance never runs this walk.

## 1. Reuse answers, ask only for gaps

Use values supplied in the request or a referenced configuration. Ask for the
working name and workspace ID if missing. Batch related optional questions;
never require a twelve-question interview before local work can begin.
Email, organisation, machine reference, and optional family paths may be empty.
Empty means unconfigured, never invented personal or machine facts.

Write non-secret answers to `00_meta/values.json`. The
[placeholder registry](placeholders.md) defines the fields.
`values.json` is tracked in Git. It is for non-secret configuration only.
Never place credentials, private literal terms, or other never-share values
in it. Names and values
that must never leave belong only in the ignored private store, never JSON.
The human configures `.workspace-private/never-share.txt` locally, or explicitly
records no literal terms as described in `80_governance/boundaries.md`; an agent may
explain the format but must not ask for secrets in a model conversation. An
explanation may be given in conversation. If a durable local procedure is
needed, file it under `30_memory/procedures/`; never write explanatory content
into `.workspace-private/`, which holds only the ignored private configuration
itself.

## 2. Mechanical fill

```sh
python3 tools/instantiate.py --minimal
```

Only `tokens: true` consumers are filled. Unlinked optional seams close.
The script records a fill checkpoint and birth event, but **keeps the sentinel**.
An interrupted fill resumes from the same saved answers. Do not change the
answers mid-fill. A completed fill is not readiness.

## 3. First task and relevant seams

Capture the first intent using `_templates/intent.md`, including a short current
checkpoint. Finalization requires a first active intent: during onboarding,
capture the user's first real objective, not "set up the workspace" housekeeping. The
housekeeping-first prohibition does not block this required capture; it
prevents setup chores from replacing the user's actual objective.
Use the user's actual objective, constraints, and authorization.
Link it from the active directory or its declared pattern. Open only the seams
needed now; optional commons, registry, and library may stay closed.
Machine facts may be observed through authorized tools when needed; a machine
reference document is optional, and its absence does not prevent other work.

## 4. Hook disposition

Install the runtime-neutral Git hooks with `python3 tools/hooks/install.py`.
Choose portable commands, or explicitly configure an adapter for the current
runtime. See `doctrine/lifecycle.md` for event intervals and observed receipts.
Declining automatic runtime hooks is valid; start and close remain explicit
commands in the entrance. Merely copying an example does not prove it fires.

## 5. Verify and finalize

```sh
python3 tools/instantiate.py --finalize --hooks portable
python3 tools/instantiate.py --check
```

Use `--hooks runtime` only to record the decision to use a runtime adapter;
it does not claim its installation or invocation. Finalization requires an
active intent, an explicit hook disposition, an explicit instance private-term configuration,
and passing metadata, graph, scrub, and neutrality gates. A failure retains
the setup markers. The ready receipt is written only after successful checks,
and the sentinel is removed last in the readiness transition.

A later ordinary session starts with the entrance and current task. It never
replays the onboarding interview or resumes an arbitrary old handover.
