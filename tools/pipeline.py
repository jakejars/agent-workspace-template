#!/usr/bin/env python3
"""Check pipeline contracts, scaffold ordinary runs, and reconstruct run state.

  python3 tools/pipeline.py check
  python3 tools/pipeline.py start --pipeline SLUG --run YYYY-MM-DD-SLUG [--intent ID]
  python3 tools/pipeline.py status --run YYYY-MM-DD-SLUG

Stdlib only. Stages are never executed by this tool. Status is read-only;
checkpoint receipts record human review, never authorization for an effect.
Exit: 0 success, 1 invalid source/state, 2 usage or unrecognized root.
"""

import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

sys.dont_write_bytecode = True
import build_catalog as catalog
from workspace_layout import refuse_unknown

ROOT = Path(catalog.ROOT)
LAYOUT = catalog.LAYOUT
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
STAGE = re.compile(r"([0-9]{2})_(" + SLUG + r")\Z")
RUN = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2})-(" + SLUG + r")\Z")
OUTPUT = re.compile(r"artifacts/[A-Za-z0-9][A-Za-z0-9._-]*\Z")
PIPELINES = LAYOUT.workspace_path("workspace/60_capabilities/pipelines")
SKILLS = LAYOUT.workspace_path("workspace/60_capabilities/skills")
RUNS = LAYOUT.workspace_path("workspace/90_runs")


def safe_path(path, allow_symlinks=False):
    """Refuse escapes and unsupported symlinks before reading or creating evidence."""
    path = Path(path)
    rel = path.relative_to(ROOT)
    cursor = ROOT
    for part in rel.parts:
        cursor /= part
        if cursor.is_symlink() and not allow_symlinks:
            raise ValueError(f"{rel}: symlinks are not supported for pipeline files")
    path.resolve().relative_to(ROOT.resolve())
    return path


def read(path):
    return safe_path(path).read_text(encoding="utf-8")


def metadata(path, expected):
    fm = catalog.parse_frontmatter(read(path))
    if not fm or fm.get("type") != expected:
        raise ValueError(f"{path.relative_to(ROOT)}: requires {expected} frontmatter")
    return fm


def sections(text):
    """Named headings and their own prose, excluding fenced examples."""
    result, current = {}, None
    body = "\n".join(catalog.body_of(text))
    for line in catalog.strip_fences(body):
        heading = re.fullmatch(r"#{2,3}\s+(.+?)\s*", line)
        if heading:
            current = heading.group(1)
            if current in result:
                raise ValueError(f"duplicate heading '{current}'")
            result[current] = []
        elif current:
            result[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in result.items()}


def source_errors():
    """Reuse canonical metadata/ref validation; retain pipeline diagnostics only."""
    errors, warnings = [], []
    prefix = PIPELINES.relative_to(ROOT).as_posix() + "/"
    try:
        # Catalog may follow ordinary contained links, but pipeline sources may not.
        safe_path(PIPELINES)
        for rel in catalog.content_files():
            safe_path(ROOT / rel, allow_symlinks=not rel.startswith(prefix))
        records = catalog.scan(errors, warnings)
        catalog.validate(records, errors, warnings)
    except (TypeError, ValueError, KeyError) as exc:
        return [f"doctrine/schema.json: invalid metadata or schema ({exc})"]
    relevant = [error for error in errors
                if error.startswith((prefix, "doctrine/schema.json:"))]
    for record in records:
        ftype = record["fm"].get("type")
        if ftype not in {"pipeline", "stage"}:
            continue
        canonical = LAYOUT.canonical_rel(record["rel"])
        suffix = r"PIPELINE\.md" if ftype == "pipeline" else r"[0-9]{2}_" + SLUG + r"/STAGE\.md"
        if not re.fullmatch(r"workspace/60_capabilities/pipelines/" + SLUG + "/" + suffix, canonical):
            relevant.append(f"{record['rel']}: {ftype} must use its pipeline definition path")
    return relevant


