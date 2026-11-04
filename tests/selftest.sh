#!/usr/bin/env bash
# selftest.sh: sets up both starts in a temporary folder and proves the checks, hooks and upgrades.
# Run from anywhere: tests/selftest.sh. Prints one line per case; exits 1 if any case fails.
set -uo pipefail
TPL="$(cd "$(dirname "$0")/.." && pwd)"; W="$TPL/bin/workspace"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
export GIT_CONFIG_GLOBAL="$TMP/gitconfig" GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
pass=0 fail=0
ok() { if eval "$2" >/dev/null 2>&1; then echo "  ok    $1"; pass=$((pass + 1)); else echo "  FAIL  $1"; fail=$((fail + 1)); fi; }
no() { ok "$1" "! { $2; }"; }
hook() {  # hook <dir> <harness> <script> <json>: run one agent hook the way that agent would
  (cd "$1" && printf '%s' "$4" | AGENT_HARNESS="$2" CLAUDE_PROJECT_DIR="$1" "$1/scripts/hooks/$3")
}

echo "project start:"
P="$TMP/proj"; "$W" init project "$P" >/dev/null
ok "init made the core" "[[ -f $P/AGENTS.md && -f $P/build-notes/task.md && -x $P/scripts/check.sh ]]"
ok "version recorded" "[[ \$(cat $P/scripts/TEMPLATE_VERSION) == \$($W version) ]]"
ok "agent hooks installed for Claude, Codex, Antigravity" "[[ -f $P/.claude/settings.json && -f $P/.codex/hooks.json && -f $P/.agents/hooks.json ]]"
ok "git hooks switched on" "[[ \$(git -C $P config core.hooksPath) == .githooks ]]"
ok "fast gate passes" "(cd $P && scripts/check.sh)"
ok "first commit through the pre-commit hook" "(cd $P && git add -A && git commit -qm start)"
ok "init again keeps existing files" "$W init project $P | grep >/dev/null 'kept   AGENTS.md'"
for i in $(seq 1 45); do echo "line $i" >> "$P/AGENTS.md"; done
no "line ceiling catches a long AGENTS.md" "(cd $P && scripts/check.sh)"
git -C "$P" checkout -q AGENTS.md

echo "assistant start:"
A="$TMP/asst"; "$W" init assistant "$A" >/dev/null
ok "memory folder and private terms file" "[[ -f $A/memory/INDEX.md && -f $A/.scrub-patterns ]]"
ok ".scrub-patterns is gitignored" "git -C $A check-ignore -q .scrub-patterns"
ok "gate passes" "(cd $A && scripts/check.sh)"
echo "Bellwether" >> "$A/.scrub-patterns"
echo "met Bellwether today" > "$A/memory/log/2026-11-04-first.md"
no "private term in a file fails" "(cd $A && scripts/check.sh)"
echo "met the client today" > "$A/memory/log/2026-11-04-first.md"
ok "clean log entry passes" "(cd $A && scripts/check.sh)"
(cd "$A" && git add -A && git commit -qm start)
echo "edited" >> "$A/memory/log/2026-11-04-first.md"
no "editing an old log entry fails" "(cd $A && scripts/check.sh)"
git -C "$A" checkout -q memory/log/2026-11-04-first.md
echo "# People" > "$A/memory/topics/people.md"
no "topic missing from the index fails" "(cd $A && scripts/check.sh)"
echo "| [people](topics/people.md) | who is who |" >> "$A/memory/INDEX.md"
ok "indexed topic passes" "(cd $A && scripts/check.sh)"
mv "$A/.scrub-patterns" "$TMP/sp"
no "missing .scrub-patterns fails" "(cd $A && scripts/check.sh)"
mv "$TMP/sp" "$A/.scrub-patterns"

echo "threads and runs:"
printf '# Thread: homelab\nState: live. Updated: 2026-11-04.\n\n## Goal\nquiet\n' > "$A/memory/threads/homelab.md"
no "thread missing from the index fails" "(cd $A && scripts/check.sh)"
echo "| [homelab](threads/homelab.md) | live | quiet so far | 2026-11-04 |" >> "$A/memory/INDEX.md"
ok "indexed thread passes" "(cd $A && scripts/check.sh)"
printf '# Thread: x\n\n## Goal\n' > "$A/memory/threads/nostate.md"; echo "| [nostate](threads/nostate.md) | | | |" >> "$A/memory/INDEX.md"
no "thread without a State line fails" "(cd $A && scripts/check.sh)"
rm "$A/memory/threads/nostate.md"; sed -i.bak '/nostate/d' "$A/memory/INDEX.md"; rm -f "$A/memory/INDEX.md.bak"
printf '# Thread: old\nState: live. Updated: 2025-01-01.\n' > "$A/memory/threads/old.md"; echo "| [old](threads/old.md) | live | | 2025-01-01 |" >> "$A/memory/INDEX.md"
ok "stale live thread warns but passes" "(cd $A && scripts/check.sh | grep -q 'WARN.*old.md' && scripts/check.sh)"
rm "$A/memory/threads/old.md"; sed -i.bak '/threads\/old.md/d' "$A/memory/INDEX.md"; rm -f "$A/memory/INDEX.md.bak"
mkdir -p "$A/memory/log/2026-11-04-first-run"
no "log folder without run.md fails" "(cd $A && scripts/check.sh)"
printf 'Thread: homelab\n\nDid the thing.\n' > "$A/memory/log/2026-11-04-first-run/run.md"; echo "result" > "$A/memory/log/2026-11-04-first-run/report.txt"
ok "run folder with run.md and a deliverable passes" "(cd $A && scripts/check.sh)"
ok "hook: editing an uncommitted run.md allowed" "hook $A claude before-tool.sh '{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$A/memory/log/2026-11-04-first-run/run.md\",\"new_string\":\"x\"}}'"
(cd "$A" && git add -A && git commit -qm run)
no "hook: editing a committed run.md blocked" "hook $A claude before-tool.sh '{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$A/memory/log/2026-11-04-first-run/run.md\",\"new_string\":\"x\"}}'"
echo "edited" >> "$A/memory/log/2026-11-04-first-run/report.txt"
no "editing a committed deliverable fails the gate" "(cd $A && scripts/check.sh)"
git -C "$A" checkout -q memory/log/2026-11-04-first-run/report.txt
for i in $(seq 1 160); do echo "x" >> "$A/memory/threads/homelab.md"; done
no "thread over 150 lines fails" "(cd $A && scripts/check.sh)"
git -C "$A" checkout -q memory/threads/homelab.md

