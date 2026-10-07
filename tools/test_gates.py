#!/usr/bin/env python3
"""Self-check for the gate suite. `python3 tools/test_gates.py` — silent = pass.

Builds a throwaway workspace in a temp dir, runs the gates against it as
subprocesses, and asserts each planted violation is caught and a clean tree
passes. The negative tests are the point: a gate that cannot fail is
decoration. No framework, no fixtures.
"""

import os
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.abspath(__file__))

CLEAN = {
    "workspace/AGENTS.md": """---
id: entrance
type: doctrine
status: mature
description: >
  The entrance. Use when starting a session. Not for metadata rules (see
  doctrine/schema.json).
load: always
updated: 2026-08-24
boot_static: [workspace/AGENTS.md, workspace/70_seams/SHARED.md]
boot_dynamic: workspace/90_runs/*/handover.md
boot_selector: latest-closed-at
boot_static_cap: 7000
boot_dynamic_cap: 3000
boot_total_cap: 10000
---

# Entrance

Boot: read the [shared view](70_seams/SHARED.md), then the newest handover.
Use [seams](70_seams/INDEX.md) and the
[token registry](00_meta/placeholders.md) only when the work cues them.
""",
    "workspace/00_meta/placeholders.md": """---
id: placeholders
type: register
status: draft
description: >
  The token registry. Use when instantiating. Not for the walk-through
  (see workspace/AGENTS.md).
updated: 2026-08-24
---

# Tokens

| Token | Fills |
|---|---|
| `<<PRINCIPAL_NAME>>` | The human this workspace serves |
""",
    "workspace/70_seams/INDEX.md": """---
id: seams-index
type: doctrine
status: draft
description: >
  Chamber index. Use when looking for a seam. Not for session entry (see
  workspace/AGENTS.md).
updated: 2026-08-24
fields:
  - name: verified_on
    kind: date
    for: seam
---

# Seams

- [shared boot view](SHARED.md)
- [harness](harness.md)
""",
    "workspace/70_seams/SHARED.md": """---
id: workspace-shared-boot
type: doctrine
status: mature
description: >
  Shared boot view. Use when starting a workspace session. Not for seam
  mechanics (see workspace/70_seams/INDEX.md).
load: always
scope: workspace
updated: 2026-08-24
---

# Shared boot view

No linked shared state in this fixture.
""",
    "workspace/70_seams/harness.md": """---
id: seam-harness
type: seam
status: draft
description: >
  The agent runtime seam. Use when wiring hooks. Not for all seams (see workspace/70_seams/INDEX.md).
updated: 2026-08-24
related:
  - type: see_also
    ref: seams-index
---

# Harness

## What crosses

Hooks.

## Direction

Both.

## Inspect point

The run log.

## Control point

The hook configuration.

## What never crosses

Private values.
""",
    "library/LIBRARY.md": """---
id: library-entrance
type: doctrine
status: draft
description: >
  The library door. Use when a task needs reference knowledge. Not for
  the map of what is here (see INDEX.md).
updated: 2026-08-24
---

# Library

The map is [INDEX.md](INDEX.md); the knowledge is under
[fields](fields/README.md).
""",
    "library/INDEX.md": """---
id: library-index
type: doctrine
status: draft
description: >
  The library map. Use when routing to a field. Not for the reading
  rules (see LIBRARY.md).
updated: 2026-08-24
---

# Map

- [door](LIBRARY.md)
- [fields](fields/README.md)
- [inbox](inbox/README.md)
""",
    "library/fields/README.md": """---
id: library-fields
type: doctrine
status: draft
description: >
  The field shelf. Use when choosing a field. Not for filing rules (see
  library/LIBRARY.md).
updated: 2026-08-24
---

# Fields

- [design](design/INDEX.md)
- [typography-layout](design/interface-design/typography-layout/README.md)
""",
    "library/fields/design/INDEX.md": """---
id: field-design
type: field
status: draft
description: >
  The design field. Use when the question is about how a made thing
  looks or behaves. Not for implementation (see library/LIBRARY.md).
updated: 2026-08-24
---

# Design

- [interface-design](interface-design/INDEX.md)
""",
    "library/fields/design/interface-design/INDEX.md": """---
id: pillar-interface-design
type: pillar
status: draft
description: >
  Interface design. Use when the question is about screens and
  interaction. Not for the whole field (see ../INDEX.md).
updated: 2026-08-24
---

# Interface design

- [typography-layout](typography-layout/README.md)
""",
    "library/fields/design/interface-design/typography-layout/README.md": """---
id: topic-typography-layout
type: topic
status: draft
description: >
  Type and grid on screen. Use when laying out text. Not for motion
  (see ../INDEX.md).
updated: 2026-08-24
review_after: 2020-01-01
---

# Typography and layout

Specimen: [a transit wayfinding manual](specimens/transit-wayfinding/NOTE.md).
""",
    "library/fields/design/interface-design/typography-layout/"
    "specimens/transit-wayfinding/NOTE.md": """---
id: specimen-transit-wayfinding
type: specimen
status: draft
description: >
  A signage standards manual. Use when a system needs one grid held
  everywhere. Not for body-text craft (see ../../README.md).
updated: 2026-08-24
---

# Transit wayfinding manual

Link-only; no bytes held.
""",
    "library/inbox/README.md": """---
id: library-inbox
type: doctrine
status: draft
description: >
  The capture zone. Use when filing takes over a minute. Not for filed
  knowledge (see ../INDEX.md).
updated: 2026-08-24
---

# Inbox

One file per capture; promoted or dropped, never reviewed in place.

<!-- lists: *.md -->
""",
    "library/inbox/2026-08-24-a-capture.md": """---
id: capture-a-capture
type: knowledge
status: draft
description: >
  An unfiled capture. Use when promoting it. Not for citation (see
  ../INDEX.md).
provenance: authored
updated: 2026-08-24
review_after: 2020-01-01
---

# A capture

Candidate home: typography-layout.
""",
}