def load_pipeline(slug):
    if not re.fullmatch(SLUG, slug):
        raise ValueError("pipeline must be a lowercase kebab-case slug")
    folder = safe_path(PIPELINES / slug)
    definition = folder / "PIPELINE.md"
    fm = metadata(definition, "pipeline")
    if not re.fullmatch(r"[1-9][0-9]*", str(fm.get("version", ""))):
        raise ValueError(f"{definition.relative_to(ROOT)}: version must be a positive integer")
    errors = [error for error in source_errors()
              if error.startswith((folder.relative_to(ROOT).as_posix() + "/",
                                   "doctrine/schema.json:"))]
    if errors:
        raise ValueError("\n".join(errors))
    stages = []
    digest = hashlib.sha256()
    digest.update(b"PIPELINE.md\0" + read(definition).encode("utf-8"))
    cap = catalog.SCHEMA["limits"]["stage_chars"]
    if cap > catalog.SCHEMA["limits"]["boot_dynamic_chars"]:
        raise ValueError("doctrine/schema.json: stage_chars exceeds the dynamic disclosure budget")
    for child in sorted(folder.iterdir()):
        safe_path(child)
        match = STAGE.fullmatch(child.name)
        if not child.is_dir():
            if match:
                raise ValueError(f"{child.relative_to(ROOT)}: stage must be a directory")
            continue
        if not match or int(match.group(1)) != len(stages) + 1:
            raise ValueError(f"{child.relative_to(ROOT)}: stage numbering must be contiguous from 01")
        contract = child / "STAGE.md"
        text = read(contract)
        stage = metadata(contract, "stage")
        if len(text) > cap:
            raise ValueError(f"{contract.relative_to(ROOT)}: stage contract exceeds {cap} chars")
        executor = stage.get("executor")
        if not isinstance(executor, str) or executor not in {"script", "model", "human"}:
            raise ValueError(f"{contract.relative_to(ROOT)}: executor must be script, model, or human")
        if executor == "script" and (not isinstance(stage.get("command"), str)
                                     or not stage["command"].strip()):
            raise ValueError(f"{contract.relative_to(ROOT)}: script executor requires a command")
        if "skill" in stage:
            skill = stage["skill"]
            if (not isinstance(skill, str) or not re.fullmatch(SLUG, skill)
                    or not safe_path(SKILLS / skill).is_dir()):
                raise ValueError(f"{contract.relative_to(ROOT)}: skill {skill!r} requires an existing skill directory")
        if not isinstance(stage.get("checkpoint"), str) or stage["checkpoint"] not in {"true", "false"}:
            raise ValueError(f"{contract.relative_to(ROOT)}: checkpoint must be true or false")
        if not OUTPUT.fullmatch(str(stage.get("output", ""))):
            raise ValueError(f"{contract.relative_to(ROOT)}: output must be artifacts/<filename>")
        parts = sections(text)
        required = catalog.TYPE_RULES["stage"]["headings"]
        for heading in required:
            if heading not in parts or (heading != "Inputs" and not parts[heading]):
                raise ValueError(f"{contract.relative_to(ROOT)}: missing or empty {heading} section")
        # Inputs has two named children; each must be nested below Inputs.
        clean_body = "\n".join(catalog.strip_fences("\n".join(catalog.body_of(text))))
        if not re.search(r"^## Inputs[^\S\n]*\n(?:(?!^## ).)*^### Reference[^\S\n]*\n"
                         r"(?:(?!^## ).)*^### Working[^\S\n]*$", clean_body, re.M | re.S):
            raise ValueError(f"{contract.relative_to(ROOT)}: Inputs requires Reference then Working subsections")
        if "Evaluation" in parts:
            for heading in ("Evaluator", "Revise", "Stop"):
                if not parts.get(heading):
                    raise ValueError(f"{contract.relative_to(ROOT)}: Evaluation requires {heading}")
            if not re.fullmatch(r"[1-9][0-9]*", str(stage.get("revision_limit", ""))):
                raise ValueError(f"{contract.relative_to(ROOT)}: Evaluation requires revision_limit as a positive integer")
        digest.update((child.name + "/STAGE.md\0").encode() + text.encode("utf-8"))
        stages.append({"stage": child.name, "output": stage["output"],
                       "checkpoint": stage["checkpoint"]})
    if not stages:
        raise ValueError(f"{definition.relative_to(ROOT)}: pipeline requires at least one stage")
    return fm, stages, digest.hexdigest()


def check_errors():
    if catalog.SCHEMA_ERROR:
        return [catalog.SCHEMA_ERROR], 0
    errors = source_errors()
    count = 0
    if PIPELINES.exists():
        try:
            safe_path(PIPELINES)
            for child in sorted(PIPELINES.iterdir()):
                if child.is_dir():
                    count += 1
                    try:
                        load_pipeline(child.name)
                    except (OSError, ValueError) as exc:
                        errors.append(str(exc))
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
    return list(dict.fromkeys(errors)), count


