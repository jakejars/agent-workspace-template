#!/usr/bin/env python3
"""Read-only Sett health check, in plain language.

usage: python3 tools/doctor.py [--verbose]
Exit: 0 healthy, 1 valid Sett with actionable problems, 2 not a Sett root.

Doctor reuses the real validators and never changes anything. `--verbose`
shows the underlying tool output for any failing check.
"""

import argparse
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sett_layout import SettLayout, refuse_unknown  # noqa: E402
import scrub_check  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYOUT = SettLayout(ROOT)

REQUIRED_VALUES = ("PRINCIPAL_NAME", "WORKSPACE_ID")


def run_tool(tool, *args):
    """Run a shipped validator; return (returncode, combined output)."""
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", tool), *args],
        cwd=ROOT, text=True, capture_output=True)
    return proc.returncode, proc.stdout + proc.stderr


def first_lines(output, count=3):
    """The most useful leading diagnostics, for the non-verbose summary."""
    lines = [ln for ln in output.splitlines() if ln.strip()]
    return lines[:count]


def check(values_rel, active_rel):
    checks = []
    context = None

    def add(name, ok, hint, raw=""):
        checks.append({"name": name, "ok": ok, "hint": hint, "raw": raw})

    add("workspace layout", True, "")   # reaching here means a recognized root

    template_mode = (LAYOUT.kind == "family"
                     and os.path.isfile(os.path.join(
                         ROOT, LAYOUT.physical_rel("workspace/00_meta/.uninitialised"))))
    if template_mode:
        context = "source checkout — a template, not a workspace"
    sentinel = os.path.join(ROOT, LAYOUT.physical_rel("workspace/00_meta/.uninitialised"))
    receipt = os.path.join(ROOT, LAYOUT.physical_rel("workspace/00_meta/ready.json"))

    # Setup state ----------------------------------------------------------
    if template_mode:
        add("setup complete", True,
            "this is the Sett source checkout; it is a template, not a "
            "workspace, so setup checks do not apply here. Run "
            "`python3 tools/new.py <destination>` to create a workspace.")
    else:
        code, out = run_tool("instantiate.py", "--check")
        add("setup complete", code == 0,
            "setup is incomplete or invalid; run "
            "`python3 tools/instantiate.py --check` for the exact findings.",
            out)

    # Identity -------------------------------------------------------------
    raw_values = None
    try:
        with open(os.path.join(ROOT, values_rel), encoding="utf-8") as handle:
            raw_values = json.load(handle)
    except (OSError, ValueError):
        raw_values = None
    if template_mode:
        add("identity configuration", True, "(template checkout)")
    elif not isinstance(raw_values, dict):
        add("identity configuration", False,
            "values.json is missing or unreadable; setup writes it during "
            "the fill.")
    else:
        missing = [n for n in REQUIRED_VALUES
                   if not str(raw_values.get(n, "")).strip()]
        add("identity configuration", not missing,
            "values.json is missing " + ", ".join(missing) + "."
            if missing else "")

    # Privacy --------------------------------------------------------------
    _, privacy_error = scrub_check.load_terms(
        __import__("pathlib").Path(ROOT), template_mode)
    add("privacy configuration", privacy_error is None,
        "No explicit private-term choice is recorded. Configure private "
        "terms in the ignored .sett-private/never-share.txt, or explicitly "
        "confirm there are none.",
        privacy_error or "")

    # Active task ----------------------------------------------------------
    if template_mode:
        add("active task", True, "(template checkout)")
    else:
        active_dir = os.path.join(ROOT, active_rel)
        found = False
        if os.path.isdir(active_dir):
            for name in sorted(os.listdir(active_dir)):
                if not name.endswith(".md"):
                    continue
                path = os.path.join(active_dir, name)
                try:
                    with open(path, encoding="utf-8") as handle:
                        text = handle.read()
                except OSError:
                    continue
                head = text.split("---", 2)[1] if text.startswith("---") else ""
                fm = {}
                for line in head.splitlines():
                    m = re.match(r"^([a-z_]+):\s*(.*)$", line)
                    if m:
                        fm[m.group(1)] = m.group(2).strip()
                if (fm.get("type") == "intent"
                        and fm.get("status") in {"draft", "mature"}
                        and fm.get("lifecycle")
                        not in {"satisfied", "abandoned", "superseded"}):
                    found = True
                    break
        add("active task", found,
            "no active intent was found in 20_intent/active/ — capture what "
            "this workspace is for.")

    # Automatic Git checks -------------------------------------------------
    if template_mode:
        add("automatic Git checks", True, "(template checkout)")
    elif not os.path.isdir(os.path.join(ROOT, ".git")):
        add("automatic Git checks", True,
            "not a Git repository yet; run `git init` and "
            "`python3 tools/hooks/install.py` to enable automatic checks.")
    else:
        proc = subprocess.run(
            [sys.executable,
             os.path.join(ROOT, "tools", "hooks", "install.py"), "--check"],
            cwd=ROOT, text=True, capture_output=True)
        add("automatic Git checks", proc.returncode == 0,
            "Git hooks are not installed; run "
            "`python3 tools/hooks/install.py` to enable automatic checks.",
            proc.stdout + proc.stderr)

    # The mechanical gates -------------------------------------------------
    gate_hints = {
        "build_catalog.py --check": ("metadata",
            "metadata validation failed; run "
            "`python3 tools/build_catalog.py --check` for the exact findings."),
        "check_loop.py": ("reachability",
            "reachability failed; run `python3 tools/check_loop.py` for the "
            "orphaned or dead links."),
        "scrub_check.py": ("privacy scan",
            "the privacy scan found never-share terms in tracked content; "
            "run `python3 tools/scrub_check.py` for locations (values stay "
            "redacted)."),
        "agnostic_check.py": ("neutrality",
            "neutrality validation failed; run "
            "`python3 tools/agnostic_check.py` for the exact findings."),
    }
    for command, (name, hint) in gate_hints.items():
        tool, *args = command.split()
        code, out = run_tool(tool, *args)
        if name == "privacy scan" and privacy_error is not None and code != 0:
            hint = ("the privacy scan could not run because the private-term "
                    "configuration above is missing or invalid.")
        add(name, code == 0, hint, out)

    return checks, context


