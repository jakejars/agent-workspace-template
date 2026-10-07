#!/usr/bin/env python3
"""Pipeline contracts and reconstructed run state. Stdlib; temp trees only."""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from test_gates import CLEAN, build
from test_instance import clone_source, git, run


TODAY = "2026-10-07"
SLUG = "pipeline-probe"
RUN_ID = f"{TODAY}-{SLUG}"
PIPELINES = "workspace/60_capabilities/pipelines"
STAGES = ("01_prepare", "02_review")


def write(root, rel, text):
    target = Path(root, rel)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


def contract(stage, executor="model", checkpoint=False):
    command = '\ncommand: python3 -c "print(1)"' if executor == "script" else ""
    return f"""---
id: stage-{SLUG}-{stage.replace('_', '-')}
type: stage
status: draft
description: Prepare material. Use when running this stage. Not for the complete process (see ../PIPELINE.md).
scope: workspace
owner: agent
executor: {executor}{command}
checkpoint: {str(checkpoint).lower()}
output: artifacts/result.txt
updated: {TODAY}
---

# {stage}

## Purpose

Produce inspectable material for the next stage.

## Inputs

### Reference

Standing constraints in workspace/80_governance/autonomy.md.

### Working

The current task material, or the preceding stage's output.

## Process

Use the declared executor, read only these inputs, and write the output.
"""


def fixture(root, checkpoint=False):
    """A real source tree and a two-stage definition, with an active intent."""
    clone_source(str(root), require_template=False)
    write(root, f"{PIPELINES}/{SLUG}/PIPELINE.md", f"""---
id: pipeline-{SLUG}
type: pipeline
status: draft
description: Two-stage probe. Use when checking a staged process. Not for ordinary work (see workspace/20_intent/INDEX.md).
scope: workspace
owner: agent
version: 1
updated: {TODAY}
---

# Pipeline probe

- [Prepare](01_prepare/STAGE.md)
- [Review](02_review/STAGE.md)
""")
    write(root, f"{PIPELINES}/{SLUG}/README.md", f"""---
id: pipeline-{SLUG}-door
type: doctrine
status: draft
description: Probe map. Use when finding a stage. Not for execution (see PIPELINE.md).
updated: {TODAY}
---

# Probe map

[Definition](PIPELINE.md)

<!-- lists: */STAGE.md -->
""")
    for stage in STAGES:
        write(root, f"{PIPELINES}/{SLUG}/{stage}/STAGE.md",
              contract(stage, "script" if stage == STAGES[0] else "model",
                       checkpoint if stage == STAGES[0] else False))
    write(root, "workspace/20_intent/active/pipeline-probe.md", f"""---
id: intent-pipeline-probe
type: intent
status: draft
lifecycle: clarified
description: Pipeline probe objective. Use when testing execution. Not for doctrine (see workspace/20_intent/INDEX.md).
scope: workspace
owner: agent
updated: {TODAY}
---

# Pipeline probe

## Checkpoint

Ready to start the two-stage probe.
""")


def require_pass(root, *args):
    code, out = run(str(root), "pipeline.py", *args)
    assert code == 0, f"pipeline {' '.join(args)} returned {code}:\n{out}"
    return out


def require_failure(root, *args, contains=()):
    code, out = run(str(root), "pipeline.py", *args)
    assert code != 0, f"pipeline {' '.join(args)} accepted a planted violation:\n{out}"
    for word in contains:
        assert word.lower() in out.lower(), f"expected {word!r} in:\n{out}"
    assert "Traceback" not in out, f"expected a diagnostic, got an exception:\n{out}"
    return out


def start(root, run_id=RUN_ID):
    return require_pass(root, "start", "--pipeline", SLUG, "--run", run_id,
                        "--intent", "intent-pipeline-probe")


def snapshot(root):
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in Path(root).rglob("*") if path.is_file()
            and "__pycache__" not in path.parts}


