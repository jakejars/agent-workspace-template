#!/usr/bin/env python3
"""Fill, resume and finalize a workspace without inventing user answers.

Usage:
  python3 tools/instantiate.py              fill this workspace from values.json
  python3 tools/instantiate.py --check      audit an instance; change nothing
  python3 tools/instantiate.py --finalize --hooks portable  validate readiness
  python3 tools/instantiate.py --date D     stamp D (YYYY-MM-DD) instead of today
  python3 tools/instantiate.py --help       this text

`00_meta/ONBOARDING.md` owns the walk. The interview, the first intent, the
consumer answer and hook disposition stay there; this tool substitutes answers,
closes unused seams, writes the birth journal, and records a resumable fill.
Finalization validates the first intent and integrity gates before removing
setup markers. It records the hook choice without claiming runtime installation.

Splitting it this way is the point. Hand-substitution is where instances break
— a family-wide grep also rewrites the `tools/` fixtures that the negative
tests plant, and the suite then passes while testing nothing.

Exit: 0 done or clean, 1 refused or incomplete, 2 usage.
"""

import argparse
import datetime
import subprocess
from pathlib import Path
import json
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_catalog import (ROOT, LAYOUT, PLACEHOLDERS,  # noqa: E402
                           content_files, parse_frontmatter, read_text,
                           token_registry)
from workspace_layout import refuse_unknown  # noqa: E402

# Policy per placeholders.md. Asserted against the registry below, so a token
# added there without a decision here is an error rather than a silent skip.
REQUIRED = ("PRINCIPAL_NAME", "WORKSPACE_ID")
OPTIONAL = ("PRINCIPAL_EMAIL", "ORG_NAME", "MACHINE_FILE", "WORKSPACE_PATH")
CLOSES_A_SEAM = {
    "SHARED_CONTEXT_PATH": "workspace/70_seams/shared-context.md",
    "REGISTRY_PATH": "workspace/70_seams/registry.md",
    "LIBRARY_PATH": "workspace/70_seams/library.md",
}
DEFAULTS = {"OBJECTION_WINDOW_HOURS": "48", **{name: "" for name in OPTIONAL}}
# Never in values.json: never-share answers live only in the ignored store.
PRIVATE_ONLY = ("PRINCIPAL_LEGAL_NAME", "CLIENT_CODENAME")

VALUES = "workspace/00_meta/values.json"
SENTINEL = "workspace/00_meta/.uninitialised"
INITIALIZING = "workspace/00_meta/.initializing"
READY = "workspace/00_meta/ready.json"
JOURNAL = "workspace/30_memory/journal"
ROSTER = "shared-context/roster.md"
CHANGES = "shared-context/CHANGES.md"

TOKEN_RE = re.compile(r"<<([A-Z][A-Z_]*)>>")
FLAG_RE = re.compile(r"^tokens: true\s*$", re.M)


def path_of(rel):
    """Absolute path for a canonical member-prefixed path in this root."""
    return os.path.join(ROOT, LAYOUT.physical_rel(rel))


def consumers():
    """Every file that declares `tokens: true`, minus the registry itself.

    The registry carries the flag because it displays every token; filling it
    would delete the table it is (placeholders.md, fill mechanism).
    """
    registry = LAYOUT.physical_rel(PLACEHOLDERS)
    found = []
    for rel in content_files():
        if rel == registry:
            continue
        text = read_text(os.path.join(ROOT, rel), [], rel)
        if text and FLAG_RE.search(text.split("---", 2)[1] if
                                   text.startswith("---") else ""):
            found.append(rel)
    return found