echo "agent hooks:"
ok "session start shows the next action" "hook $A claude session-start.sh '{}' | grep >/dev/null 'Next action'"
ok "session start shows the memory index" "hook $A claude session-start.sh '{}' | grep >/dev/null 'topics/people.md'"
ok "Antigravity session start is JSON" "hook $A agy session-start.sh '{}' | python3 -c 'import json,sys; json.load(sys.stdin)[\"injectSteps\"]'"
no "Claude: --no-verify blocked" "hook $A claude before-tool.sh '{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git commit --no-verify -m x\"}}'"
no "Codex: force-push blocked" "hook $A codex before-tool.sh '{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git push -f origin main\"}}'"
ok "force-with-lease allowed" "hook $A claude before-tool.sh '{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git push --force-with-lease\"}}'"
no "hard reset blocked" "hook $A claude before-tool.sh '{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git reset --hard HEAD~1\"}}'"
no "rm -rf outside the project blocked" "hook $A claude before-tool.sh '{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"rm -rf ~/Documents\"}}'"
ok "rm -rf inside the project allowed" "hook $A claude before-tool.sh '{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"rm -rf $A/build\"}}'"
no "editing an old log entry blocked" "hook $A claude before-tool.sh '{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$A/memory/log/2026-11-04-first.md\",\"new_string\":\"x\"}}'"
ok "a new log entry allowed" "hook $A claude before-tool.sh '{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$A/memory/log/2026-11-05-next.md\",\"content\":\"x\"}}'"
no "editing a template script blocked" "hook $A claude before-tool.sh '{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$A/scripts/check.sh\",\"new_string\":\"x\"}}'"
ok "editing scripts/local allowed" "hook $A claude before-tool.sh '{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$A/scripts/local/checks.sh\",\"new_string\":\"x\"}}'"
no "writing a private term blocked" "hook $A claude before-tool.sh '{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$A/notes.md\",\"content\":\"call bellwether\"}}'"
no "Codex apply_patch on an old log entry blocked" "hook $A codex before-tool.sh '{\"tool_name\":\"apply_patch\",\"tool_input\":{\"input\":\"*** Begin Patch\n*** Update File: memory/log/2026-11-04-first.md\n*** End Patch\"}}'"
ok "Antigravity block is a deny decision" "hook $A agy before-tool.sh '{\"toolCall\":{\"name\":\"run_command\",\"args\":{\"CommandLine\":\"git reset --hard\",\"Cwd\":\"$A\"}}}' | grep >/dev/null '\"decision\": \"deny\"'"
ok "Antigravity allows a safe command" "[[ -z \$(hook $A agy before-tool.sh '{\"toolCall\":{\"name\":\"run_command\",\"args\":{\"CommandLine\":\"ls\",\"Cwd\":\"$A\"}}}') ]]"
for i in $(seq 1 160); do echo "x" >> "$A/memory/topics/people.md"; done
no "after an edit: a too-long topic is reported" "hook $A claude after-edit.sh '{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$A/memory/topics/people.md\"}}'"
echo "# People" > "$A/memory/topics/people.md"
echo "change" > "$A/new-file.md"
no "before stop: asks for the gate after changes" "hook $A claude before-stop.sh '{}'"
ok "before stop: asks only once" "hook $A claude before-stop.sh '{}'"
(cd "$A" && scripts/check.sh >/dev/null)
echo "more" >> "$A/new-file.md"
ok "before stop: passing gate lets it stop" "(cd $A && scripts/check.sh) && hook $A claude before-stop.sh '{}'"

echo "versions and upgrades:"
ok "up to date" "$W status $P | grep >/dev/null 'up to date'"
echo 2.9.0 > "$P/scripts/TEMPLATE_VERSION"; echo "# old" >> "$P/scripts/check-lines.sh"
ok "older version: upgrade notice" "$W status $P --brief | grep >/dev/null 'upgrade available: 2.9.0'"
ok "older version: what changed, from the change log" "$W status $P | grep >/dev/null 'What to do'"
ok "older version: lists files to replace" "$W status $P | grep >/dev/null 'changed  scripts/check-lines.sh'"
ok "upgrade without --yes changes nothing" "$W upgrade $P >/dev/null && grep -q 2.9.0 $P/scripts/TEMPLATE_VERSION"
ok "upgrade --yes applies and keeps the edited copy" "$W upgrade $P --yes >/dev/null && grep -q \$($W version) $P/scripts/TEMPLATE_VERSION && [[ -f $P/scripts/check-lines.sh.before-\$($W version) ]]"
O="$TMP/old"; mkdir -p "$O/workspace" "$O/20_intent"; echo x > "$O/workspace/AGENTS.md"; git -C "$O" init -q
ok "old layout: told to move" "$W status $O --brief | grep >/dev/null 'old layout'"
no "old layout: init refuses" "$W init assistant $O"

echo "selftest: $pass passed, $fail failed"
(( fail == 0 ))
