#!/usr/bin/env python3
"""Create a ready-to-use Sett workspace with one command.

usage:
  python3 tools/new.py ~/setts/my-workspace            interactive wizard
  python3 tools/new.py TARGET --non-interactive --name NAME \
      --workspace-id ID --goal GOAL [--no-private-terms | --private-term] \
      [--hooks portable] [--verbose]

The wizard asks a few plain-English questions, then fills, validates and
finalizes the workspace. It refuses ambiguous destinations, never mutates the
template checkout, and never prints a private term. The generated workspace
starts at its own AGENTS.md.

Exit: 0 ready, 1 refused or failed setup, 2 usage.
"""

import argparse
import getpass
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sett_setup import (  # noqa: E402
    SetupError, SOURCE_LAYOUT, build_workspace, check_workspace_id,
    kebab, normalize_workspace_id, validate_family_source, validate_target)


def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"{prompt}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit(1)
    return answer or (default or "")


def ask_choice(prompt, options):
    print(prompt)
    for index, label in enumerate(options, start=1):
        print(f"  {index}. {label}")
    while True:
        answer = ask("Choose 1 or 2")
        if answer in {"1", "2"}:
            return options[int(answer) - 1]
        print("Please answer 1 or 2.")


def gather_answers(args, target):
    """Interactive interview. Each answer maps onto one setup fact."""
    print("Set up a new Sett workspace at:")
    print(f"  {target}")
    print("Answer a few questions; defaults are shown in [brackets].\n")

    name = args.name or ask("What should your agent call you?",
                            getpass.getuser())

    default_id = normalize_workspace_id("", target.name)
    workspace_id = args.workspace_id or ask("Workspace ID", default_id)
    while True:
        problem = check_workspace_id(workspace_id)
        if not problem:
            break
        print(problem)
        suggestion = kebab(workspace_id)
        workspace_id = ask("Workspace ID",
                           suggestion if suggestion else None)

    goal = args.goal or ask(
        "What do you want this workspace to help you with first?")

    privacy = None
    if args.no_private_terms:
        privacy = []
    elif args.private_terms is not None:
        privacy = args.private_terms
    if privacy is None:
        choice = ask_choice(
            "Are there any literal names, codenames, IDs or terms that must "
            "never appear in commits or external output?",
            ("No", "Yes, add private terms"))
        if choice == "No":
            privacy = []
        else:
            print("Enter them one per line; an empty line finishes. "
                  "They are stored only in the ignored .sett-private/ "
                  "and are never printed.")
            privacy = []
            while True:
                term = input("> ")
                if not term.strip():
                    break
                privacy.append(term)
    return name, workspace_id, goal, privacy


def success(target):
    print(f"\nSett workspace ready: {target}\n")
    print("✓ identity configured")
    print("✓ privacy choice recorded")
    print("✓ first task captured")
    print("✓ automatic Git checks installed")
    print("✓ integrity checks passed")
    print(f"""
Open this folder with your AI agent and say:

  Read AGENTS.md and help me with my current task.

Health check:
  cd {target} && python3 tools/doctor.py
""")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="destination for the new workspace")
    parser.add_argument("--name", help="what your agent should call you")
    parser.add_argument("--workspace-id", help="kebab-case workspace name")
    parser.add_argument("--goal", help="your first real objective")
    privacy = parser.add_mutually_exclusive_group()
    privacy.add_argument("--no-private-terms", action="store_true",
                         help="explicitly record that there are no private "
                              "literal terms")
    privacy.add_argument("--private-terms", nargs="+",
                         help=argparse.SUPPRESS)  # values never appear in help
    parser.add_argument("--hooks", choices=["portable"], default="portable",
                        help=argparse.SUPPRESS)
    parser.add_argument("--non-interactive", action="store_true",
                        help="never prompt; fail with the missing answers")
    parser.add_argument("--verbose", action="store_true",
                        help="show setup mechanics (private values stay "
                             "redacted)")
    args = parser.parse_args(argv)

    try:
        validate_family_source()
        target = validate_target(args.target)
        if args.non_interactive:
            missing = [flag for flag, value in (
                ("--name", args.name), ("--workspace-id", args.workspace_id),
                ("--goal", args.goal)) if not (value or "").strip()]
            privacy = None
            if args.no_private_terms:
                privacy = []
            elif args.private_terms is not None:
                privacy = args.private_terms
            if privacy is None:
                missing.append("--no-private-terms or --private-terms")
            if missing:
                print("new: missing required answers: " + ", ".join(missing)
                      + "\nSupply them as flags; do not rely on prompts in "
                        "non-interactive mode.", file=sys.stderr)
                return 2
            name = args.name.strip()
            workspace_id = args.workspace_id.strip()
            goal = args.goal.strip()
        else:
            name, workspace_id, goal, privacy = gather_answers(args, target)

        problem = check_workspace_id(workspace_id)
        if problem:
            print(f"new: {problem}", file=sys.stderr)
            return 1
        build_workspace(target, name, workspace_id, goal, privacy,
                        verbose=args.verbose)
    except SetupError as exc:
        print(f"new: {exc}", file=sys.stderr)
        print("\nNothing is ready yet; fix the cause and rerun the command.",
              file=sys.stderr)
        return 1
    success(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