def load_values(problems):
    """values.json, checked against the registry and this tool's policy."""
    raw = read_text(path_of(VALUES), [], VALUES)
    if raw is None:
        problems.append(f"{VALUES} is missing — run the interview first "
                        "(00_meta/ONBOARDING.md step 1)")
        return {}
    try:
        values = json.loads(raw)
    except json.JSONDecodeError as exc:
        problems.append(f"{VALUES}: not valid JSON ({exc})")
        return {}
    if not isinstance(values, dict):
        problems.append(f"{VALUES}: expected an object of TOKEN to value")
        return {}

    registered, label = token_registry([])
    known = set(REQUIRED) | set(CLOSES_A_SEAM) | set(DEFAULTS) | set(PRIVATE_ONLY)
    for name in sorted(registered - known):
        problems.append(f"{name} has a row in {label} but no rule in "
                        "tools/instantiate.py — decide whether it is required, "
                        "closes a seam, or has a default")
    for name in sorted(known - registered - set(PRIVATE_ONLY)):
        problems.append(f"{name} has a rule in tools/instantiate.py but no row "
                        f"in {label}")

    for name in sorted(set(values) - registered):
        problems.append(f"{VALUES}: {name} is not a registered token")
    for name in PRIVATE_ONLY:
        if name in values:
            problems.append(f"{VALUES}: {name} is a never-share answer and "
                            "belongs only in the ignored private store")
    for name in REQUIRED:
        if not str(values.get(name, "")).strip():
            problems.append(f"{VALUES}: {name} is required and unanswered")
    for name, fallback in DEFAULTS.items():
        values.setdefault(name, fallback)
    for name in CLOSES_A_SEAM:
        values.setdefault(name, "")

    machine = str(values.get("MACHINE_FILE", "")).strip()
    if machine:
        if not os.path.isabs(os.path.expanduser(machine)) or not os.path.isfile(os.path.expanduser(machine)):
            problems.append("MACHINE_FILE must be an existing absolute file path")
        resolved = os.path.realpath(os.path.expanduser(machine))
        if resolved.startswith(os.path.realpath(ROOT) + os.sep):
            problems.append("MACHINE_FILE must resolve outside the workspace root; "
                            "machine truth is referenced, never copied")
    for name in ("WORKSPACE_PATH",) + tuple(CLOSES_A_SEAM):
        supplied = str(values.get(name, "")).strip()
        if supplied and not os.path.exists(os.path.expanduser(supplied)):
            problems.append(f"{name} does not exist: {supplied}")
    return values


def substitute(values, changed):
    """Fill every consumer, one exact token at a time."""
    for rel in consumers():
        target = os.path.join(ROOT, rel)
        with open(target, encoding="utf-8") as handle:
            before = handle.read()
        after = before
        for name, value in values.items():
            after = after.replace(f"<<{name}>>", str(value))
        if after != before:
            with open(target, "w", encoding="utf-8") as handle:
                handle.write(after)
            changed.append(rel)


def close_seam(rel, token, today, changed):
    """Demote an unlinked seam to `stub` (doctrine/seams.md, on closure)."""
    target = path_of(rel)
    if not os.path.isfile(target):
        return
    with open(target, encoding="utf-8") as handle:
        text = handle.read()
    head, body = text.split("---", 2)[1], text.split("---", 2)[2]
    title = re.search(r"^# .*$", body, re.M)
    head = head.replace("status: draft", "status: stub")
    # The flag goes with the token: a closed seam names no path, and a file
    # holding a registered token without the flag is a validator error.
    head = re.sub(r"\ntokens: true(?=\n)", "", head)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(
            f"---{head}---\n\n{title.group(0) if title else '# Seam'}\n\n"
            "This seam is not open. Nothing crosses it. To open it, answer\n"
            "the five questions in doctrine/seams.md from evidence.\n\n"
            f"Closed at instantiation on {today}: no `{token}` was supplied.\n"
            "The answers this template shipped with are in Git history;\n"
            "re-answer them from evidence rather than restoring them.\n")
    changed.append(LAYOUT.physical_rel(rel))


def fill_commons(values, today, changed):
    """The roster row and the changelog trailer (ONBOARDING step 3)."""
    roster = path_of(ROSTER)
    if os.path.isfile(roster):
        with open(roster, encoding="utf-8") as handle:
            text = handle.read()
        filled = text.replace("| YYYY-MM-DD | YYYY-MM-DD |",
                              f"| {today} | {today} |")
        if filled != text:
            with open(roster, "w", encoding="utf-8") as handle:
                handle.write(filled)
            changed.append(LAYOUT.physical_rel(ROSTER))

    changes = path_of(CHANGES)
    if os.path.isfile(changes):
        with open(changes, encoding="utf-8") as handle:
            text = handle.read()
        window = int(str(values.get("OBJECTION_WINDOW_HOURS", "48")) or 48)
        opened = f"{today}T12:00Z"
        binds = (datetime.datetime.strptime(opened, "%Y-%m-%dT%H:%MZ")
                 + datetime.timedelta(hours=window)).strftime("%Y-%m-%dT%H:%MZ")
        trailer = (f"`{opened} | {values['WORKSPACE_ID']} | shared-context/* | "
                   f"instantiation fill | state: bound | binds: {binds}`")
        filled = re.sub(r"`[^`\n]*example trailer[^`\n]*`", trailer, text, count=1)
        if filled != text:
            with open(changes, "w", encoding="utf-8") as handle:
                handle.write(filled)
            changed.append(LAYOUT.physical_rel(CHANGES))


