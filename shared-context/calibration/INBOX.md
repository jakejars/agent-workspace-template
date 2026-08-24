---
id: commons-calibration-inbox
type: register
status: draft
description: Calibration candidate register. Use when filing or checking an open candidate. Not for candidate format (see shared-context/calibration/README.md).
scope: shared
owner: shared
updated: 2026-08-24
related:
  - type: canonical
    ref: shared-context/calibration/README.md
---

# Calibration inbox

Every candidate file in this chamber has a row here, newest first. A
candidate that is not listed is not filed: the file is the content,
this table is the queue, and a workspace checking "is one already open
on this target?" reads only this table.

Rows are appended above the marker and never edited. A state change is
a new row naming the candidate it supersedes — the same append-only
rule the rest of the store runs on.

`state` is one of `filed` · `triaged` · `promoted` · `rejected` ·
`parked` · `superseded`. Only a human moves a candidate out of
`filed`. Promotion names the `CHANGES.md` trailer that carried the
edit; rejection carries one line of why, because the why is what stops
the refile.

| filed | candidate | target | filed_by | state | disposed |
|---|---|---|---|---|---|

<!-- ledger: append above this line -->

Empty is the normal state of a healthy commons: it means every
workspace's view of the principal currently agrees with this store.