def report(checks, verbose, context=None):
    healthy = all(c["ok"] for c in checks)
    print("Sett health" + (f" ({context})" if context else "") + "\n")
    for c in checks:
        print(f"{'✓' if c['ok'] else '✗'} {c['name']}")
        if not c["ok"] and c["hint"]:
            print(f"  {c['hint']}")
        if verbose and c["raw"] and not c["ok"]:
            for line in first_lines(c["raw"]):
                print(f"  | {line}")
        elif verbose and c["raw"]:
            for line in first_lines(c["raw"], 1):
                print(f"  | {line}")
    print()
    if healthy:
        print("Everything looks good.")
        return 0
    print("Fix the ✗ items above; run `python3 tools/doctor.py --verbose` "
          "for validator output.")
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true",
                        help="show the underlying validator output")
    args = parser.parse_args(argv)
    refused = refuse_unknown(LAYOUT, "doctor")
    if refused:
        sys.stderr.write(refused + "\n")
        return 2
    if LAYOUT.kind == "member":
        print("Sett health\n")
        print("✓ member layout")
        print("This is a Sett member (optional pack), not a workspace; "
              "workspace checks do not apply. Run doctor from a workspace "
              "or the Sett source checkout.")
        return 0
    values_rel = LAYOUT.physical_rel("workspace/00_meta/values.json")
    active_rel = LAYOUT.physical_rel("workspace/20_intent/active")
    checks, context = check(values_rel, active_rel)
    return report(checks, args.verbose, context)


if __name__ == "__main__":
    sys.exit(main())
