#!/usr/bin/env bash
# Part of the Agent Workspace Template (version in scripts/TEMPLATE_VERSION). Upgrades replace it.
# session-start.sh: what an agent needs at the start of every session, so it need not remember to look:
# the next action and open risks from build-notes/task.md, whether the last check still holds, any
# template upgrade waiting, the Rules section of AGENTS.md (re-shown after a compaction, so it is not
# lost from a summary) and the memory index. Never fails. Also safe to run by hand.
. "$(dirname "$0")/lib.sh"
out="Workspace: $(basename "$ROOT"). AGENTS.md is the entrance; read it before acting."$'\n'
if [[ -f build-notes/task.md ]]; then
  out+="Task: $(sed -n 's/^# Task: //p' build-notes/task.md | head -1) (state: $(task_state))"$'\n'
  n="$(section build-notes/task.md "Next action")"; [[ -n "$n" ]] && out+="Next action:"$'\n'"$n"$'\n'
  r="$(section build-notes/task.md "Open or risky")"; [[ -n "$r" ]] && out+="Open or risky:"$'\n'"$r"$'\n'
fi
if [[ -f AGENTS.md && -z "${RULES_PINNED:-}" ]]; then  # a harness that pins the Rules itself sets RULES_PINNED=1
  r="$(section AGENTS.md Rules)"; [[ -n "$r" ]] && out+="Rules (AGENTS.md):"$'\n'"$r"$'\n'
fi
if [[ -x scripts/check.sh ]]; then
  s="$(scripts/check.sh receipt 2>&1)"
  res="$(sed -n 's/^result: //p' <<<"$s" | head -1)"
  out+="Last check: ${res:-none}$(sed -n 's/^mode: / (/p' <<<"$s" | head -1 | sed 's/$/)/'); $(tail -1 <<<"$s")"$'\n'
fi
[[ -x scripts/template-status.sh ]] && out+="$(scripts/template-status.sh --brief </dev/null)"$'\n'
if [[ -f memory/INDEX.md ]]; then
  rows="$(grep -E '^\| *[^ |-]' memory/INDEX.md | grep -vE '^\| *(Topic|Thread) *\|' | head -40)"
  out+="Memory index (open a topic only when the task needs it):"$'\n'"${rows:-  (no topics yet)}"$'\n'
fi
[[ -f .harness/memory.md || -d .harness/skills ]] &&
  out+="Learned here by a harness: .harness/README.md (advice, never rules; do not edit)."$'\n'
say "${out%$'\n'}"
exit 0