def test_recorded_checkpoint_matches_definition(home, base):
    tree = Path(home, "altered-checkpoint")
    shutil.copytree(base, tree)
    write(tree, f"{PIPELINES}/{SLUG}/01_prepare/STAGE.md",
          contract(STAGES[0], "script", True))
    start(tree)
    folder = tree / "workspace/90_runs" / RUN_ID
    (folder / STAGES[0] / "artifacts/result.txt").write_text("Needs review.\n")
    state = require_pass(tree, "status", "--run", RUN_ID)
    assert "Next: human checkpoint for 01_prepare" in state, state
    record = folder / "run.md"
    record.write_text(record.read_text().replace("    checkpoint: true",
                                                "    checkpoint: false", 1))
    state = require_failure(tree, "status", "--run", RUN_ID,
                            contains=("recorded", "stage plan", "definition"))
    assert "Next: 02_review" not in state, state
    return 1


def test_recorded_version_matches_definition(home, base):
    tree = Path(home, "altered-version")
    shutil.copytree(base, tree)
    start(tree)
    record = tree / "workspace/90_runs" / RUN_ID / "run.md"
    record.write_text(record.read_text().replace("pipeline_version: 1",
                                                "pipeline_version: 2", 1))
    state = require_failure(tree, "status", "--run", RUN_ID,
                            contains=("recorded", "version", "definition"))
    assert "Next: 01_prepare" not in state, state
    return 1


def test_recorded_stage_plan_matches_definition(home, base):
    mutations = (
        ("output", "    output: artifacts/result.txt", "    output: artifacts/other.txt"),
        ("name", "  - stage: 01_prepare", "  - stage: 01_other"),
        ("missing", "  - stage: 02_review\n    output: artifacts/result.txt\n"
         "    checkpoint: false\n", ""),
        ("extra-field", "  - stage: 01_prepare", "  - stage: 01_prepare\n    extra: yes"),
    )
    for name, before, after in mutations:
        tree = Path(home, "altered-plan-" + name)
        shutil.copytree(base, tree)
        start(tree)
        record = tree / "workspace/90_runs" / RUN_ID / "run.md"
        record.write_text(record.read_text().replace(before, after, 1))
        state = require_failure(tree, "status", "--run", RUN_ID,
                                contains=("recorded", "stage plan", "definition"))
        assert "Next: 01_" not in state, state
    return len(mutations)


def test_unverified_definition_requires_restoration(home, base):
    for name in ("changed", "missing"):
        tree = Path(home, "definition-" + name)
        shutil.copytree(base, tree)
        start(tree)
        definition = tree / PIPELINES / SLUG / "PIPELINE.md"
        if name == "changed":
            definition.write_text(definition.read_text() + "\nChanged contract.\n")
        else:
            definition.unlink()
        before = snapshot(tree)
        state = require_failure(tree, "status", "--run", RUN_ID,
                                contains=("definition", "restore"))
        assert "Next: restore" in state, state
        assert "Next: 01_prepare" not in state and "Next: 02_review" not in state, state
        assert before == snapshot(tree), "failed definition verification changed source"
    return 2


def test_evaluation_requires_numeric_revision_limit(home, base):
    tree = Path(home, "unlimited-revision")
    shutil.copytree(base, tree)
    path = tree / PIPELINES / SLUG / STAGES[1] / "STAGE.md"
    text = contract(STAGES[1]) + ("\n## Evaluation\n\n### Evaluator\n\n"
        "Check acceptance criterion 1.\n\n### Revise\n\nFix the failed criterion.\n\n"
        "### Stop\n\nKeep revising until acceptance criterion 1 passes, "
        "with no revision limit.\n")
    path.write_text(text)
    require_failure(tree, "check", contains=("revision_limit", "positive integer"))
    # The bound is structured metadata; Stop prose need not carry a numeral.
    bounded = text.replace("executor: model", "executor: model\nrevision_limit: 2")
    bounded = bounded.replace("Keep revising until acceptance criterion 1 passes, "
                              "with no revision limit.",
                              "Stop when the criterion passes or revision_limit is reached.")
    path.write_text(bounded)
    require_pass(tree, "check")
    for value in ("0", "-1", "unlimited", "[2]"):
        path.write_text(bounded.replace("revision_limit: 2", "revision_limit: " + value))
        require_failure(tree, "check", contains=("revision_limit",))
    return 6


