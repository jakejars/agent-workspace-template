#!/usr/bin/env python3
"""Standalone-workspace setup logic shared by tools/new.py.

Novice-facing behavior lives in new.py; this module owns the mechanics it
orchestrates. It reuses the existing machinery wherever a rule already has an
owner — instantiate.py for the fill/finalize/check walk, scrub_check.py for
private-term semantics, hooks/install.py for portable Git hooks — and adds
only what those tools do not own: family-source validation, destination
topology, the extracted copy, and first-intent capture.

Stdlib only. Never prints a private term; diagnostics report counts only.
"""

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SOURCE = TOOLS.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(TOOLS))

from sett_layout import SettLayout, refuse_unknown  # noqa: E402
import scrub_check  # noqa: E402

SOURCE_LAYOUT = SettLayout(SOURCE)

# Canonical member paths, filled by the mechanical fill (placeholders.md).
VALUES_REL = "00_meta/values.json"
SENTINEL_REL = "00_meta/.uninitialised"
READY_REL = "00_meta/ready.json"
INTENT_ACTIVE_REL = "20_intent/active"
PRIVATE_DIR = ".sett-private"
NO_TERMS_FILE = f"{PRIVATE_DIR}/no-private-terms.json"
NEVER_SHARE_FILE = f"{PRIVATE_DIR}/never-share.txt"

# Family-level support an extracted workspace copies in (migrations.md).
FAMILY_COPIES = ("tools", ".githooks", ".gitignore", "doctrine",
                 "_templates", "LOOP.md", "LICENSE", "NAMESPACE.md")
# Files copied verbatim from these top-level names, or named directly.
# Everything else at the family root is not part of an instance.
ROOT_COPY = {".gitignore", "LOOP.md", "LICENSE", "NAMESPACE.md"}
JUNK = shutil.ignore_patterns("__pycache__", "*.pyc", ".sett-private")

KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class SetupError(Exception):
    """A refusal with a plain-language message (new.py prints it verbatim)."""


def kebab(slug):
    """Lowercase ASCII kebab-case (doctrine/naming.md)."""
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", slug.lower())).strip("-")


# ---------------------------------------------------------------------------
# source and destination topology


def validate_family_source():
    """Refuse to run anywhere but a family/template checkout."""
    layout = SOURCE_LAYOUT
    if layout.kind == "workspace":
        raise SetupError(
            "This is already a Sett workspace, not the Sett source template.\n"
            "Create new workspaces from the template checkout.")
    if layout.kind == "member":
        raise SetupError(
            "This is a Sett member, not the Sett source template.\n"
            "Create new workspaces from the template checkout.")
    refused = refuse_unknown(layout, "new")
    if refused:
        raise SetupError(refused)
    for evidence in ("workspace/AGENTS.md", "workspace/00_meta/.uninitialised",
                     "NAMESPACE.md", "tools/instantiate.py"):
        if not (SOURCE / evidence).is_file():
            raise SetupError(
                f"The Sett source checkout is incomplete: {evidence} is "
                "missing. Re-clone the repository or restore the file.")


def normalize_workspace_id(raw, basename):
    """Offer the directory name when it is already valid; suggest otherwise."""
    candidate = (raw or "").strip()
    if not candidate and basename:
        candidate = kebab(basename)
    return candidate


def check_workspace_id(candidate):
    if not candidate:
        return "a workspace id is required"
    if not KEBAB_RE.match(candidate):
        suggestion = kebab(candidate)
        if suggestion and KEBAB_RE.match(suggestion):
            return (f"'{candidate}' is not a valid workspace id (lowercase "
                    f"kebab-case). Did you mean '{suggestion}'?")
        return (f"'{candidate}' is not a valid workspace id "
                "(lowercase kebab-case, letters digits and dashes)")
    return None


def first_sett_ancestor(path):
    """Nearest ancestor (inclusive) carrying NAMESPACE.md — a Sett root by
    doctrine (the nearest ancestor containing it)."""
    cursor = Path(path).resolve()
    while True:
        if (cursor / "NAMESPACE.md").is_file():
            return cursor
        if cursor.parent == cursor:
            return None
        cursor = cursor.parent