def birth_journal(values, today, changed):
    """One entry naming the instance and its links (ONBOARDING step 7)."""
    journal = path_of(JOURNAL)
    os.makedirs(journal, exist_ok=True)
    minute = datetime.datetime.now().strftime("%H%M")
    name = f"{today}-{minute}-instantiated.md"
    target = os.path.join(journal, name)
    if any(n.endswith("-instantiated.md") for n in os.listdir(journal)):
        return
    linked = [member for token, member in
              (("SHARED_CONTEXT_PATH", "commons"), ("REGISTRY_PATH", "registry"),
               ("LIBRARY_PATH", "library"))
              if str(values.get(token, "")).strip()]
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(
            f"---\ndate: {today}T{minute[:2]}:{minute[2:]}\nkind: event\n"
            "refs: [00_meta/values.json]\n---\n\n"
            f"Workspace instantiated as `{values['WORKSPACE_ID']}` from the answers "
            f"in `00_meta/values.json`. Linked: "
            f"{', '.join(linked) if linked else 'no optional members'}. "
            "The first intent and the runtime hook are the walk's remaining "
            "steps.\n")
    changed.append(f"{LAYOUT.physical_rel(JOURNAL)}/{name}")


def survivors():
    """Registered tokens still unfilled in a consumer."""
    registered, _ = token_registry([])
    left = []
    for rel in consumers():
        text = read_text(os.path.join(ROOT, rel), [], rel) or ""
        for name in sorted(set(TOKEN_RE.findall(text)) & registered):
            left.append(f"{rel}: <<{name}>> survived the fill")
    return left


def audit(values, problems, require_finalized=True):
    """What `--check` proves about a workspace that claims to be instantiated."""
    if require_finalized and os.path.isfile(path_of(SENTINEL)):
        problems.append(f"{LAYOUT.physical_rel(SENTINEL)} is still present — run --finalize after the first intent and hook choice")
    if require_finalized and os.path.isfile(path_of(INITIALIZING)):
        problems.append("Setup checkpoint remains — resume --finalize to finish readiness.")
    problems.extend(survivors())
    journal = path_of(JOURNAL)
    entries = [n for n in sorted(os.listdir(journal))
               if n.endswith(".md") and n not in ("INDEX.md", "README.md")
               ] if os.path.isdir(journal) else []
    if not entries:
        problems.append(f"{JOURNAL}/ holds no entry — instantiation is a "
                        "durable event and is journalled")
    for token, seam in CLOSES_A_SEAM.items():
        linked = bool(str(values.get(token, "")).strip())
        text = read_text(path_of(seam), [], seam) or ""
        head = text.split("---", 2)[1] if text.startswith("---") else ""
        stubbed = "status: stub" in head
        if linked and stubbed:
            problems.append(f"{seam}: closed, but {token} names a path")
        if not linked and not stubbed:
            problems.append(f"{seam}: open, but {token} is empty — an unlinked "
                            "seam is a stub")


def write_state(rel, value):
    from context import atomic_write
    atomic_write(path_of(rel), json.dumps(value, indent=2)+"\n")


