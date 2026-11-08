#!/usr/bin/env bash
# Part of the Agent Workspace Template (version in scripts/TEMPLATE_VERSION). Upgrades replace it.
# before-stop.sh: before the agent ends its turn, asks for the gate and the task notes when files
# changed since the last passing check. Asks once per state of the files, so it never loops.
# An honest way out: State: blocked in build-notes/task.md, with the reason under "Open or risky".
HOOK_EVENT=stop
. "$(dirname "$0")/lib.sh"
[[ "$(get stop_hook_active)" == true ]] && exit 0
[[ -x scripts/check.sh ]] || exit 0
[[ -n "$(git status --porcelain -- . ':!build-notes' 2>/dev/null)" ]] || exit 0  # nothing changed
s="$(scripts/check.sh receipt 2>&1)" && grep -q '^result: PASS' <<<"$s" && exit 0
[[ "$(task_state)" == blocked && -n "$(blocked_reason)" ]] && exit 0  # stuck, and says why
mark="$(git rev-parse --git-dir)/agent-stop-asked"
state="$(git status --porcelain 2>/dev/null | git hash-object --stdin)"
[[ "$(cat "$mark" 2>/dev/null)" == "$state" ]] && exit 0  # already asked about exactly these changes
echo "$state" > "$mark"
block "Before stopping: files changed since the last passing check. Run scripts/check.sh (full before a handover), then rewrite build-notes/task.md (Now, Verified, Next action). If you cannot finish, set State: blocked in build-notes/task.md and say why under Open or risky; never weaken a check to pass it. If this was only exploring, say so and stop."