def contains_sett_root(directory):
    """True if a directory tree at or below `directory` holds a Sett root."""
    directory = Path(directory)
    if (directory / "NAMESPACE.md").is_file():
        return True
    for sub in sorted(directory.iterdir()):
        if sub.is_dir():
            if (sub / "NAMESPACE.md").is_file():
                return True
            for nested in sub.rglob("NAMESPACE.md"):
                if nested.is_file():
                    return True
    return False


def validate_target(raw_target):
    """Refuse unsafe or ambiguous destinations before anything is copied."""
    target = Path(raw_target).expanduser()
    try:
        target = target.resolve(strict=False)
    except OSError as exc:
        raise SetupError(f"Cannot resolve destination '{raw_target}': {exc}")
    if target == target.parent:
        raise SetupError(
            "Refusing to create a workspace at the filesystem root.")
    if target == SOURCE_LAYOUT.root or SOURCE_LAYOUT.root in target.parents:
        raise SetupError(
            "Refusing to create a workspace inside the Sett source checkout.\n"
            "Choose a destination outside it, for example ~/setts/my-workspace.")
    ancestor = first_sett_ancestor(target.parent)
    if ancestor:
        raise SetupError(
            f"Refusing to nest a workspace inside the Sett root at "
            f"{ancestor}.\nChoose a destination outside any Sett root.")
    if target.exists():
        if not target.is_dir():
            raise SetupError(f"'{target}' exists and is not a directory.")
        if any(target.iterdir()):
            raise SetupError(
                f"'{target}' is not empty. This wizard only creates a "
                "workspace in an empty, new directory.")
        if contains_sett_root(target):
            raise SetupError(
                f"'{target}' contains another Sett root. Choose a different "
                "destination.")
    parent = target.parent
    if not parent.exists():
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise SetupError(f"Cannot create '{parent}': {exc}")
    if not os.access(parent, os.W_OK):
        raise SetupError(f"Cannot write to '{parent}'.")
    return target


# ---------------------------------------------------------------------------
# the extracted copy


def _copy_file(src, dst):
    shutil.copy2(src, dst)          # preserves executable bits on .githooks


def source_files():
    """Tracked files plus safe new files in the source, like test_instance.

    Instance state (values.json, generated catalogs, the private store,
    untracked journals/runs/intents) is never part of a fresh workspace, so a
    dirty maintenance checkout cannot leak into someone's first sett.
    """
    def git(*args):
        proc = subprocess.run(["git", *args], cwd=SOURCE, text=True,
                              capture_output=True, check=True)
        return {n for n in proc.stdout.split("\0") if n}
    names = git("ls-files", "-z")
    blocked_parts = {".sett-private", ".sett-cache", "__pycache__", "work",
                     "artifacts"}
    blocked = {"CATALOG.md", "CATALOG.json", "workspace/00_meta/values.json"}
    for name in git("ls-files", "--others", "--exclude-standard", "-z"):
        parts = set(Path(name).parts)
        dynamic = ((name.startswith("workspace/30_memory/journal/")
                    and not name.endswith(("README.md", "INDEX.md")))
                   or (name.startswith("workspace/90_runs/")
                       and not name.endswith(("README.md", "INDEX.md")))
                   or (name.startswith("workspace/20_intent/active/")
                       and not name.endswith("README.md")))
        if name not in blocked and not parts & blocked_parts and not dynamic:
            names.add(name)
    return names


def instance_rel(name):
    """Map a source-relative path onto the extracted instance, or None."""
    if name.startswith("workspace/"):
        return name[len("workspace/"):]
    top = name.split("/", 1)[0]
    if name in ROOT_COPY or top in {"tools", ".githooks", "doctrine",
                                    "_templates"}:
        return name
    return None