def run_path(run_id):
    match = RUN.fullmatch(run_id)
    if not match:
        raise ValueError("run must be YYYY-MM-DD-<kebab-case-slug>")
    datetime.date.fromisoformat(match.group(1))
    return safe_path(RUNS / run_id)


def select_intent(identifier):
    active = LAYOUT.workspace_path("workspace/20_intent/active")
    candidates = []
    for path in sorted(active.glob("*.md")):
        fm = catalog.parse_frontmatter(read(path)) or {}
        if (fm.get("type") == "intent" and fm.get("status") in {"draft", "mature"}
                and fm.get("lifecycle") not in {"satisfied", "abandoned", "superseded"}):
            if identifier is None or identifier in {fm.get("id"), path.stem,
                                                   LAYOUT.canonical_rel(path.relative_to(ROOT))}:
                candidates.append((path, fm))
    if len(candidates) != 1:
        raise ValueError("select exactly one active intent with --intent <id-or-slug>")
    return candidates[0]


def start(slug, run_id, intent):
    folder = run_path(run_id)
    if folder.exists():
        raise ValueError(f"{folder.relative_to(ROOT)}: existing run; never overwrite")
    fm, stages, digest = load_pipeline(slug)
    intent_path, intent_fm = select_intent(intent)
    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.date().isoformat()
    pipeline_ref = f"workspace/60_capabilities/pipelines/{slug}/PIPELINE.md"
    intent_ref = LAYOUT.canonical_rel(intent_path.relative_to(ROOT))
    plan = "\n".join(f"  - stage: {s['stage']}\n    output: {s['output']}\n"
                     f"    checkpoint: {s['checkpoint']}" for s in stages)
    evidence = "\n".join(f"- `{s['stage']}/{s['output']}` — pending" for s in stages)
    text = (f"---\nid: run-{run_id}\ntype: run\nstatus: draft\n"
            f"description: Pipeline {slug}. Use when tracing this execution. "
            "Not for the definition (see " + pipeline_ref + ").\n"
            f"scope: run:{run_id}\nload: drill\nowner: agent\nupdated: {today}\n"
            f"pipeline: {pipeline_ref}\npipeline_version: {fm['version']}\n"
            f"pipeline_digest: {digest}\npipeline_stages:\n{plan}\n"
            f"related:\n  - type: canonical\n    ref: {intent_ref}\n"
            f"  - type: depends_on\n    ref: {pipeline_ref}\n---\n\n"
            f"# Run {run_id}\n\n**Intent:** `{intent_fm['id']}` · **Started:** {today}\n"
            "**Outcome:** in progress\n\n## Context loaded\n\n"
            f"- Reference: `{pipeline_ref}` — definition and version recorded at start\n"
            "- Working: record each stage's actual inputs before executing it\n\n"
            "## Actions\n\n| time | action | class | effect |\n|---|---|---|---|\n"
            f"| {now:%H:%M} | start pipeline | A | scaffold stage output folders |\n\n"
            "## Approvals used\n\nNone at start; record authorization before consequential effects.\n\n"
            f"## Evidence\n\n{evidence}\n\n## Outcome\n\nIn progress.\n")
    if (len(text) > catalog.PROSE_CHARS or text.count("\n") + 1 > catalog.PROSE_LINES
            or len(catalog.parse_frontmatter(text)["description"]) > catalog.DESCRIPTION_CHARS):
        raise ValueError("run scaffold exceeds schema budgets; shorten names or split the process")
    journal = safe_path(LAYOUT.workspace_path("workspace/30_memory/journal"))
    trace_slug = "pipeline-" + hashlib.sha256(run_id.encode()).hexdigest()[:12]
    entry = journal / f"{today}-{now:%H%M}-{trace_slug}.md"
    if entry.exists():
        raise ValueError(f"{entry.relative_to(ROOT)}: journal trace already exists")
    safe_path(RUNS).mkdir(parents=True, exist_ok=True)
    # mkdir is exclusive even if another writer creates this run after the check.
    folder.mkdir()
    entry_created = False
    try:
        (folder / "run.md").write_text(text, encoding="utf-8")
        for stage in stages:
            (folder / stage["stage"] / "artifacts").mkdir(parents=True)
        journal.mkdir(parents=True, exist_ok=True)
        with entry.open("x", encoding="utf-8") as handle:
            entry_created = True
            handle.write(f"---\ndate: {today}T{now:%H:%M}\nkind: event\n"
                         f"refs: [90_runs/{run_id}/run.md]\n---\n\n"
                         f"Started pipeline {slug} version {fm['version']}; outputs pending.\n")
    except BaseException:
        if entry_created:
            entry.unlink()
        shutil.rmtree(folder)
        raise
    print(f"Started: {folder.relative_to(ROOT)}/run.md (pipeline {slug} version {fm['version']})")
    print(f"Next: {stages[0]['stage']}")


