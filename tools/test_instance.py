#!/usr/bin/env python3
"""Acceptance test: a stranger's instance, end to end. Silent = pass.

  python3 tools/test_instance.py            run it
  python3 tools/test_instance.py --fast     skip the nested regression suites
  python3 tools/test_instance.py --keep     leave the instance on disk and
                                            print its path

Every other test validates the family checkout — the maintenance mode nobody
ships in. This one does what a user does: take the template, answer the
interview, instantiate, file one record from *every* kit, work a session,
close it, and commit through the hooks. Each stage asserts against the real
gates, so a kit or a doctrine step that cannot survive contact with the
validator fails here rather than in someone's first session.

Adding a kit adds a case automatically: kits are discovered, their markers are
filled from KIT_MARKERS, and an unknown marker is a failure, not a guess.
"""

import datetime
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from workspace_layout import PRIVATE_DIRS

TOOLS = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.dirname(TOOLS)
TODAY = "2026-08-24"
REVIEW = "2026-11-24"

# One value per marker any kit declares. A kit that adds a marker fails until
# it is answered here, which is how a new kit gets exercised instead of skipped.
KIT_MARKERS = {
    "TODAY": TODAY,
    "HHMM": "1200",
    "REVIEW_DATE": REVIEW,
    "EXPIRY_DATE": REVIEW,
    "SLUG": "worked-example",
    "TITLE": "Worked example",
    "DECISION_ID": "0001",
    "PACKET_ID": "DP-2026-001",
    "BOARD_SLUG": "release-readiness",
    "BOARD_NAME": "Release readiness",
    "CAPABILITY_NAME": "worked-capability",
    "RUN_ID": f"{TODAY}-worked-example",
    "CLOSED_AT": f"{TODAY}T12:00:00Z",
    "INTENT_SLUG": "worked-example",
    "INTENT_TITLE": "Worked example",
    "SYSTEM_SLUG": "worked-system",
    "SYSTEM_NAME": "Worked system",
    "FIELD": "design",
    "PILLAR": "",
    "TOPIC": "worked-topic",
    "TOPIC_NAME": "Worked topic",
    "SPECIMEN": "worked-specimen",
    "SPECIMEN_NAME": "Worked specimen",
}

SECOND_INTENT = "second-example"
# A kit leaves the neighbouring record's name to the filer. Each of these maps
# a `<slot>` path onto something this test creates or the template ships.
PATH_FIXUPS = (
    ("workspace/20_intent/active/<other>.md",
     f"workspace/20_intent/active/{SECOND_INTENT}.md"),
    ("workspace/70_seams/<other>.md", "workspace/70_seams/harness.md"),
    ("registry/<other>/manifest.yml", "registry/example-capability/manifest.yml"),
    ("workspace/90_runs/<run-id>/run.md",
     f"workspace/90_runs/{KIT_MARKERS['RUN_ID']}/run.md"),
    ("workspace/20_intent/active/<intent>.md",
     f"workspace/20_intent/active/{KIT_MARKERS['INTENT_SLUG']}.md"),
    ("workspace/30_memory/preferences/<preference>.md",
     f"workspace/30_memory/preferences/{KIT_MARKERS['SLUG']}.md"),
    ("library/fields/<field>/<topic>/README.md",
     f"library/fields/{KIT_MARKERS['FIELD']}/{KIT_MARKERS['TOPIC']}/README.md"),
)

COPY_TO_RE = re.compile(r"\*\*Copy to:\*\*\s*\n?\s*`([^`]+)`")
MARKER_RE = re.compile(r"\{\{([A-Z_]+)\}\}")
FENCE_RE = re.compile(r"```markdown\n(.*?)```", re.S)
# A kit's prose slots. Not `<!-- -->`, not `<<TOKEN>>`, not a bare comparison.
SLOT_RE = re.compile(r"<(?!!--)(?!<)([^<>\n]{2,})>")
INDEX_NAMES = ("INDEX.md", "README.md")


