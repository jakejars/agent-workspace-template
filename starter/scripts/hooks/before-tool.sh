#!/usr/bin/env bash
# Part of the Agent Workspace Template (version in scripts/TEMPLATE_VERSION). Upgrades replace it.
# before-tool.sh: stops actions that break a workspace rule, before they run, and says why.
# Shell: skipping the git hooks, force-push, hard reset, recursive delete outside the project.
# Writes: editing a committed memory log entry (a run in progress may still edit its own uncommitted run.md), editing a template-owned file,
# changing an existing limits file (scripts/local/limits.env, scripts/ceilings.json: the owner's call), writing a private term.
# Private terms are checked in what gets written, not in shell commands, so an agent can still search for one.
. "$(dirname "$0")/lib.sh"
if [[ "$KIND" == shell ]]; then
  grep -qE -- '(^|[[:space:]])--no-verify([[:space:]]|$)|git( [^|;&]*)? commit( [^|;&]*)? -[a-zA-Z]*n[a-zA-Z]*( |$)' <<<"$CMD" &&
    block "Blocked: skipping the git hooks skips the gate. Fix what scripts/check.sh reports instead."
  grep -qE -- 'git( [^|;&]*)? push( [^|;&]*)? (--force([[:space:]]|$)|-[a-zA-Z]*f[a-zA-Z]*([[:space:]]|$)|\+[^[:space:]])' <<<"$CMD" &&
    block "Blocked: force-push rewrites shared history. Use --force-with-lease, and only with the owner's yes."
  grep -qE -- 'git( [^|;&]*)? reset( [^|;&]*)? --hard' <<<"$CMD" &&
    block "Blocked: git reset --hard throws away work. Use git stash, or ask the owner first."
  if grep -qE -- '(^|[;&|[:space:]])rm[[:space:]]+(-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)' <<<"$CMD"; then
    for p in $(grep -oE -- '(^|[[:space:]])(/|~|\.\.|\$HOME|\$\{HOME\})[^[:space:];&|]*' <<<"$CMD"); do
      p="${p/#\~/$HOME}"; p="${p/#\$\{HOME\}/$HOME}"; p="${p/#\$HOME/$HOME}"
      [[ -n "$(rel "$p")" ]] || block "Blocked: recursive delete outside this project ($p). Ask the owner first."
    done
  fi
elif [[ "$KIND" == write ]]; then
  while IFS= read -r f; do
    r="$(rel "$f")"; [[ -n "$r" ]] || continue
    [[ "$r" == memory/log/* ]] && git ls-files --error-unmatch -- "$r" >/dev/null 2>&1 &&
      block "Blocked: memory/log/ is append-only once committed. Add a new entry instead of changing $r."
    [[ "${TEMPLATE_DEV:-}" == 1 ]] || ! template_owned "$r" ||
      block "Blocked: $r belongs to the template and upgrades replace it. Put project checks in scripts/local/checks.sh."
    owner_limit "$r" && [[ -e "$r" ]] &&
      block "Blocked: $r sets the limits the gate enforces, so the owner changes it. Propose the change and the reason in your reply."
  done <<<"$FILES"
fi
if [[ "$KIND" == write ]]; then
  hits="$(private_terms "$TEXTS")"
  [[ -z "$hits" ]] || block "Blocked: this contains a private term (.scrub-patterns line $(echo $hits)). Leave it out."
fi
exit 0