def test_ordinary_contained_symlink_passes_pipeline_context_and_staged(home, base):
    tree = Path(home, "ordinary-symlink")
    build(str(tree), CLEAN)
    shutil.copy2(Path(__file__).parent / "context.py", tree / "tools/context.py")
    (tree / "workspace/00_meta/.uninitialised").touch()
    write(tree, ".gitignore", ".workspace-private/\n.workspace-cache/\n")
    assert not list((tree / PIPELINES).glob("*/PIPELINE.md")), \
        "this regression requires zero pipeline definitions"
    linked = tree / "workspace/70_seams/SHARED.md"
    target = tree / "tools/ordinary-shared.txt"
    linked.rename(target)
    linked.symlink_to("../../tools/ordinary-shared.txt")
    for tool, args in (("scrub_check.py", ()), ("build_catalog.py", ("--check",)),
                       ("check_loop.py", ())):
        code, out = run(str(tree), tool, *args)
        assert code == 0, f"{tool} rejected contained ordinary symlink:\n{out}"
    require_pass(tree, "check")
    code, out = run(str(tree), "context.py", "refresh", "--force")
    assert code == 0, f"context rejected contained ordinary symlink:\n{out}"
    git(str(tree), "init", "-q")
    git(str(tree), "add", "-A")
    code, out = run(str(tree), "check_staged.py")
    assert code == 0, f"staged gates rejected contained ordinary symlink:\n{out}"
    # Containment still applies outside the pipeline shelf, before source reads.
    outside = write(home, "outside-ordinary.md", "OUTSIDE-ORDINARY-MARKER\n")
    linked.unlink()
    linked.symlink_to(outside)
    diagnostic = require_failure(tree, "check")
    assert "OUTSIDE-ORDINARY-MARKER" not in diagnostic, \
        "pipeline validation read external content before refusing an escape"
    return 5


def test_partial_journal_write_rolls_back_new_trace_and_run(home, base):
    tree = Path(home, "partial-journal")
    shutil.copytree(base, tree)
    write(tree, "workspace/00_meta/.initializing",
          json.dumps({"version": 1, "state": "filled", "workspace_id": SLUG,
                      "started_on": TODAY}) + "\n")
    # clone_source omits ignored values; inherited journals may still name them.
    write(tree, "workspace/00_meta/values.json", "{}\n")
    start(tree)
    code, out = run(str(tree), "build_catalog.py", "--check")
    assert code == 0, f"journal rollback baseline failed catalog:\n{out}"
    before = snapshot(tree)
    interrupted = RUN_ID + "-interrupted"
    script = """from pathlib import Path
from unittest.mock import patch
import pipeline

open_file = Path.open
class InterruptedTrace:
    def __init__(self, handle):
        self.handle = handle
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.handle.close()
    def write(self, text):
        self.handle.write(text[:8])
        self.handle.flush()
        raise OSError('injected failure after eight journal bytes')

def fail_trace(path, mode='r', *args, **kwargs):
    handle = open_file(path, mode, *args, **kwargs)
    if mode == 'x' and path.parent.name == 'journal':
        return InterruptedTrace(handle)
    return handle

with patch.object(Path, 'open', fail_trace):
    raise SystemExit(pipeline.main(['start', '--pipeline', %r, '--run', %r,
                                  '--intent', 'intent-pipeline-probe']))
""" % (SLUG, interrupted)
    result = subprocess.run([sys.executable, "-c", script], cwd=tree / "tools",
                            capture_output=True, text=True)
    out = result.stdout + result.stderr
    assert result.returncode == 1 and "injected failure" in out, out
    assert before == snapshot(tree), \
        "failed start retained a partial trace or changed pre-existing history"
    start(tree, interrupted)
    code, out = run(str(tree), "build_catalog.py", "--check")
    assert code == 0, f"retry after interrupted journal write failed catalog:\n{out}"
    return 2