def run(root, tool, *args):
    proc = subprocess.run([sys.executable, os.path.join(root, "tools", tool),
                           *args], cwd=root, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def git(root, *args, check=True):
    proc = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if check:
        assert proc.returncode == 0, f"git {' '.join(args)}:\n{proc.stdout}{proc.stderr}"
    return proc


def write(root, rel, text):
    target = os.path.join(root, rel)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(text)


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as handle:
        return handle.read()


def append(root, rel, text):
    with open(os.path.join(root, rel), "a", encoding="utf-8") as handle:
        handle.write(text)


def gates_pass(root, stage):
    """The session-close suite, in the order doctrine/gates.md runs it."""
    for tool, args in (("scrub_check.py", ()), ("build_catalog.py", ("--check",)),
                       ("skills.py", ("check",)),
                       ("check_loop.py", ()), ("pipeline.py", ("check",)),
                       ("agnostic_check.py", ()),
                       ("journal_guard.py", ("--selftest",))):
        code, out = run(root, tool, *args)
        assert code == 0, f"[{stage}] {tool} {' '.join(args)} failed:\n{out}"


# --------------------------------------------------------------------------
# 1. what a stranger downloads


def clone_source(root, require_template=True):
    """Tracked files plus safe new implementation files from this checkout."""
    listing = subprocess.run(["git", "ls-files", "-z"], cwd=SOURCE,
                             capture_output=True, text=True, check=True)
    pending = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=SOURCE, capture_output=True, text=True, check=True)
    # Exclude existing legacy stores and disposable caches from copied source.
    blocked_parts = {*PRIVATE_DIRS, ".workspace-cache", ".sett-cache",
                     "__pycache__", "scratch", "artifacts", "work"}
    blocked_paths = {"CATALOG.md", "CATALOG.json",
                     "workspace/00_meta/values.json"}
    names = {name for name in listing.stdout.split("\0")
             if name and name not in blocked_paths
             and not set(Path(name).parts) & blocked_parts
             and Path(SOURCE, name).is_file()}
    for name in (n for n in pending.stdout.split("\0") if n):
        parts = set(Path(name).parts)
        dynamic = (name.startswith("workspace/30_memory/journal/") and
                   not name.endswith(("README.md", "INDEX.md"))) or \
                  (name.startswith("workspace/90_runs/") and
                   not name.endswith(("README.md", "INDEX.md"))) or \
                  (name.startswith("workspace/20_intent/active/") and
                   not name.endswith("README.md"))
        if (name not in blocked_paths and not parts & blocked_parts and not dynamic
                and Path(SOURCE, name).is_file()):
            names.add(name)
    assert names, "no tracked files — is the source a Git repository?"
    for name in sorted(names):
        target = os.path.join(root, name)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(os.path.join(SOURCE, name), target)
    if require_template:
        assert os.path.isfile(os.path.join(root, "workspace/00_meta/.uninitialised")), \
            "the sentinel is not tracked — a clone would arrive already 'instantiated'"


# --------------------------------------------------------------------------
# 2. the interview's output, then the mechanical walk


def answer_interview(root, home):
    machine = os.path.join(home, "MACHINE.md")
    write(home, "MACHINE.md", "# Machine\n\nA laptop, macOS, Python 3, Git.\n")
    write(root, "workspace/00_meta/values.json",
          '{\n "PRINCIPAL_NAME": "Jane Okoro",\n'
          ' "PRINCIPAL_EMAIL": "jane@example.com",\n'
          ' "ORG_NAME": "Example Ltd",\n'
          f' "MACHINE_FILE": "{machine}",\n'
          ' "WORKSPACE_ID": "okoro-consulting",\n'
          f' "WORKSPACE_PATH": "{os.path.join(root, "workspace")}",\n'
          f' "SHARED_CONTEXT_PATH": "{os.path.join(root, "shared-context")}",\n'
          f' "REGISTRY_PATH": "{os.path.join(root, "registry")}",\n'
          ' "LIBRARY_PATH": "",\n'
          ' "OBJECTION_WINDOW_HOURS": "48"\n}\n')
    # An unanswered library path closes that seam; the other two stay open.
    # Built from parts: this file is copied into the instance, and a literal
    # term here would be a hit against itself.
    write(root, ".workspace-private/never-share.txt",
          "zz-example-" + "private-term\n")