def checkpoint_state(folder, stage):
    output = safe_path(folder / stage["stage"] / stage["output"])
    if not output.is_file():
        return "no output"
    if stage["checkpoint"] == "false":
        return "output complete"
    receipt = folder / stage["stage"] / "checkpoint.json"
    try:
        review = json.loads(read(receipt))
        valid = (isinstance(review, dict) and review.get("approved") is True
                 and isinstance(review.get("reviewed_by"), str)
                 and review["reviewed_by"].strip()
                 and review.get("output_sha256") == hashlib.sha256(output.read_bytes()).hexdigest())
        datetime.date.fromisoformat(review.get("reviewed_on", ""))
        if valid:
            return "output complete; checkpoint reviewed"
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return "output pending checkpoint"


def status(run_id):
    folder = run_path(run_id)
    fm = metadata(folder / "run.md", "run")
    stages = fm.get("pipeline_stages")
    version = str(fm.get("pipeline_version", ""))
    ref = str(fm.get("pipeline", ""))
    match = re.fullmatch(r"workspace/60_capabilities/pipelines/(" + SLUG + r")/PIPELINE.md", ref)
    if (not match or not re.fullmatch(r"[1-9][0-9]*", version)
            or not re.fullmatch(r"[a-f0-9]{64}", str(fm.get("pipeline_digest", "")))
            or not isinstance(stages, list) or not stages):
        raise ValueError("run has no valid recorded pipeline version and stage plan")
    for index, stage in enumerate(stages, 1):
        if not isinstance(stage, dict):
            raise ValueError("invalid recorded stage plan")
        name = STAGE.fullmatch(str(stage.get("stage", "")))
        if (not name or int(name.group(1)) != index
                or not OUTPUT.fullmatch(str(stage.get("output", "")))
                or not isinstance(stage.get("checkpoint"), str)
                or stage["checkpoint"] not in {"true", "false"}):
            raise ValueError("invalid recorded stage plan")
    print(f"Run: {run_id} · pipeline {match.group(1)} version {version}")
    try:
        definition, verified_stages, digest = load_pipeline(match.group(1))
    except (OSError, ValueError):
        print("Definition unavailable or invalid: restore the recorded version before executing another stage.")
        print("Next: restore the recorded pipeline definition")
        return 1
    if digest != fm["pipeline_digest"]:
        print("Definition changed: restore the recorded version before executing another stage.")
        print("Next: restore the recorded pipeline definition")
        return 1
    if version != str(definition["version"]):
        raise ValueError("recorded pipeline version does not match the verified definition")
    if stages != verified_stages:
        raise ValueError("recorded stage plan does not match the verified definition")
    next_step = None
    for stage in stages:
        state = checkpoint_state(folder, stage)
        print(f"{stage['stage']}: {state} ({stage['stage']}/{stage['output']})")
        if next_step is None and state == "no output":
            next_step = stage["stage"]
        elif next_step is None and state == "output pending checkpoint":
            next_step = f"human checkpoint for {stage['stage']}"
    print(f"Next: {next_step or 'complete'}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
    begin = commands.add_parser("start")
    begin.add_argument("--pipeline", required=True)
    begin.add_argument("--run", required=True)
    begin.add_argument("--intent")
    report = commands.add_parser("status")
    report.add_argument("--run", required=True)
    args = parser.parse_args(argv)
    refused = refuse_unknown(LAYOUT, "pipeline")
    if refused:
        print(refused, file=sys.stderr)
        return 2
    try:
        if catalog.SCHEMA_ERROR:
            raise ValueError(catalog.SCHEMA_ERROR)
        if args.command == "check":
            errors, count = check_errors()
            for error in errors:
                print("ERROR " + error)
            if errors:
                return 1
            print(f"OK: {count} pipeline(s); contracts, numbering, executors, and budgets valid.")
        elif args.command == "start":
            start(args.pipeline, args.run, args.intent)
        else:
            return status(args.run)
    except (OSError, ValueError) as exc:
        print(f"pipeline: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