# A journal, a run, and the doors that reach them.
JOURNAL_TREE = {
    "workspace/30_memory/INDEX.md": """---
id: memory-index
type: doctrine
status: draft
description: >
  The memory chamber. Use when filing what happened. Not for intent (see
  workspace/AGENTS.md).
updated: 2026-08-24
---

# Memory

- [journal](journal/README.md)
""",
    "workspace/30_memory/journal/README.md": """---
id: memory-journal
type: doctrine
status: draft
description: >
  The append-only record. Use when writing an entry. Not for promoted
  memory (see workspace/30_memory/INDEX.md).
updated: 2026-08-24
---

# Journal

One file per event.

<!-- lists: *.md -->
""",
    "workspace/30_memory/journal/2026-08-24-1200-first-entry.md":
        "---\ndate: 2026-08-24T12:00\nkind: digest\n"
        "refs: [90_runs/2026-08-24-probe/run.md]\n---\n\nThe run closed.\n",
    "workspace/90_runs/INDEX.md": """---
id: runs-index
type: register
status: draft
description: >
  The session record. Use when opening or closing a run. Not for memory
  (see workspace/30_memory/INDEX.md).
updated: 2026-08-24
---

# Runs

<!-- lists: */run.md -->
""",
    "workspace/90_runs/2026-08-24-probe/run.md": """---
id: run-probe
type: run
status: draft
description: >
  A run record. Use when reconstructing this session. Not for doctrine
  (see workspace/AGENTS.md).
updated: 2026-08-24
---

# Run

Detail lives in 30_memory/journal/ — naming the chamber is not naming an entry,
so `run-untraced` still fails once the entry stops reffing this folder.
""",
}

# Every planted defect is one edit to the entry the clean tree accepts.
ENTRY = "workspace/30_memory/journal/2026-08-24-1200-first-entry.md"
BAD_JOURNAL = {
    "journal-bad-kind": (ENTRY,
                         lambda t: t.replace("kind: digest", "kind: milestone"),
                         "is not one of event | correction | digest"),
    "journal-bad-date": (ENTRY,
                         lambda t: t.replace("date: 2026-08-24T12:00",
                                             "date: yesterday"),
                         "is not YYYY-MM-DDTHH:MM local"),
    "journal-okf-header": (ENTRY,
                           lambda t: t.replace("---\ndate:",
                                               "---\nid: entry\ntype: journal\ndate:"),
                           "and nothing more"),
    "journal-no-header": (ENTRY, lambda t: "Just prose.\n",
                          "missing or unterminated entry header"),
    "journal-dead-ref": (ENTRY,
                         lambda t: t.replace("90_runs/2026-08-24-probe/run.md",
                                             "90_runs/no-such-run/run.md"),
                         "does not resolve"),
    "journal-uncorrected": (ENTRY,
                            lambda t: t.replace("kind: digest", "kind: correction")
                            .replace("refs: [90_runs/2026-08-24-probe/run.md]\n", ""),
                            "must ref the entry it corrects"),
    "journal-unknown-bare-ref": (ENTRY,
                                lambda t: t.replace(
                                    "refs: [90_runs/2026-08-24-probe/run.md]",
                                    "refs: [no-such-id-anywhere]"),
                                "names no id and no entry"),
    # The run.md names the chamber but no entry; only the ref makes it traced.
    "run-untraced": (ENTRY,
                     lambda t: t.replace("90_runs/2026-08-24-probe/run.md",
                                         "30_memory/journal/README.md"),
                     "no journal entry"),
}

