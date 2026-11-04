#!/usr/bin/env bash
# Part of the Agent Workspace Template (version in scripts/TEMPLATE_VERSION). Upgrades replace it.
# check-memory.sh [fast|full]: the rules that keep memory/ trustworthy. Runs only when memory/ exists.
#   1. private terms: no line of .scrub-patterns (gitignored, one term per line) appears in any
#      tracked or untracked file. A missing .scrub-patterns fails: it must exist, even if empty.
#   2. append-only log: files in memory/log/ are added, never edited or deleted. `full` also
#      checks the commits not yet pushed.
#   3. one hop to everything: every memory/topics/*.md is linked from memory/INDEX.md, and every
#      topic the index links to exists.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1
[[ -d memory ]] || exit 0
MODE="${1:-fast}"
fail=0
bad() { echo "memory: FAIL  $*"; fail=1; }

# 1. private terms
if [[ ! -f .scrub-patterns ]]; then
  bad ".scrub-patterns is missing. Create it (one private term per line, # for comments) and gitignore it."
elif ! git check-ignore -q .scrub-patterns; then
  bad ".scrub-patterns must be gitignored, or the private terms get committed."
else
  pats="$(mktemp)"; grep -v -e '^[[:space:]]*#' -e '^[[:space:]]*$' .scrub-patterns > "$pats" || true
  if [[ -s "$pats" ]]; then
    hits="$(git grep --untracked -I -l -i -F -f "$pats" -- . 2>&1)"; rc=$?
    case $rc in
      0) bad "private terms found in:"; printf '%s\n' "$hits" | sed 's/^/        /' ;;
      1) ;;
      *) bad "cannot search for private terms: $hits" ;;
    esac
  fi
  rm -f "$pats"
fi

# 2. append-only log
edited() {  # edited <git diff args...>: log files that were modified, deleted or renamed
  git diff --name-status --no-renames "$@" -- memory/log | awk '$1 != "A" {print $2}'
}
if git rev-parse -q --verify HEAD >/dev/null; then
  e="$(edited HEAD)"
  [[ -z "$e" ]] || bad "memory/log/ is append-only; these were edited or deleted (restore them, add a new entry instead): $(echo $e)"
  if [[ "$MODE" == full ]] && up="$(git rev-parse -q --verify '@{u}' 2>/dev/null)"; then
    e="$(edited "$up" HEAD)"
    [[ -z "$e" ]] || bad "commits not yet pushed edit or delete log entries: $(echo $e)"
  fi
fi

# 3. everything one hop from the index
if [[ ! -f memory/INDEX.md ]]; then
  bad "memory/INDEX.md is missing."
else
  shopt -s nullglob
  for f in memory/topics/*.md; do
    grep -qF "topics/${f##*/}" memory/INDEX.md || bad "$f is not linked from memory/INDEX.md"
  done
  while read -r link; do
    [[ -f "memory/$link" ]] || bad "memory/INDEX.md links to $link, which does not exist"
  done < <(grep -oE 'topics/[A-Za-z0-9._-]+\.md' memory/INDEX.md | sort -u)
fi

exit "$fail"