def instantiate(root):
    code, out = run(root, "instantiate.py", "--date", TODAY)
    assert code == 0, f"instantiate refused:\n{out}"
    code, out = run(root, "instantiate.py", "--check")
    assert code == 1 and "finalize" in out, f"a fill must not claim readiness:\n{out}"
    code, out = run(root, "instantiate.py")
    assert code == 0 and "checkpoint exists" in out.lower(), \
        f"a second fill must resume, not erase progress:\n{out}"

    body = read(root, "workspace/10_identity/principal.md")
    assert "Jane Okoro" in body and "<<" not in body, body[:400]
    fixtures = read(root, "tools/test_gates.py")
    assert "<<PRINCIPAL_NAME>>" in fixtures, \
        "the fill reached tools/ and disarmed the negative tests"
    library = read(root, "workspace/70_seams/library.md")
    assert "status: stub" in library and "not open" in library, library[:400]
    registry = read(root, "workspace/70_seams/registry.md")
    assert "status: draft" in registry and root in registry, \
        "a linked seam must keep its answers and hold the real path"
    gates_pass(root, "instantiated")


# --------------------------------------------------------------------------
# 3. one record from every kit


def seed_journal(root):
    """The entry the memory-fact kit cites as its support.

    A promoted fact must point at the observation it came from, so the kit
    names one. Writing it first is what a real session does — journal the
    event, then promote from it.
    """
    entry = (f"{TODAY}-{KIT_MARKERS['HHMM']}-{KIT_MARKERS['SLUG']}.md")
    write(root, f"workspace/30_memory/journal/{entry}",
          f"---\ndate: {TODAY}T12:00\nkind: event\n"
          "refs: [00_meta/values.json]\n---\n\n"
          "Observed the thing the worked-example fact records.\n")


def fill_slots(text):
    """Replace a kit's remaining `<prose slot>` guidance with usable prose."""
    return SLOT_RE.sub(lambda m: m.group(1).split(",")[0].split(";")[0].strip()
                       .replace("`", "").replace("|", "or") or "example", text)


def fill_paths(text):
    """Point the kits' `<slot>` paths at records this test actually creates.

    These are the filer's job, not the kit's claim — a kit cannot know the
    neighbouring intent's name. Anything the kit *hardcodes* is left alone, so
    a route that cannot resolve from the kit's own destination still fails.
    """
    for literal, real in PATH_FIXUPS:
        text = text.replace(literal, real)
    return text


def door_for(root, rel):
    """The door that must list `rel`: its own directory's, else its parent's."""
    parts = rel.split("/")
    start = len(parts) - 1 if parts[-1] not in INDEX_NAMES else len(parts) - 2
    for depth in range(start, 0, -1):
        for name in INDEX_NAMES:
            candidate = "/".join(parts[:depth] + [name])
            if candidate != rel and os.path.isfile(os.path.join(root, candidate)):
                return candidate
    return None


def kits(root):
    """Every kit that names a destination, with its record and that path."""
    found = []
    for directory, _, names in os.walk(os.path.join(root, "_templates")):
        for name in sorted(names):
            if not name.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(directory, name), root)
            text = read(root, rel)
            destination = COPY_TO_RE.search(text)
            fence = FENCE_RE.search(text)
            if not destination:
                continue
            assert fence, f"{rel} names a destination but ships no example record"
            found.append((rel, fence.group(1), destination.group(1)))
    assert len(found) >= 14, f"only {len(found)} kits discovered"
    return sorted(found)


def place(root, kit, record, destination, overrides=None):
    """Write one filled kit to its documented home and link it from its door."""
    markers = dict(KIT_MARKERS, **(overrides or {}))

    def fill(text):
        def swap(match):
            name = match.group(1)
            assert name in markers, \
                f"{kit} uses {{{{{name}}}}}, which this test cannot fill"
            return markers[name]
        return MARKER_RE.sub(swap, text)

    # `[{{PILLAR}}/]` marks an optional path segment.
    target = fill(re.sub(r"\[([^\]]*)\]", "", destination)).rstrip("/")
    if kit.endswith("capability.md"):
        target = f"{target}/README.md"          # the kit names a directory
    door = door_for(root, target)
    assert door, f"{target} has no door above it"
    body = fill_paths(fill(record))
    # `(see <ref>)` is the filer's job — the kit cannot know the neighbour.
    # A route the kit spells out itself is left alone, and still has to resolve.
    body = re.sub(r"\(see\s+<[^>]+>\s*\)", f"(see {door})", body)
    write(root, target, fill_slots(body))
    append(root, door, f"\n- [{os.path.basename(target)}]"
                       f"({os.path.relpath(target, os.path.dirname(door))})\n")
    return target