BAD_GLOB = {
    "glob-bare-star": ("workspace/90_runs/INDEX.md",
                       lambda t: t.replace("<!-- lists: */run.md -->",
                                           "<!-- lists: * -->"),
                       "is unbounded"),
    "glob-double-star": ("workspace/90_runs/INDEX.md",
                         lambda t: t.replace("<!-- lists: */run.md -->",
                                             "<!-- lists: **/run.md -->"),
                         "is unbounded"),
    # `*.md` on the runs door must not reach a run folder one level down.
    "glob-does-not-cross-directories": ("workspace/90_runs/INDEX.md",
                                        lambda t: t.replace("<!-- lists: */run.md -->",
                                                            "<!-- lists: *.md -->"),
                                        "not listed in"),
}


BAD = {
    "always-not-mature": ("workspace/70_seams/harness.md",
                          lambda t: t.replace("status: draft",
                                              "status: draft\nload: always"),
                          "load: always requires status: mature"),
    "wrong-chamber": ("workspace/70_seams/harness.md",
                      lambda t: t.replace("type: seam", "type: decision"),
                      "belongs in 40_knowledge/"),
    "bad-type": ("workspace/70_seams/harness.md",
                 lambda t: t.replace("type: seam", "type: nonsense"),
                 "type 'nonsense' not in"),
    "dead-ref": ("workspace/70_seams/harness.md",
                 lambda t: t.replace("ref: seams-index", "ref: no-such-id"),
                 "does not resolve"),
    "fat-reserved": ("workspace/70_seams/harness.md",
                     lambda t: t.replace("status: draft", "status: reserved")
                     + "\nSecond line of body.\nThird line.\n",
                     "reserved scaffolding is one line max"),
    "no-id": ("workspace/70_seams/harness.md",
              lambda t: t.replace("id: seam-harness\n", ""),
              "missing required field 'id'"),
    "no-frontmatter": ("workspace/70_seams/harness.md",
                       lambda t: "# Harness\n",
                       "missing or unterminated OKF frontmatter"),
    "unflagged-token": ("workspace/70_seams/harness.md",
                        lambda t: t + "\nOwned by <<PRINCIPAL_NAME>>.\n",
                        "does not declare 'tokens: true'"),
    "unregistered-token": ("workspace/70_seams/harness.md",
                           lambda t: t.replace("status: draft",
                                               "status: draft\ntokens: true")
                           + "\nOwned by <<NOPE>>.\n",
                           "has no row in workspace/00_meta/placeholders.md"),
    "no-provenance": ("library/inbox/2026-08-24-a-capture.md",
                      lambda t: t.replace("provenance: authored\n", ""),
                      "missing required field 'provenance' for type 'knowledge'"),
    "mature-agent-proposed": ("library/inbox/2026-08-24-a-capture.md",
                              lambda t: t.replace("status: draft", "status: mature")
                              .replace("provenance: authored",
                                       "provenance: agent_proposed"),
                              "provenance: agent_proposed cannot be mature"),
    "topic-outside-library-tree": ("library/INDEX.md",
                                   lambda t: t.replace("type: doctrine",
                                                       "type: topic"),
                                   "belongs under library/fields/"),
    "fat-entrance": ("workspace/AGENTS.md",
                     lambda t: t + "\nPadding.\n" + "x" * 7000,
                     "static boot"),
    "no-use-when": ("workspace/70_seams/harness.md",
                    lambda t: t.replace("Use when wiring hooks",
                                        "For wiring hooks"),
                    "description must match"),
    "undeclared-field": ("workspace/70_seams/harness.md",
                         lambda t: t.replace("status: draft",
                                             "status: draft\nzzkey: x"),
                         "undeclared"),
    "bad-field-kind": ("workspace/70_seams/harness.md",
                       lambda t: t.replace("status: draft",
                                           "status: draft\nverified_on: soon"),
                       "not YYYY-MM-DD"),
    "required-field-missing": ("workspace/70_seams/INDEX.md",
                               lambda t: t.replace("    for: seam",
                                                   "    for: seam\n"
                                                   "    required: true"),
                               "missing required field 'verified_on'"),
    "mature-seam-unverified": ("workspace/70_seams/harness.md",
                               lambda t: t.replace("status: draft",
                                                   "status: mature"),
                               "requires verified_on"),
    "okf-mismatch": ("workspace/70_seams/harness.md",
                     lambda t: t.replace("status: draft",
                                         "status: draft\nokf: \"0.1\""),
                     "does not match the enforced contract"),
    "fat-prose": ("workspace/70_seams/harness.md",
                  lambda t: t + "\nPadding line.\n" * 160,
                  "split behind an INDEX"),
}