def finalize(values, hooks, today):
    problems = []
    audit(values, problems, require_finalized=False)
    if not hooks:
        problems.append("Finalization needs explicit --hooks portable or --hooks runtime; neither is assumed.")
    active = Path(path_of("workspace/20_intent/active"))
    intents = []
    for p in active.glob("*.md"):
        fm = parse_frontmatter(p.read_text()) or {}
        if fm.get("type") == "intent" and fm.get("status") in {"draft", "mature"} and fm.get("lifecycle") not in {"satisfied", "abandoned", "superseded"}:
            intents.append(p)
    if not intents:
        problems.append("Create the first active intent before finalization.")
    if not os.path.isfile(path_of(INITIALIZING)):
        problems.append("No fill checkpoint exists; complete the mechanical fill first.")
    if problems:
        for problem in problems: print("ERROR "+problem)
        return 1
    # --check normally sees template mode while sentinel remains. Read the
    # instance privacy configuration explicitly before allowing that transition.
    from scrub_check import load_terms
    _, error = load_terms(Path(ROOT), False)
    if error:
        print("ERROR finalization gate: "+error)
        return 1
    for tool, args in (("build_catalog.py", ["--check"]), ("check_loop.py", []),
                       ("pipeline.py", ["check"]),
                       ("scrub_check.py", []), ("agnostic_check.py", [])):
        result = subprocess.run([sys.executable, str(Path(ROOT)/"tools"/tool), *args],
                                cwd=ROOT, text=True, capture_output=True)
        if result.returncode:
            print("ERROR finalization gate: "+tool+"\n"+result.stdout+result.stderr)
            return 1
    # Readiness is written only after validation. If interrupted after this
    # point, --finalize can safely finish removing the remaining markers.
    write_state(READY, {"version": 1, "workspace_id": values["WORKSPACE_ID"],
                        "finalized_on": today, "hooks": hooks})
    Path(path_of(SENTINEL)).unlink(missing_ok=True)
    os.remove(path_of(INITIALIZING))
    print("Ready: first intent, hook disposition and integrity gates verified. "
          "Runtime hooks are not claimed installed by this receipt.")
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    refused = refuse_unknown(LAYOUT, "instantiate")
    if refused:
        sys.stderr.write(refused + "\n")
        return 2
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--finalize", action="store_true")
    parser.add_argument("--minimal", action="store_true",
                        help="minimal answers, not minimal effects; only name "
                             "and workspace id are asked, optional member "
                             "paths stay empty and close their seams")
    parser.add_argument("--hooks", choices=["portable", "runtime"])
    parser.add_argument("--date", default=str(datetime.date.today()))
    args = parser.parse_args(argv[1:])
    try: datetime.date.fromisoformat(args.date)
    except ValueError:
        parser.error("--date takes a real YYYY-MM-DD date")
    problems = []
    values = load_values(problems)
    if args.check:
        if values: audit(values, problems)
        try:
            with open(path_of(READY), encoding="utf-8") as handle:
                receipt = json.load(handle)
            valid = (receipt.get("version") == 1
                     and receipt.get("workspace_id") == values.get("WORKSPACE_ID")
                     and receipt.get("hooks") in {"portable", "runtime"})
            datetime.date.fromisoformat(receipt.get("finalized_on", ""))
            if not valid: raise ValueError("invalid receipt")
        except (OSError, ValueError, AttributeError, TypeError):
            problems.append("Missing or invalid readiness receipt; complete --finalize.")
        for problem in problems: print("ERROR "+problem)
        if problems: return 1
        print("OK: instantiated and finalized as "+values["WORKSPACE_ID"])
        return 0
    if problems:
        for problem in problems: print("ERROR "+problem)
        print("Nothing was changed.")
        return 1
    if args.finalize and os.path.isfile(path_of(INITIALIZING)):
        return finalize(values, args.hooks, args.date)
    if not os.path.isfile(path_of(SENTINEL)):
        print("Already instantiated; use --check to audit it.")
        return 1
    if args.finalize:
        return finalize(values, args.hooks, args.date)
    if os.path.isfile(path_of(INITIALIZING)):
        try:
            with open(path_of(INITIALIZING), encoding="utf-8") as handle:
                prior = json.load(handle)
            if prior.get("state") == "filled":
                print("Fill checkpoint exists; resume setup and run --finalize. Nothing re-filled.")
                return 0
        except (OSError, ValueError, AttributeError):
            print("ERROR invalid fill checkpoint; inspect setup state before retrying.")
            return 1
    write_state(VALUES, values)
    marker = {"version": 1, "state": "filling", "workspace_id": values["WORKSPACE_ID"], "started_on": args.date}
    write_state(INITIALIZING, marker)
    changed = []
    substitute(values, changed)
    for token, seam in CLOSES_A_SEAM.items():
        if not str(values.get(token, "")).strip(): close_seam(seam, token, args.date, changed)
    fill_commons(values, args.date, changed)
    birth_journal(values, args.date, changed)
    left = survivors()
    if left:
        for problem in left: print("ERROR "+problem)
        return 1
    marker["state"] = "filled"
    write_state(INITIALIZING, marker)
    print(f"Filled {values['WORKSPACE_ID']}: {len(changed)} files. Setup remains open; "
          "create the first intent, choose hook disposition, then run --finalize.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
