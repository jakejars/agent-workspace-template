---
id: memory-procedures
type: doctrine
status: draft
description: Procedures. Use when a proven sequence should not be re-derived. Not for executable capabilities (see workspace/60_capabilities/INDEX.md).
scope: workspace
owner: agent
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/30_memory/INDEX.md
  - type: contrast_with
    ref: workspace/60_capabilities/INDEX.md
fields:
  - name: version
    for: procedure
    required: true
  - name: verified_on
    kind: date
    for: procedure
    required: true
  - name: verified_by
    values: [human, agent]
    for: procedure
    required: true
  - name: preconditions
    kind: list
    for: procedure
    required: true
---

# procedures/ — how, versioned

One judgment-complete procedure per `<slug>.md`, `type: procedure`.

## Required beyond the OKF core

```yaml
version: MAJOR.MINOR             # semver-ish; see below
verified_on: YYYY-MM-DD          # last time someone ran it end to end
verified_by: human | agent
preconditions: [...]             # what must be true before step 1
```

## Versioned like code

- **MINOR:** same outcome; edit, bump, append changelog.
- **MAJOR:** tool/effect/result change; bump, record break and pinned callers.
- **Replacement:** new approach/file with `supersedes`; demote and retain old.

Every file ends with a changelog, newest-first, append-only:

```markdown
## Changelog
<!-- ledger: append above this line -->
```

Line: `YYYY-MM-DD · vX.Y · change · reason`; append corrections.

## Verification

State toolchain drift since `verified_on`; `review_after` drives `--stale`.
External steps name autonomy class and stop for B/C approval. A procedure is
not approval.

## Boundary with capabilities

Procedures are instructions; capabilities are checksummed installable artifacts
arriving through the registry seam. Repeated automation becomes a capability.

Agent-proposed factual evidence may guide reversible work provisionally after
checking its source, scope, and freshness. It grants no policy or permissions.
Human promotion remains required for standing authority and mature status.