def test_journal_creation_race_preserves_preexisting_trace(home, base):
    tree = Path(home, "existing-journal-race")
    shutil.copytree(base, tree)
    script = """from pathlib import Path
from unittest.mock import patch
import pipeline

open_file = Path.open
def race_trace(path, mode='r', *args, **kwargs):
    if mode == 'x' and path.parent.name == 'journal':
        with open_file(path, 'w', encoding='utf-8') as handle:
            handle.write('Pre-existing history from another writer.\\n')
    return open_file(path, mode, *args, **kwargs)

with patch.object(Path, 'open', race_trace):
    raise SystemExit(pipeline.main(['start', '--pipeline', %r, '--run', %r,
                                  '--intent', 'intent-pipeline-probe']))
""" % (SLUG, RUN_ID)
    result = subprocess.run([sys.executable, "-c", script], cwd=tree / "tools",
                            capture_output=True, text=True)
    assert result.returncode == 1, result.stdout + result.stderr
    assert not (tree / "workspace/90_runs" / RUN_ID).exists(), "run was not rolled back"
    trace_slug = "pipeline-" + hashlib.sha256(RUN_ID.encode()).hexdigest()[:12]
    traces = list((tree / "workspace/30_memory/journal").glob(f"*-{trace_slug}.md"))
    assert len(traces) == 1 and traces[0].read_text() == \
        "Pre-existing history from another writer.\n", \
        "rollback removed or changed a trace it did not create"
    return 1


def test_pipeline_symlink_sources_are_refused_before_reading(home, base):
    for location in ("contained", "outside"):
        tree = Path(home, "symlinked-stage-" + location)
        shutil.copytree(base, tree)
        target_root = tree if location == "contained" else Path(home)
        target = write(target_root, "tools/symlinked-stage.txt",
                       contract(STAGES[0], "SYMLINKED-STAGE-MARKER"))
        linked = tree / PIPELINES / SLUG / STAGES[0] / "STAGE.md"
        linked.unlink()
        linked.symlink_to(target)
        diagnostic = require_failure(tree, "check", contains=("symlink",))
        assert "SYMLINKED-STAGE-MARKER" not in diagnostic, \
            "validation read symlink bytes before rejecting a pipeline source"
    return 2


def test_final_stage_entries_must_be_directories(home, base):
    for replacement in ("dangling-symlink", "regular-file", "directory-symlink"):
        for operation in ("check", "start"):
            tree = Path(home, "final-stage-" + replacement + "-" + operation)
            shutil.copytree(base, tree)
            stage = tree / PIPELINES / SLUG / STAGES[-1]
            if replacement == "directory-symlink":
                target = tree / "tools/final-stage-target"
                stage.rename(target)
                stage.symlink_to(target, target_is_directory=True)
            else:
                shutil.rmtree(stage)
                if replacement == "regular-file":
                    stage.write_text("A stage must be a directory.\n", encoding="utf-8")
                else:
                    stage.symlink_to("missing-stage", target_is_directory=True)
            before = snapshot(tree)
            args = ("check",) if operation == "check" else (
                "start", "--pipeline", SLUG, "--run", RUN_ID,
                "--intent", "intent-pipeline-probe")
            diagnostic = "directory" if replacement == "regular-file" else "symlink"
            require_failure(tree, *args, contains=(STAGES[-1], diagnostic))
            assert before == snapshot(tree), "refused stage substitution changed source"
            assert not (tree / "workspace/90_runs" / RUN_ID).exists(), \
                "refused stage substitution created a run"
    return 6