def file_every_kit(root):
    """Every kit, at its own documented destination, linked from its door.

    Shallowest destination first: a topic README is the door its specimens
    are listed from, so it has to exist before they are filed.
    """
    filed = []
    ordered = sorted(kits(root),
                     key=lambda k: re.sub(r"\[[^\]]*\]", "", k[2]).count("/"))
    for kit, record, destination in ordered:
        target = place(root, kit, record, destination)
        filed.append((kit, target))
        if kit.replace(os.sep, "/") == "_templates/pipeline/README.md":
            # A pipeline kit is one definition with two small stage contracts.
            # Exercise each fenced file; checking only PIPELINE.md would hide
            # a stage kit that cannot pass the real schema or graph gates.
            records = FENCE_RE.findall(read(root, kit))
            assert len(records) == 3, f"{kit} must ship its two worked stages"
            for stage, contract in zip(("01_prepare", "02_review"), records[1:]):
                place(root, kit, contract,
                      f"{os.path.dirname(target)}/{stage}/STAGE.md")
        if kit.endswith("intent.md"):
            # A second intent so the kit's `<other>` neighbour is a real file.
            place(root, kit, record, destination,
                  {"INTENT_SLUG": SECOND_INTENT, "INTENT_TITLE": "Second example"})
    assert any(kit.endswith("skill/README.md") and target.endswith("/SKILL.md")
               for kit, target in filed), "the skill kit must file a native SKILL.md"
    return filed


def execute_pipeline(root):
    """Start the copied kit and reconstruct its next stage from disk alone."""
    run_id = f"{TODAY}-pipeline-example"
    code, out = run(root, "pipeline.py", "start", "--pipeline", KIT_MARKERS["SLUG"],
                    "--run", run_id, "--intent", "intent-worked-example")
    assert code == 0, f"pipeline start refused the copied kit:\n{out}"
    folder = f"workspace/90_runs/{run_id}"
    assert os.path.isfile(os.path.join(root, folder, "run.md"))
    for stage in ("01_prepare", "02_review"):
        assert os.path.isdir(os.path.join(root, folder, stage)), stage
    contract = read(root, f"workspace/60_capabilities/pipelines/"
                    f"{KIT_MARKERS['SLUG']}/01_prepare/STAGE.md")
    output = re.search(r"^output:\s*(\S+)\s*$", contract, re.M)
    assert output, "the prepare stage must name its inspectable artifact"
    write(root, f"{folder}/01_prepare/{output.group(1)}",
          "# Prepared material\n\nThe first stage produced an inspectable file.\n")
    code, out = run(root, "pipeline.py", "status", "--run", run_id)
    assert code == 0 and "Next: 02_review" in out, \
        f"a fresh agent cannot reconstruct the second stage:\n{out}"
    code, out = run(root, "check_loop.py", "--graph")
    assert code == 0, f"pipeline reachability failed:\n{out}"
    assert f"60_capabilities/pipelines/{KIT_MARKERS['SLUG']}/01_prepare/STAGE.md" in out
    assert f"90_runs/{run_id}/run.md" in out


# --------------------------------------------------------------------------
# 4. a session: work, journal, close


def work_a_session(root):
    run_id = KIT_MARKERS["RUN_ID"]
    write(root, f"workspace/30_memory/journal/{TODAY}-1300-worked-example.md",
          f"---\ndate: {TODAY}T13:00\nkind: event\n"
          f"refs: [90_runs/{run_id}/run.md]\n---\n\n"
          "Filed one record from every kit to prove the walk.\n")
    write(root, f"workspace/30_memory/journal/{TODAY}-1400-session-digest.md",
          f"---\ndate: {TODAY}T14:00\nkind: digest\n"
          f"refs: [90_runs/{run_id}/run.md]\n---\n\n"
          "Session close: kits filed, gates green, work continues tomorrow.\n")
    write(root, f"workspace/30_memory/journal/{TODAY}-1500-correction.md",
          f"---\ndate: {TODAY}T15:00\nkind: correction\n"
          f"refs: [{TODAY}-1300-worked-example.md]\n---\n\n"
          "The earlier entry undercounted the kits; both entries stand.\n")
    gates_pass(root, "session")

    guard = os.path.join(root, "tools", "journal_guard.py")
    entry = f"workspace/30_memory/journal/{TODAY}-1300-worked-example.md"
    for payload, why in (
            ('{"op": "modify", "path": "%s"}' % entry, "an existing entry"),
            ('{"op": "modify", "path": "tools/check_loop.py"}', "a gate"),
            ('{"op": "create-or-overwrite", "path": "workspace/AGENTS.md"}',
             "the entrance"),
            ('{"op": "create-or-overwrite", '
             '"path": "workspace/00_meta/.uninitialised"}', "the sentinel")):
        proc = subprocess.run([sys.executable, guard], cwd=root, input=payload,
                              capture_output=True, text=True)
        assert proc.returncode == 2, f"the guard allowed a write to {why}"


