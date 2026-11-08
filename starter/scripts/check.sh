#!/usr/bin/env bash
# Part of the Agent Workspace Template (version in scripts/TEMPLATE_VERSION). Upgrades replace it.
# check.sh: the one verification entry point.
#   scripts/check.sh           fast gate, run before every commit (seconds: format, ceilings)
#   scripts/check.sh full      everything, run before a push or a handover
#   scripts/check.sh receipt   what was last checked, and whether it still matches the tree
#   add --json to any of these   one JSON object on stdout instead of text, for harnesses and tools
#
# Stack blocks switch on by the files present (Cargo.toml, package.json, pyproject.toml, Makefile).
# This file belongs to the template; add this project's own checks to scripts/local/checks.sh.
# Every run writes a receipt (tree hash, mode, result, time) to the git dir, as text (last-check) and
# as JSON with each check's result (last-check.json), so a handover can prove which exact tree passed.
# Anyone can re-run `receipt` to see if the tree moved since.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1
MODE=fast JSON=""
for a in "$@"; do case "$a" in --json) JSON=1;; *) MODE="$a";; esac; done
RECEIPT="$(git rev-parse --git-dir)/last-check"; RECEIPT_JSON="$RECEIPT.json"

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
  now="$(tree_hash)" || now=""
  if [[ -n "$JSON" ]]; then  # the JSON receipt, plus whether the tree still matches it; exit 0 only when it does
    python3 -I - "$RECEIPT_JSON" "$now" <<'PY'
import json, sys
path, now = sys.argv[1], sys.argv[2]
try: d = json.load(open(path))
except (OSError, ValueError): d = {"result": "none"}
d["tree_now"] = now or None
d["tree_matches_now"] = bool(now) and d.get("tree") == now
print(json.dumps(d, indent=2))
sys.exit(0 if d["tree_matches_now"] else 1)
PY
    exit $?
  fi
  [[ -f "$RECEIPT" ]] || { echo "receipt: none (run scripts/check.sh)"; exit 1; }
  cat "$RECEIPT"
  [[ -n "$now" ]] || { echo "tree: cannot hash the working tree"; exit 1; }
  recorded="$(sed -n 's/^tree: //p' "$RECEIPT")"
  if [[ -n "$recorded" && "$recorded" == "$now" ]]; then echo "tree: unchanged since that run"; exit 0
  else echo "tree: CHANGED since that run; re-run the gate"; exit 1; fi
fi
[[ "$MODE" == fast || "$MODE" == full ]] || { echo "usage: check.sh [fast|full|receipt] [--json]"; exit 2; }

fail=0 CHECK_N=0
RESULTS="$(mktemp -d)"; trap 'rm -rf "$RESULTS"' EXIT
say() { [[ -n "$JSON" ]] || printf '%s\n' "$*"; }  # text output; silent with --json
record() {  # record <name> <ok|fail> <output>: one check's result, for the JSON receipt
  CHECK_N=$((CHECK_N + 1)); local d; d="$RESULTS/$(printf '%03d' "$CHECK_N")"; mkdir "$d"
  printf '%s' "$1" > "$d/name"; printf '%s' "$2" > "$d/status"; printf '%s\n' "$3" > "$d/out"
}
run() {  # run <name> <command...>: prints one line, the tail of the output on failure
  local name="$1" out; shift
  if out="$("$@" 2>&1)"; then record "$name" ok "$out"; say "  ok    $name"
    [[ -n "$JSON" ]] || { grep 'WARN' <<<"$out" | sed 's/^/        /' || true; }
  else record "$name" fail "$out"; fail=1; say "  FAIL  $name"
    [[ -n "$JSON" ]] || printf '%s\n' "$out" | tail -40 | sed 's/^/        /'; fi
}
have() { command -v "$1" >/dev/null 2>&1; }
full() { [[ "$MODE" == full ]]; }

say "check ($MODE):"
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

# entry files stay short; docs/ keeps its frontmatter and index; memory/ keeps its rules (private terms,
# append-only log, everything indexed)
run "line ceilings" scripts/check-lines.sh
[[ -d docs ]] && run "docs" scripts/check-docs.sh
[[ -d memory ]] && run "memory" scripts/check-memory.sh "$MODE"

# project: this project's own checks live in scripts/local/checks.sh (never edited by upgrades)
# (with --json, anything it prints goes to stderr so stdout stays one JSON object)
if [[ -f scripts/local/checks.sh ]]; then
  if [[ -n "$JSON" ]]; then . scripts/local/checks.sh >&2; else . scripts/local/checks.sh; fi
fi

# template: a newer Agent Workspace Template is only a note, never a failure
if full && [[ -x scripts/template-status.sh ]]; then
  note="$(scripts/template-status.sh --brief)"; printf '%s\n' "$note" > "$RESULTS/notes"
  [[ -z "$note" || -n "$JSON" ]] || sed 's/^/  note  /' <<<"$note"
fi

after="$(tree_hash)" || { echo "check: FAIL  cannot hash the working tree"; exit 1; }
if [[ "$after" != "$before" ]]; then
  record "tree unchanged while checking" fail "a formatter or generator wrote files; re-run"
  say "  FAIL  tree changed while the checks ran (a formatter or generator wrote files); re-run"; fail=1
fi
result=$([[ $fail == 0 ]] && echo PASS || echo FAIL)
head="$(git rev-parse --short HEAD 2>/dev/null || echo none)"; when="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
{ echo "tree: $after"; echo "head: $head"; echo "mode: $MODE"; echo "result: $result"; echo "when: $when"; } > "$RECEIPT"
python3 -I - "$RESULTS" "$RECEIPT_JSON" "$after" "$head" "$MODE" "$result" "$when" \
  "$(cat scripts/TEMPLATE_VERSION 2>/dev/null)" <<'PY'
import json, os, sys
res, out, tree, head, mode, result, when, ver = sys.argv[1:9]
checks = []
for n in sorted(x for x in os.listdir(res) if x.isdigit()):
    read = lambda f: open(os.path.join(res, n, f)).read()
    lines = read("out").rstrip("\n").splitlines()
    c = {"name": read("name"), "status": read("status")}
    warnings = [l.strip() for l in lines if "WARN" in l]
    if warnings: c["warnings"] = warnings
    if c["status"] == "fail": c["output_tail"] = lines[-40:]
    checks.append(c)
p = os.path.join(res, "notes")
notes = [l for l in open(p).read().splitlines() if l.strip()] if os.path.exists(p) else []
d = {"result": result, "mode": mode, "tree": tree, "head": head, "when": when,
     "template_version": ver.strip() or None, "checks": checks, "notes": notes}
with open(out, "w") as f: json.dump(d, f, indent=2); f.write("\n")
PY
if [[ -n "$JSON" ]]; then cat "$RECEIPT_JSON"; else echo "check: $result ($MODE) — receipt in $(basename "$RECEIPT")"; fi
exit $fail
