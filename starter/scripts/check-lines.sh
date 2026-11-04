#!/usr/bin/env bash
# Part of the Agent Workspace Template (version in scripts/TEMPLATE_VERSION). Upgrades replace it.
# check-lines.sh: line ceilings on the files every agent reads first, so they stay short enough to read.
# Overrides go in scripts/local/limits.env; raise one only with the reason in the same commit.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
LINES_AGENTS=40 LINES_PROJECT=120 LINES_TASK=80 LINES_INDEX=150 LINES_TOPIC=150
[[ -f scripts/local/limits.env ]] && . scripts/local/limits.env

fail=0
cap() {  # cap <file> <max>
  [[ -f "$1" ]] || return 0
  local n; n="$(wc -l < "$1" | tr -d ' ')"
  if (( n > $2 )); then echo "lines: FAIL  $1 has $n lines (max $2)"; fail=1; fi
}
cap AGENTS.md "$LINES_AGENTS"
cap build-notes/project.md "$LINES_PROJECT"
cap build-notes/task.md "$LINES_TASK"
cap memory/INDEX.md "$LINES_INDEX"
shopt -s nullglob
for f in memory/topics/*.md; do cap "$f" "$LINES_TOPIC"; done
(( fail == 0 )) || echo "lines: split the file or move detail out (topics, the log); keep the entry short."
exit "$fail"