def copy_workspace(source_root, destination):
    """Build the extracted-workspace shape (migrations.md, extraction steps)."""
    source_root = Path(source_root)
    copied = 0
    for name in sorted(source_files()):
        rel = instance_rel(name)
        if not rel or "__pycache__" in Path(rel).parts:
            continue
        src = source_root / name
        dst = destination / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        _copy_file(src, dst)          # copy2 preserves executable bits
        copied += 1
    sentinel = destination / SENTINEL_REL
    if not sentinel.is_file():
        raise SetupError(
            "The copied workspace carries no .uninitialised sentinel; the "
            "source checkout is incomplete or already instantiated.")
    if not (destination / "AGENTS.md").is_file():
        raise SetupError(
            "The copied workspace carries no AGENTS.md entrance; the source "
            "checkout is incomplete.")
    (destination / "README.md").write_text(instance_readme(), encoding="utf-8")
    return copied


def instance_readme(workspace_id=None):
    """The generated novice-facing workspace README (exempt, root README)."""
    name = workspace_id or "my workspace"
    return f"""# {name}

This is a Sett workspace.

For AI agents: start at `AGENTS.md`.

For humans:

- current tasks live in `20_intent/`
- durable memory lives in `30_memory/`
- knowledge and decisions live in `40_knowledge/`
- permissions and boundaries live in `80_governance/`

To check workspace health:

    python3 tools/doctor.py

`00_meta/values.json` is tracked configuration: non-secret setup values only.
Private literal terms belong only in the ignored `.sett-private/`.
The full mechanics are documented under `doctrine/` and `NAMESPACE.md`.
"""


# ---------------------------------------------------------------------------
# values, privacy, first intent


def write_values(destination, name, workspace_id):
    """Tracked, non-secret configuration only (placeholders.md)."""
    values_path = destination / VALUES_REL
    values = json.loads(values_path.read_text(encoding="utf-8")) \
        if values_path.is_file() else {}
    values["PRINCIPAL_NAME"] = name
    values["WORKSPACE_ID"] = workspace_id
    values_path.write_text(json.dumps(values, indent=2) + "\n", encoding="utf-8")


def validate_private_terms(terms):
    """Same usability semantics as scrub_check (one owner, no drift)."""
    for index, term in enumerate(terms, start=1):
        stripped = term.strip()
        if len(stripped) < 3 or stripped.casefold() in {
                "none", "n/a", "tbd", "todo", "unknown"}:
            # Never echo the term itself.
            return (f"line {index} is not a usable private term (too short or "
                    "a placeholder word). Terms are at least three characters.")
    return None


def write_privacy(destination, terms):
    """Translate the plain-language choice into the filesystem state.

    `terms` falsy -> explicit no-private-terms confirmation.
    `terms` list  -> ignored never-share.txt, one term per line.
    """
    private_dir = destination / PRIVATE_DIR
    private_dir.mkdir(exist_ok=True)
    if not terms:
        (destination / NO_TERMS_FILE).write_text(
            json.dumps({"version": 1, "confirmed": True}) + "\n",
            encoding="utf-8")
    else:
        text = "".join(f"{term.strip()}\n" for term in terms)
        (destination / NEVER_SHARE_FILE).write_text(text, encoding="utf-8")
        error = validate_private_terms(terms)
        if error:
            raise SetupError(f"Privacy setup is incomplete: {error}")
        # The scrub gate is the authority; confirm against it.
        _, error = scrub_check.load_terms(destination, False)
        if error:
            raise SetupError(f"Privacy setup is incomplete: {error}")


def title_from_goal(goal):
    """A short title: first clause of the goal, trimmed."""
    head = re.split(r"[.!?;\n]", goal.strip(), maxsplit=1)[0].strip()
    head = head.rstrip("(—-– ")
    if len(head) > 60:
        head = head[:57].rsplit(" ", 1)[0] + "…"
    return head or goal.strip()[:60]