# --------------------------------------------------------------------------
# 5. the commit a stranger makes


def commit_through_hooks(root):
    git(root, "init", "-q")
    git(root, "config", "core.hooksPath", ".githooks")
    git(root, "config", "user.name", "Jane Okoro")
    git(root, "config", "user.email", "jane@example.com")
    git(root, "add", "-A")
    proc = git(root, "commit", "-m", "instantiate and work one session", check=False)
    assert proc.returncode == 0, \
        f"the hooks refused a clean first commit:\n{proc.stdout}{proc.stderr}"

    tracked = git(root, "ls-files").stdout.split()
    assert "workspace/00_meta/values.json" in tracked
    assert not [n for n in tracked if any(n.startswith(d + "/") for d in PRIVATE_DIRS)], \
        "the private store must never be committed"
    assert not [n for n in tracked if n.startswith("CATALOG.")], \
        "catalogs are query outputs, never tracked"

    # The backstop, from a real instance: mutate an entry, stage it, commit.
    entry = f"workspace/30_memory/journal/{TODAY}-1300-worked-example.md"
    write(root, entry, read(root, entry).replace("Filed one", "Mutated one"))
    git(root, "add", entry)
    proc = git(root, "commit", "-m", "mutate", check=False)
    assert proc.returncode != 0, "the commit hook allowed a journal mutation"
    assert "journal" in (proc.stdout + proc.stderr).lower()
    git(root, "checkout", "--", entry)


def suites_pass_inside_the_instance(root):
    """The shipped regressions must run from where they are shipped to."""
    for suite in ("test_gates.py", "test_gate_corrections.py", "test_skills.py",
                  "test_pipeline.py"):
        code, out = run(root, suite)
        assert code == 0, f"{suite} does not pass inside an instance:\n{out[-3000:]}"


def main(argv):
    flags = argv[1:]
    keep = "--keep" in flags
    # --fast is for focused local checks. CI runs the nested suites too, which
    # catches regressions that appear only inside an extracted instance.
    # Routine commit hooks validate integrity without running this suite.
    fast = "--fast" in flags
    if [a for a in flags if a not in ("--keep", "--fast")]:
        sys.stderr.write(__doc__)
        return 2
    # Only a family checkout can produce an instance. Run from inside one —
    # an extracted workspace, or an instance running its own hooks — there is
    # nothing to instantiate, and saying so beats failing.
    if not os.path.isfile(os.path.join(SOURCE, "workspace/AGENTS.md")):
        print("test_instance: not a family checkout; nothing to instantiate.")
        return 0
    home = tempfile.mkdtemp(prefix="workspace-instance-")
    root = os.path.join(home, "my-workspace")
    os.makedirs(root)
    try:
        clone_source(root)
        answer_interview(root, home)
        instantiate(root)
        seed_journal(root)
        filed = file_every_kit(root)
        execute_pipeline(root)
        work_a_session(root)
        code, out = run(root, "instantiate.py", "--finalize", "--hooks", "portable")
        assert code == 0, f"finalization failed:\n{out}"
        code, out = run(root, "instantiate.py", "--check")
        assert code == 0, out
        gates_pass(root, "closed")
        commit_through_hooks(root)
        if not fast:
            suites_pass_inside_the_instance(root)
    except BaseException:
        sys.stderr.write(f"\ninstance left at {root}\n")
        raise
    else:
        if keep:
            print(f"instance kept at {root}")
            return 0
        shutil.rmtree(home)
    print(f"test_instance: a fresh instance instantiates, files {len(filed)} "
          "kits, resumes a two-stage pipeline, closes a session, and commits through the hooks"
          f"{'' if fast else '; its own suites pass from inside it'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
