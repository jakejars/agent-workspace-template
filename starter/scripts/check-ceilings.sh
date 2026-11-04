#!/usr/bin/env bash
# check-ceilings.sh: counts that may not rise. Floors (counts that may not fall) are not here on
# purpose: a test-count floor invites padding. Patterns live in scripts/ceilings.json:
#   { "name": { "pattern": "<git grep -E pattern>", "paths": ["pathspec", ...], "max": N }, ... }
# `--seed` rewrites every max from the current counts (after a reviewer agreed a rise was right).
# Lowering a max is always allowed; raising one by hand belongs in the same commit as the reason.
set -euo pipefail
set -f  # pathspecs such as *.rs are for git, never for the shell
cd "$(git rev-parse --show-toplevel)"
FILE="scripts/ceilings.json"
[[ -f "$FILE" ]] || { echo "ceilings: $FILE missing"; exit 1; }

# One line per ceiling: name, pattern, max, then the pathspecs, all tab-separated. Parsed up front
# so a malformed file fails the gate instead of producing an empty, passing loop.
TABLE="$(python3 -I -c '
import json, sys
d = json.load(open(sys.argv[1]))
for k, v in d.items():
    row = [k, v["pattern"], str(int(v["max"]))] + list(v.get("paths", ["."]))
    assert not any("\t" in c or "\n" in c for c in row), "tabs and newlines are not allowed in " + k
    print("\t".join(row))' "$FILE")" || { echo "ceilings: FAIL  cannot parse $FILE"; exit 1; }
[[ -n "$TABLE" ]] || { echo "ceilings: FAIL  $FILE has no ceilings"; exit 1; }

count() {  # count <pattern> <pathspec...>: matching lines, in tracked and untracked files
  local pattern="$1" out rc; shift
  out="$(git grep --untracked -c -E -- "$pattern" "$@" 2>&1)" && rc=0 || rc=$?
  case $rc in
    0|1) printf '%s\n' "$out" | awk -F: '{s+=$NF} END{print s+0}' ;;  # 1 = no matches
    *) echo "ceilings: FAIL  git grep error for pattern '$pattern': $out" >&2; return 1 ;;
  esac
}

fail=0; seeded=""
while IFS=$'\t' read -r -a row; do
  name="${row[0]}" pattern="${row[1]}" max="${row[2]}"; paths=("${row[@]:3}")
  n="$(count "$pattern" "${paths[@]}")" || { fail=1; continue; }
  if [[ "${1:-}" == --seed ]]; then seeded+="$name"$'\t'"$n"$'\n'
  elif (( n > max )); then echo "ceilings: FAIL  $name rose to $n (max $max)"; fail=1
  else echo "ceilings: ok    $name $n (max $max)"; fi
done <<< "$TABLE"

if [[ "${1:-}" == --seed ]]; then
  (( fail == 0 )) || exit 1
  python3 -I -c '
import json, sys
d = json.load(open(sys.argv[1]))
for line in sys.stdin.read().splitlines():
    if not line.strip(): continue
    k, n = line.split("\t"); d[k]["max"] = int(n)
with open(sys.argv[1], "w") as f:
    json.dump(d, f, indent=2); f.write("\n")' "$FILE" <<< "$seeded"
  echo "ceilings: seeded $FILE"; exit 0
fi
(( fail == 0 )) || { echo "ceilings: a count rose. Fix the code, or raise the max in $FILE in the same commit with the reason."; exit 1; }
