#!/usr/bin/env python3
"""Pipeline contracts and reconstructed run state. Stdlib; temp trees only."""

import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

from test_instance import clone_source, run


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


def main():
    checks = 0
    with tempfile.TemporaryDirectory(prefix="workspace-pipeline-") as home:
        base = Path(home, "base")
        fixture(base)
        require_pass(base, "check")
        checks += 1

        defects = (
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

        symlinked = Path(home, "symlinked-stage")
        shutil.copytree(base, symlinked)
        outside = write(home, "outside-stage.md", contract(STAGES[0], "OUTSIDE-MARKER"))
        linked = symlinked / PIPELINES / SLUG / STAGES[0] / "STAGE.md"
        linked.unlink()
        linked.symlink_to(outside)
        diagnostic = require_failure(symlinked, "check", contains=("symlink",))
        assert "OUTSIDE-MARKER" not in diagnostic, \
            "validation read external symlink bytes before rejecting the path"
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
        shutil.copytree(base / "workspace", extracted)
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
