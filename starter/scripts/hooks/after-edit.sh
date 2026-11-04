#!/usr/bin/env bash
# Part of the Agent Workspace Template (version in scripts/TEMPLATE_VERSION). Upgrades replace it.
# after-edit.sh: checks each file just written, so a problem shows now rather than at commit time:
# line ceilings on entry files and memory topics, an index row for each topic, private terms.
. "$(dirname "$0")/lib.sh"
[[ "$KIND" == write ]] || exit 0
problems=""
while IFS= read -r f; do
  r="$(rel "$f")"; [[ -n "$r" && -f "$r" ]] || continue
  case "$r" in
    AGENTS.md|build-notes/project.md|build-notes/task.md|memory/INDEX.md|memory/topics/*.md)
      out="$(scripts/check-lines.sh 2>&1)" || problems+="$(grep -F "$r " <<<"$out")"$'\n' ;;
  esac
  [[ "$r" == memory/topics/*.md ]] && ! grep -qF "topics/${r##*/}" memory/INDEX.md 2>/dev/null &&
    problems+="memory: add a row for topics/${r##*/} to memory/INDEX.md."$'\n'
  hits="$(private_terms "$r")"
  [[ -z "$hits" ]] || problems+="$r contains a private term (.scrub-patterns line $(echo $hits)); remove it."$'\n'
done <<<"$FILES"
[[ -z "${problems//[[:space:]]/}" ]] || block "${problems%$'\n'}"
exit 0