def main():
    checks = 0
    with tempfile.TemporaryDirectory(prefix="workspace-pipeline-") as home:
        base = Path(home, "base")
        fixture(base)
        require_pass(base, "check")
        checks += 1

        for regression in (test_recorded_checkpoint_matches_definition,
                           test_recorded_version_matches_definition,
                           test_recorded_stage_plan_matches_definition,
                           test_unverified_definition_requires_restoration,
                           test_evaluation_requires_numeric_revision_limit,
                           test_ordinary_contained_symlink_passes_pipeline_context_and_staged,
                           test_partial_journal_write_rolls_back_new_trace_and_run,
                           test_journal_creation_race_preserves_preexisting_trace,
                           test_pipeline_symlink_sources_are_refused_before_reading,
                           test_final_stage_entries_must_be_directories):
            checks += regression(home, base)

        with_skill = Path(home, "with-skill")
        shutil.copytree(base, with_skill)
        # Only the named directory is required; skill validity/trust is a separate gate.
        (with_skill / "workspace/60_capabilities/skills/model-probe").mkdir()
        write(with_skill, f"{PIPELINES}/{SLUG}/02_review/STAGE.md",
              contract(STAGES[1]).replace("executor: model\n",
                                         "executor: model\nskill: model-probe\n"))
        require_pass(with_skill, "check")
        checks += 1

        defects = (
            ("missing-skill", lambda root: write(root,
             f"{PIPELINES}/{SLUG}/02_review/STAGE.md",
             contract(STAGES[1]).replace("executor: model\n",
                                        "executor: model\nskill: missing-probe\n")),
             ("skill", "missing-probe")),
            ("skill-outside-chamber", lambda root: write(root,
             f"{PIPELINES}/{SLUG}/02_review/STAGE.md",
             contract(STAGES[1]).replace("executor: model\n",
                                        "executor: model\nskill: ../pipelines\n")),
             ("skill",)),
            ("numbering-gap", lambda root: Path(root,
             f"{PIPELINES}/{SLUG}/02_review").rename(Path(root,
             f"{PIPELINES}/{SLUG}/03_review")), ("contiguous",)),
            ("missing-executor", lambda root: write(root,
             f"{PIPELINES}/{SLUG}/01_prepare/STAGE.md",
             contract(STAGES[0]).replace("executor: model\n", "")), ("executor",)),
            ("script-without-command", lambda root: write(root,
             f"{PIPELINES}/{SLUG}/01_prepare/STAGE.md",
             contract(STAGES[0]).replace("executor: model", "executor: script")),
             ("command",)),
            ("invalid-executor", lambda root: write(root,
             f"{PIPELINES}/{SLUG}/01_prepare/STAGE.md",
             contract(STAGES[0]).replace("executor: model", "executor: magic")),
             ("executor",)),
            ("list-executor", lambda root: write(root,
             f"{PIPELINES}/{SLUG}/01_prepare/STAGE.md",
             contract(STAGES[0]).replace("executor: model", "executor: [model]")),
             ("executor",)),
            ("list-command", lambda root: write(root,
             f"{PIPELINES}/{SLUG}/01_prepare/STAGE.md",
             contract(STAGES[0], "script").replace(
                 'command: python3 -c "print(1)"', "command: [python3]")),
             ("command",)),
            ("oversize-contract", lambda root: write(root,
             f"{PIPELINES}/{SLUG}/01_prepare/STAGE.md",
             contract(STAGES[0]) + "\n" + "x" * 3000), ("3000",)),
            ("invalid-frontmatter", lambda root: write(root,
             f"{PIPELINES}/{SLUG}/01_prepare/STAGE.md",
             contract(STAGES[0]).replace(f"updated: {TODAY}", "updated: yesterday")),
             ("updated",)),
            ("missing-working-inputs", lambda root: write(root,
             f"{PIPELINES}/{SLUG}/01_prepare/STAGE.md",
             contract(STAGES[0]).replace("### Working", "### Other")), ("Working",)),
            ("fenced-inputs", lambda root: write(root,
             f"{PIPELINES}/{SLUG}/01_prepare/STAGE.md",
             contract(STAGES[0]).replace("### Reference", "## Reference")
             .replace("### Working", "## Working")
             + "\n```markdown\n## Inputs\n### Reference\nStanding rules.\n"
               "### Working\nRun material.\n```\n"), ("Inputs",)),
            ("misfiled-pipeline", lambda root: write(root,
             "workspace/60_capabilities/stray.md",
             Path(root, f"{PIPELINES}/{SLUG}/PIPELINE.md").read_text(encoding="utf-8")
             .replace(f"id: pipeline-{SLUG}", "id: stray-pipeline")), ("pipeline",)),
        )
        for name, mutate, words in defects:
            tree = Path(home, name)
            shutil.copytree(base, tree)
            mutate(tree)
            require_failure(tree, "check", contains=words)
            checks += 1

        tree = Path(home, "ordinary-run")
        shutil.copytree(base, tree)
        start(tree)
        folder = tree / "workspace/90_runs" / RUN_ID
        assert (folder / "run.md").is_file(), "start must create an ordinary run"
        for stage in STAGES:
            assert (folder / stage / "artifacts").is_dir(), stage
        metadata = (folder / "run.md").read_text(encoding="utf-8")
        assert "pipeline_version: 1" in metadata, metadata
        assert "pipeline_digest:" in metadata, metadata
        traces = [path for path in (tree / "workspace/30_memory/journal").glob("*.md")
                  if f"90_runs/{RUN_ID}/run.md" in path.read_text(encoding="utf-8")]
        assert len(traces) == 1, "start must append exactly one journal trace"
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}-\d{4}-[a-z0-9]+"
                            r"(?:-[a-z0-9]+){0,4}\.md", traces[0].name), \
            f"start minted an invalid journal name: {traces[0].name}"
        state = require_pass(tree, "status", "--run", RUN_ID)
        assert "Next: 01_prepare" in state, state
        (folder / STAGES[0] / "artifacts/result.txt").write_text("Prepared.\n")
        before = snapshot(tree)
        state = require_pass(tree, "status", "--run", RUN_ID)
        assert "Next: 02_review" in state, state
        assert before == snapshot(tree), "status changed source files"
        checks += 1
        require_failure(tree, "start", "--pipeline", SLUG, "--run", RUN_ID,
                        "--intent", "intent-pipeline-probe", contains=("overwrite",))
        assert before == snapshot(tree), "refused start changed an existing run"
        checks += 1

        for args in (("start", "--pipeline", "../outside", "--run", RUN_ID),
                     ("start", "--pipeline", SLUG, "--run", "../outside"),
                     ("status", "--run", "../outside")):
            require_failure(tree, *args)
            assert before == snapshot(tree), "unsafe identifier changed source"
            checks += 1

        pending = Path(home, "checkpoint")
        shutil.copytree(base, pending)
        write(pending, f"{PIPELINES}/{SLUG}/01_prepare/STAGE.md",
              contract(STAGES[0], "script", True))
        start(pending)
        folder = pending / "workspace/90_runs" / RUN_ID
        output = folder / STAGES[0] / "artifacts/result.txt"
        output.write_text("Await human review.\n", encoding="utf-8")
        state = require_pass(pending, "status", "--run", RUN_ID)
        assert "checkpoint" in state.lower() and "01_prepare" in state, state
        assert "Next: human checkpoint for 01_prepare" in state, state
        write(pending, f"workspace/90_runs/{RUN_ID}/{STAGES[0]}/checkpoint.json",
              json.dumps({"approved": True,
                          "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                          "reviewed_by": "Jake", "reviewed_on": TODAY}) + "\n")
        state = require_pass(pending, "status", "--run", RUN_ID)
        assert "Next: 02_review" in state, state
        output.write_text("Human edits after approval.\n", encoding="utf-8")
        state = require_pass(pending, "status", "--run", RUN_ID)
        assert "Next: human checkpoint for 01_prepare" in state, state
        checks += 1

        extracted = Path(home, "extracted")
        shutil.copytree(with_skill / "workspace", extracted)
        for name in ("tools", "doctrine", "_templates"):
            shutil.copytree(base / name, extracted / name)
        for name in ("NAMESPACE.md", "LOOP.md", ".gitignore"):
            shutil.copy2(base / name, extracted / name)
        require_pass(extracted, "check")
        start(extracted)
        assert (extracted / "90_runs" / RUN_ID / "run.md").is_file()
        state = require_pass(extracted, "status", "--run", RUN_ID)
        assert "Next: 01_prepare" in state, state
        checks += 1

    print(f"test_pipeline: {checks} contract, run, checkpoint, and extracted-layout cases passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
