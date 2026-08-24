---
id: intent-satisfied
type: register
status: draft
description: Closed intents. Use when checking completed, abandoned, or superseded wants. Not for active intents (see ../active/README.md).
load: drill
scope: workspace
updated: 2026-08-24
related:
  - type: canonical
    ref: workspace/20_intent/INDEX.md
---

# satisfied/ — what is closed

Named for the common case; it holds all three terminal states. The
file's `lifecycle:` field says which:

| `lifecycle:` | Means | Must also carry |
|---|---|---|
| `satisfied` | The success definition was met | The evidence — what was produced, where it is |
| `abandoned` | Deliberately dropped | Why. An abandoned intent is a finding about what this sett does not do |
| `superseded` | Replaced by a later intent | `superseded_by:` naming that intent's id |

## Rules

1. **Arrival is by `git mv` from `active/`.** History carries the walk;
   the file's body is not rewritten to look like it was always
   finished.
2. **Nothing here is authority.** A closed intent authorises no work.
   Reviving one means capturing a new intent that references it, not
   moving the old file back.
3. **`load: drill`.** This drawer is read when something points at it —
   never bulk-read at boot, never swept into context "for background".
4. **Abandoned entries are the valuable ones.** They are the closest
   thing this chamber has to a dead-end record: before capturing a new
   want, check whether this sett already tried it and stopped. Verified
   dead ends themselves live in `30_memory/dead-ends/`; this drawer
   holds why the *want* was dropped, which is a different fact.
5. **Never prune.** The drawer grows. Its cost is disk; its value is
   that "we already decided not to" stays answerable years later.