BOUNDARIES = "workspace/80_governance/boundaries.md"
SCRUB_TREE = {
    BOUNDARIES: """---
id: governance-boundaries
type: policy
status: draft
description: >
  The confidentiality floor. Use before anything leaves. Not for
  permission to act (see autonomy.md).
updated: 2026-08-24
---

# Boundaries

## Tier 1 — never leaves the machine

- *(none yet — add backticked terms here)*

## Tier 2 — never leaves the family

- `family-thing`
""",
}


def build(tmp, files):
    for rel, text in files.items():
        path = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    os.makedirs(os.path.join(tmp, "tools"), exist_ok=True)
    for tool in ("build_catalog.py", "check_loop.py", "scrub_check.py",
                 "agnostic_check.py", "workspace_layout.py", "check_staged.py", "journal_guard.py", "pipeline.py"):
        shutil.copy(os.path.join(TOOLS, tool), os.path.join(tmp, "tools", tool))
    schema_dir = os.path.join(tmp, "doctrine")
    os.makedirs(schema_dir, exist_ok=True)
    shutil.copy(
        os.path.join(os.path.dirname(TOOLS), "doctrine", "schema.json"),
        os.path.join(schema_dir, "schema.json"),
    )


def run(tmp, tool, *args):
    env = os.environ.copy()
    for name in (
        "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX",
        "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    ):
        env.pop(name, None)
    proc = subprocess.run([sys.executable, os.path.join(tmp, "tools", tool), *args],
                          capture_output=True, text=True, env=env)
    return proc.returncode, proc.stdout + proc.stderr


def main():
    tmp = tempfile.mkdtemp()
    try:
        build(tmp, CLEAN)
        code, out = run(tmp, "build_catalog.py")
        assert code == 0, f"clean tree failed build_catalog:\n{out}"
        assert os.path.isfile(os.path.join(tmp, "CATALOG.md")), out
        assert os.path.isfile(os.path.join(tmp, "CATALOG.json")), out
        assert "70_seams/harness.md" in open(
            os.path.join(tmp, "CATALOG.md"), encoding="utf-8").read(), out

        code, out = run(tmp, "build_catalog.py", "--check")
        assert code == 0, f"--check should pass right after a build:\n{out}"

        code, out = run(tmp, "check_loop.py")
        assert code == 0, f"clean tree failed check_loop:\n{out}"

        code, out = run(tmp, "check_loop.py", "--graph")
        assert "  3  library/fields/design/interface-design/typography-layout/" \
               "specimens/transit-wayfinding/NOTE.md" in out, out

        code, out = run(tmp, "build_catalog.py", "--stale")
        assert code == 0, out
        assert "typography-layout/README.md" in out, \
            f"an overdue topic must be listed:\n{out}"
        assert "inbox" not in out, \
            f"library/inbox/ is promoted, not reviewed:\n{out}"

        with open(os.path.join(tmp, "CATALOG.md"), "a", encoding="utf-8") as fh:
            fh.write("hand edit\n")
        code, out = run(tmp, "build_catalog.py", "--check")
        assert code == 0 and "source is catalogable" in out, out

        assert run(tmp, "build_catalog.py", "--wat")[0] == 2
        assert run(tmp, "check_loop.py", "--wat")[0] == 2
        assert run(tmp, "build_catalog.py", "--help")[0] == 0
    finally:
        shutil.rmtree(tmp)

    tmp = tempfile.mkdtemp()
    try:
        files = dict(CLEAN, **JOURNAL_TREE)
        files["workspace/AGENTS.md"] = files["workspace/AGENTS.md"].replace(
            "[seams](70_seams/INDEX.md)",
            "[seams](70_seams/INDEX.md), [memory](30_memory/INDEX.md), "
            "[runs](90_runs/INDEX.md)")
        build(tmp, files)
        code, out = run(tmp, "build_catalog.py", "--check")
        assert code == 0, f"a shaped journal and a traced run must pass:\n{out}"
        code, out = run(tmp, "check_loop.py")
        assert code == 0, f"pattern-covered journal and run must pass:\n{out}"

        # A sentinel beside a written journal means onboarding came back.
        sentinel = os.path.join(tmp, "workspace/00_meta/.uninitialised")
        open(sentinel, "w", encoding="utf-8").close()
        code, out = run(tmp, "build_catalog.py")
        assert code == 1 and "sentinel is back" in out, out
        os.remove(sentinel)

        # The name is half the contract: no time, no entry.
        os.rename(os.path.join(tmp, ENTRY),
                  os.path.join(tmp, "workspace/30_memory/journal/no-time.md"))
        code, out = run(tmp, "build_catalog.py")
        assert code == 1 and "YYYY-MM-DD-HHMM-slug.md" in out, out
    finally:
        shutil.rmtree(tmp)

    for name, (target, mutate, expect) in {**BAD_JOURNAL, **BAD_GLOB}.items():
        tmp = tempfile.mkdtemp()
        try:
            files = dict(CLEAN, **JOURNAL_TREE)
            files["workspace/AGENTS.md"] = files["workspace/AGENTS.md"].replace(
                "[seams](70_seams/INDEX.md)",
                "[seams](70_seams/INDEX.md), [memory](30_memory/INDEX.md), "
                "[runs](90_runs/INDEX.md)")
            files[target] = mutate(files[target])
            build(tmp, files)
            gate = "check_loop.py" if name in BAD_GLOB else "build_catalog.py"
            code, out = run(tmp, gate)
            assert code == 1, f"[{name}] expected exit 1, got {code}:\n{out}"
            assert expect in out, f"[{name}] expected {expect!r} in:\n{out}"
        finally:
            shutil.rmtree(tmp)

    for name, (target, mutate, expect) in BAD.items():
        tmp = tempfile.mkdtemp()
        try:
            files = dict(CLEAN)
            files[target] = mutate(files[target])
            build(tmp, files)
            code, out = run(tmp, "build_catalog.py")
            assert code == 1, f"[{name}] expected exit 1, got {code}:\n{out}"
            assert expect in out, f"[{name}] expected {expect!r} in:\n{out}"
            assert not os.path.isfile(os.path.join(tmp, "CATALOG.md")), \
                f"[{name}] catalog written despite errors"
        finally:
            shutil.rmtree(tmp)

    tmp = tempfile.mkdtemp()
    try:
        files = dict(CLEAN)
        files["workspace/70_seams/harness.md"] = files[
            "workspace/70_seams/harness.md"].replace(
            "status: draft", "status: mature\nverified_on: 2026-08-24")
        build(tmp, files)
        code, out = run(tmp, "build_catalog.py")
        assert code == 0, f"a verified mature seam must pass:\n{out}"
    finally:
        shutil.rmtree(tmp)

    tmp = tempfile.mkdtemp()
    try:
        files = dict(CLEAN)
        files["workspace/70_seams/mcp.md"] = files[
            "workspace/70_seams/harness.md"].replace(
            "seam-harness", "seam-mcp").replace("# Harness", "# MCP")
        build(tmp, files)
        code, out = run(tmp, "build_catalog.py")
        assert code == 0, out
        assert "70_seams/mcp.md" in open(
            os.path.join(tmp, "CATALOG.md"), encoding="utf-8").read(), out
        code, out = run(tmp, "check_loop.py")
        assert code == 1, f"a catalogued orphan must still fail:\n{out}"
        assert "orphan" in out and "mcp.md" in out, out
        assert "not listed in" in out, f"INDEX omission is an error:\n{out}"

        idx = os.path.join(tmp, "workspace/70_seams/INDEX.md")
        with open(idx, "a", encoding="utf-8") as fh:
            fh.write("- [mcp](mcp.md)\n")
        run(tmp, "build_catalog.py")
        code, out = run(tmp, "check_loop.py")
        assert code == 0, f"linked from its INDEX, it should pass:\n{out}"

        os.remove(os.path.join(tmp, "CATALOG.md"))
        code, out = run(tmp, "check_loop.py")
        assert code == 0, out
    finally:
        shutil.rmtree(tmp)

    tmp = tempfile.mkdtemp()
    try:
        files = dict(CLEAN)
        files["workspace/90_runs/INDEX.md"] = """---
id: runs-index
type: register
status: draft
description: >
  The session record. Use when opening or closing a run. Not for intent
  (see 20_intent).
updated: 2026-08-24
---

# Runs

One folder per run; each holds `run.md`.

<!-- lists: */run.md -->
"""
        files["workspace/90_runs/2026-08-24-1400-probe/run.md"] = """---
id: run-probe
type: run
status: draft
description: >
  A run record. Use when reconstructing this session. Not for doctrine
  (see workspace/AGENTS.md).
updated: 2026-08-24
---

# Run
"""
        files["workspace/AGENTS.md"] = files["workspace/AGENTS.md"].replace(
            "[seams](70_seams/INDEX.md)",
            "[seams](70_seams/INDEX.md), [runs](90_runs/INDEX.md)")
        build(tmp, files)
        run(tmp, "build_catalog.py")
        code, out = run(tmp, "check_loop.py")
        assert code == 0, f"a pattern-covered run record must pass:\n{out}"

        idx = os.path.join(tmp, "workspace/90_runs/INDEX.md")
        text = open(idx, encoding="utf-8").read().replace("<!-- lists: */run.md -->", "")
        open(idx, "w", encoding="utf-8").write(text)
        run(tmp, "build_catalog.py")
        code, out = run(tmp, "check_loop.py")
        assert code == 1 and "run.md" in out, out
    finally:
        shutil.rmtree(tmp)

    tmp = tempfile.mkdtemp()
    try:
        build(tmp, dict(CLEAN, **SCRUB_TREE))
        open(os.path.join(tmp, ".gitignore"), "w", encoding="utf-8").write(
            ".workspace-private/\n"
        )
        sentinel = os.path.join(tmp, "workspace/00_meta/.uninitialised")
        os.makedirs(os.path.dirname(sentinel), exist_ok=True)
        open(sentinel, "w", encoding="utf-8").close()
        code, out = run(tmp, "scrub_check.py")
        assert code == 0, f"a clean template needs no real terms:\n{out}"

        os.remove(sentinel)
        code, out = run(tmp, "scrub_check.py")
        assert code == 1 and "missing ignored" in out, \
            f"an instance with no private list must fail closed:\n{out}"

        terms = os.path.join(tmp, ".workspace-private/never-share.txt")
        os.makedirs(os.path.dirname(terms), exist_ok=True)
        open(terms, "w", encoding="utf-8").write("zz-leak-token\n")
        code, out = run(tmp, "scrub_check.py")
        assert code == 0, f"declared but unused term is clean:\n{out}"
        with open(os.path.join(tmp, "workspace/70_seams/harness.md"), "a",
                  encoding="utf-8") as fh:
            fh.write("\nRuns as zz-leak-token.\n")
        code, out = run(tmp, "scrub_check.py")
        assert code == 1 and "never-share term" in out, out
        assert "zz-leak-token" not in out, out

        open(terms, "w", encoding="utf-8").write("—\n")
        code, out = run(tmp, "scrub_check.py")
        assert code == 1 and "unusable" in out and "—" not in out, out
    finally:
        shutil.rmtree(tmp)

    tmp = tempfile.mkdtemp()
    try:
        files = dict(CLEAN)
        files["workspace/70_seams/INDEX.md"] += \
            "\nScratch dir: `/private/tmp/claude-501/scratch`.\n"
        build(tmp, files)
        code, out = run(tmp, "agnostic_check.py", "--root", tmp)
        assert code == 0, f"a path containing a vendor term must pass:\n{out}"
        with open(os.path.join(tmp, "workspace/70_seams/INDEX.md"), "a",
                  encoding="utf-8") as fh:
            # split so this test file itself stays clean under the gate
            fh.write("\nWorks best in " + "cla" "ude.\n")
        code, out = run(tmp, "agnostic_check.py", "--root", tmp)
        assert code == 1 and "vendor agent name" in out, \
            f"prose vendor lock-in must still fail:\n{out}"
    finally:
        shutil.rmtree(tmp)

    tmp = tempfile.mkdtemp()
    try:
        files = dict(CLEAN)
        files["workspace/70_seams/INDEX.md"] += "\n- [gone](nowhere.md)\n"
        build(tmp, files)
        run(tmp, "build_catalog.py")
        code, out = run(tmp, "check_loop.py")
        assert code == 1, out
        assert "dead link -> nowhere.md" in out, out
        assert ":11:" in out or "INDEX.md:" in out, f"no path:line in:\n{out}"
    finally:
        shutil.rmtree(tmp)

    print("test_gates: all checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