def first_intent_record(goal, slug, workspace_id, today):
    """A captured first intent (workspace/20_intent/INDEX.md, the kit)."""
    title = title_from_goal(goal)
    body = goal.strip()
    if len(body) > 1200:                    # the record stays under its cap
        body = body[:1197] + "…"
    # The routing description is capped by schema; trim the title until the
    # normalized one-line form fits.
    template = ("{title} — current objective. Use when deciding whether "
                "work belongs to {slug}. Not for other tasks (see "
                "20_intent/INDEX.md).")
    description = template.format(title=title, slug=slug)
    while len(description) > 180 and len(title) > 8:
        title = title[:len(title) - 5].rstrip() + "…"
        description = template.format(title=title, slug=slug)
    return f"""---
id: intent-{slug}
type: intent
status: draft
description: >
  {description}
scope: workspace
lifecycle: captured
load: cue
owner: human
updated: {today}
---

# {title}

## Objective

{body}

## Constraints

- Follow the current user request and standing workspace boundaries.

## Success definition

- [ ] The requested outcome is completed or clarified into checkable criteria.
- [ ] The current checkpoint records the result or next concrete step.

## Delegation deltas

None.

## Not in scope

- Unrequested work outside this objective.

## Checkpoint

- State: Objective captured during setup.
- Next: Clarify the task only where necessary, then begin useful work.
- Open: None recorded yet.
- Evidence: Workspace setup.
"""


def create_first_intent(destination, goal, workspace_id, today=None):
    """Capture the user's first real objective as the required first intent."""
    goal = (goal or "").strip()
    if not goal:
        raise SetupError("A first objective is required before finalization.")
    today = today or datetime.date.today().isoformat()
    active = destination / INTENT_ACTIVE_REL
    slug = kebab(title_from_goal(goal))[:30].strip("-") or "first-objective"
    candidate, n = slug, 2
    while (active / f"{candidate}.md").exists():
        candidate = f"{slug}-{n}"
        n += 1
    target = active / f"{candidate}.md"
    target.write_text(
        first_intent_record(goal, candidate, workspace_id, today),
        encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# orchestration


def run(tool_rel, *args, cwd):
    """Run a Sett tool with an argument array; output is captured, not shown."""
    return subprocess.run(
        [sys.executable, str(Path(cwd) / tool_rel), *args],
        cwd=str(cwd), text=True, capture_output=True)


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), text=True,
                          capture_output=True)


def install_hooks(destination):
    """Portable hooks: local core.hooksPath, no global configuration."""
    result = run("tools/hooks/install.py", cwd=destination)
    if result.returncode:
        detail = (result.stdout + result.stderr).strip()
        raise SetupError(
            "Automatic Git checks could not be installed"
            + (f": {detail}" if detail else "."))
    return result


def build_workspace(destination, name, workspace_id, goal, privacy_terms,
                    today=None, verbose=False):
    """Create, fill, finalize and validate the workspace at `destination`.

    The workspace is built and validated in a temporary sibling directory and
    moved into place only after every gate passes, so a failed setup never
    leaves a target that looks ready.
    """
    today = today or datetime.date.today().isoformat()
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(
        prefix=f".{destination.name}.sett-building-",
        dir=destination.parent))
    try:
        copy_workspace(SOURCE, staging)
        proc = git("init", "-q", cwd=staging)
        if proc.returncode:
            raise SetupError(f"git init failed: {proc.stderr.strip()}")
        write_values(staging, name, workspace_id)
        write_privacy(staging, privacy_terms)
        result = run("tools/instantiate.py", "--minimal", "--date", today,
                     cwd=staging)
        if result.returncode:
            raise SetupError("The mechanical fill failed:\n"
                             + (result.stdout + result.stderr).strip())
        create_first_intent(staging, goal, workspace_id, today)
        install_hooks(staging)
        result = run("tools/instantiate.py", "--finalize", "--hooks",
                     "portable", "--date", today, cwd=staging)
        if result.returncode:
            raise SetupError("Finalization failed:\n"
                             + (result.stdout + result.stderr).strip())
        result = run("tools/instantiate.py", "--check", cwd=staging)
        if result.returncode:
            raise SetupError("The readiness check failed:\n"
                             + (result.stdout + result.stderr).strip())
        result = run("tools/doctor.py", cwd=staging)
        if result.returncode:
            raise SetupError("The health check failed:\n"
                             + (result.stdout + result.stderr).strip())
        if verbose:
            print(f"[verbose] validated in {staging}")
        os.replace(staging, destination)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return destination
