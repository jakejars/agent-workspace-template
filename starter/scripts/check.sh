#!/usr/bin/env bash
# Part of the Agent Workspace Template (version in scripts/TEMPLATE_VERSION). Upgrades replace it.
# check.sh: the one verification entry point.
#   scripts/check.sh           fast gate, run before every commit (seconds: format, ceilings)
#   scripts/check.sh full      everything, run before a push or a handover
#   scripts/check.sh receipt   what was last checked, and whether it still matches the tree
#
# Stack blocks switch on by the files present (Cargo.toml, package.json, pyproject.toml, Makefile).
# This file belongs to the template; add this project's own checks to scripts/local/checks.sh.
# Every run writes a receipt (tree hash, mode, result, time) to the git dir, so a handover can
# prove which exact tree passed. Anyone can re-run `receipt` to see if the tree moved since.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1
MODE="${1:-fast}"
RECEIPT="$(git rev-parse --git-dir)/last-check"

tree_hash() {  # hash of the working tree: tracked and untracked (not ignored) files, minus build-notes/
  # Starts from an empty index so assume-unchanged and skip-worktree flags cannot hide a file;
  # tracked files are then re-added by name so a tracked-but-ignored file still counts.
  # build-notes/ is left out so writing the notes after a passing gate does not void its receipt.
  # Submodule commits and any uncommitted change inside a submodule are folded into the hash.
  local idx tree subs; idx="$(mktemp -u)"
  { GIT_INDEX_FILE="$idx" git add -A -- . ':!build-notes' 2>/dev/null &&  # stderr is only the embedded-repo warning for submodules; failure still returns 1
    git ls-files -z -- . ':!build-notes' | GIT_INDEX_FILE="$idx" git update-index --add --remove -z --stdin &&
    tree="$(GIT_INDEX_FILE="$idx" git write-tree)"; } || { rm -f "$idx"; return 1; }
  rm -f "$idx"
  subs="$( git submodule status --recursive &&
           git submodule foreach --quiet --recursive 'git status --porcelain=v1 --untracked-files=all; git diff HEAD;
             git ls-files --others --exclude-standard | git hash-object --stdin-paths' )" || return 1
  [[ -z "$subs" ]] && { echo "$tree"; return; }
  printf '%s\n%s\n' "$tree" "$subs" | git hash-object --stdin
}

if [[ "$MODE" == receipt ]]; then
  [[ -f "$RECEIPT" ]] || { echo "receipt: none (run scripts/check.sh)"; exit 1; }
  cat "$RECEIPT"
  recorded="$(sed -n 's/^tree: //p' "$RECEIPT")"; now="$(tree_hash)" || { echo "tree: cannot hash the working tree"; exit 1; }
  if [[ -n "$recorded" && "$recorded" == "$now" ]]; then echo "tree: unchanged since that run"; exit 0
  else echo "tree: CHANGED since that run; re-run the gate"; exit 1; fi
fi
[[ "$MODE" == fast || "$MODE" == full ]] || { echo "usage: check.sh [fast|full|receipt]"; exit 2; }

fail=0
run() {  # run <name> <command...>: prints one line, the tail of the output on failure
  local name="$1" out; shift
  if out="$("$@" 2>&1)"; then echo "  ok    $name"
  else echo "  FAIL  $name"; printf '%s\n' "$out" | tail -40 | sed 's/^/        /'; fail=1; fi
}
have() { command -v "$1" >/dev/null 2>&1; }
full() { [[ "$MODE" == full ]]; }

echo "check ($MODE):"
before="$(tree_hash)" || { echo "check: FAIL  cannot hash the working tree"; exit 1; }

# rust
if [[ -f Cargo.toml ]]; then
  run "cargo fmt" cargo fmt --all -- --check
  if full; then
    run "cargo clippy" cargo clippy --workspace --all-targets -- -D warnings
    if have cargo-nextest; then run "cargo nextest" cargo nextest run --workspace
    else run "cargo test" cargo test --workspace; fi
    have cargo-machete && run "cargo machete" cargo machete
    [[ -f deny.toml ]] && have cargo-deny && run "cargo deny" cargo deny check
  fi
fi

# node, svelte, typescript: the project defines "check" (types, lint) and "test" in package.json
if [[ -f package.json ]]; then
  grep -q '"check"' package.json && run "npm run check" npm run --silent check
  full && grep -q '"test"' package.json && run "npm test" npm test --silent
fi

# python
if [[ -f pyproject.toml ]] || ls ./*.py >/dev/null 2>&1; then
  have ruff && run "ruff" ruff check .
  full && have ruff && run "ruff format" ruff format --check .
  full && run "pytest" python3 -I -m pytest -q
fi

# c
if [[ -f Makefile ]] && full; then
  run "make check" make -s check
fi

# ceilings: counts that may not rise (allow, ignore, todo, undocumented unsafe...)
[[ -f scripts/ceilings.json ]] && run "ceilings" scripts/check-ceilings.sh

# entry files stay short; memory/ keeps its rules (private terms, append-only log, everything indexed)
run "line ceilings" scripts/check-lines.sh
[[ -d memory ]] && run "memory" scripts/check-memory.sh "$MODE"

# project: this project's own checks live in scripts/local/checks.sh (never edited by upgrades)
[[ -f scripts/local/checks.sh ]] && . scripts/local/checks.sh

# template: a newer Agent Workspace Template is only a note, never a failure
full && [[ -x scripts/template-status.sh ]] && scripts/template-status.sh --brief | sed 's/^/  note  /'

after="$(tree_hash)" || { echo "check: FAIL  cannot hash the working tree"; exit 1; }
if [[ "$after" != "$before" ]]; then echo "  FAIL  tree changed while the checks ran (a formatter or generator wrote files); re-run"; fail=1; fi
result=$([[ $fail == 0 ]] && echo PASS || echo FAIL)
{ echo "tree: $after"; echo "head: $(git rev-parse --short HEAD 2>/dev/null || echo none)"
  echo "mode: $MODE"; echo "result: $result"; echo "when: $(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$RECEIPT"
echo "check: $result ($MODE) — receipt in $(basename "$RECEIPT")"
exit $fail
