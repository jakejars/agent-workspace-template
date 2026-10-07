#!/usr/bin/env python3
"""Upgrade a main instance using the executable block in migrations.md."""

import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

from test_gate_corrections import isolated_git_env

SOURCE = Path(__file__).resolve().parents[1]
TODAY = "2026-10-07"


# Last commit released under the Sett name; existing instances descend from it.
LEGACY_BASELINE = "c4e375af698b03e1abbedbad67b45810aa1867c7"

class UpgradeTests(unittest.TestCase):
    def command(self, args, *, cwd=None, data=None, env=None):
        return subprocess.run(args, cwd=cwd or self.root, input=data,
                              capture_output=True, text=True, env=env or self.env)

    def tool(self, name, *args, data=None, env=None, checkout=None):
        path = (checkout or self.root) / "tools" / name
        return self.command([sys.executable, str(path), *args], data=data, env=env)

    def succeeds(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_main_instance_upgrades_with_documented_commands(self):
        self.env = isolated_git_env()
        for name in ("WORKSPACE_ROOT", "SETT_ROOT"):
            self.env.pop(name, None)
        found = subprocess.run(["git", "rev-parse", "--verify", LEGACY_BASELINE + "^{commit}"],
                               cwd=SOURCE, capture_output=True, text=True, env=self.env)
        if found.returncode != 0:
            self.skipTest("legacy Sett baseline commit unavailable; fetch full history to exercise upgrade")
        baseline = found.stdout.strip()
        with tempfile.TemporaryDirectory(prefix="workspace-upgrade-") as tmp:
            self.root = Path(tmp) / "instance"
            self.root.mkdir()
            archived = subprocess.run(["git", "archive", baseline], cwd=SOURCE,
                                      capture_output=True, check=True, env=self.env)
            with tarfile.open(fileobj=io.BytesIO(archived.stdout)) as archive:
                # The archive is the pinned last Sett release.
                for entry in archive:
                    target = self.root / entry.name
                    if entry.isdir():
                        target.mkdir(parents=True, exist_ok=True)
                    elif entry.isfile():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(archive.extractfile(entry).read())
                        target.chmod(entry.mode)
                    else:
                        self.fail(f"unsupported main archive member: {entry.name}")

            values = self.root / "workspace/00_meta/values.json"
            values.write_text(json.dumps({"PRINCIPAL_NAME": "Upgrade Fixture",
                                          "WORKSPACE_ID": "upgrade-fixture"}),
                              encoding="utf-8")
            # Assemble the fixture term so copied test source cannot hit itself.
            term = "zz-upgrade-" + "private-term"
            private = self.root / ".sett-private/never-share.txt"
            private.parent.mkdir()
            private.write_text(term + "\n", encoding="utf-8")
            self.succeeds(self.tool("instantiate.py", "--date", TODAY))
            intent = self.root / "workspace/20_intent/active/upgrade.md"
            intent.write_text(f"""---
id: intent-upgrade
type: intent
status: draft
description: Upgrade fixture. Use when checking upgrades. Not for history (see workspace/20_intent/INDEX.md).
owner: human
lifecycle: captured
updated: {TODAY}
---

# Upgrade

## Objective

Keep an existing instance usable after updating its support files.

## Checkpoint

Next: apply the documented upgrade.
""", encoding="utf-8")
            self.succeeds(self.tool("instantiate.py", "--finalize", "--hooks", "portable"))
            self.succeeds(self.tool("instantiate.py", "--check"))
            journal = next((self.root / "workspace/30_memory/journal").glob("*-instantiated.md"))
            protected = [private, journal, self.root / "workspace/10_identity/principal.md",
                         self.root / "workspace/00_meta/ready.json"]
            original = {path: path.read_bytes() for path in protected}
            self.succeeds(self.command(["git", "init", "-q"]))
            self.succeeds(self.command(["git", "config", "user.name", "Upgrade Test"]))
            self.succeeds(self.command(["git", "config", "user.email", "upgrade@example.invalid"]))
            self.succeeds(self.tool("hooks/install.py"))
            self.succeeds(self.command(["git", "add", "."]))
            self.succeeds(self.command(["git", "commit", "-qm", "main instance fixture"]))
            stale = self.root / ".sett-cache/context.json"
            stale.parent.mkdir(exist_ok=True)
            stale.write_text(json.dumps({"obsolete": term}), encoding="utf-8")

            guide = (SOURCE / "doctrine/migrations.md").read_text(encoding="utf-8")
            section = guide.split("## Agent Workspace Template rename\n", 1)[1].split("\n## ", 1)[0]
            blocks = re.findall(r"```sh\n(.*?)```", section, re.S)
            self.assertEqual(len(blocks), 1, "rename migration needs one executable upgrade block")
            upgrade_env = dict(self.env, TEMPLATE=str(SOURCE), INSTANCE=str(self.root))
            self.succeeds(self.command(["bash", "-c", blocks[0]], env=upgrade_env))
            self.assertEqual(original, {path: path.read_bytes() for path in protected})
            self.assertFalse((self.root / ".workspace-private").exists())
            self.assertEqual((self.root / "doctrine/schema.json").read_bytes(),
                             (SOURCE / "doctrine/schema.json").read_bytes())

            for name, args in (("build_catalog.py", ("--check",)),
                               ("check_loop.py", ()), ("doctor.py", ()),
                               ("agnostic_check.py", ()), ("scrub_check.py", ()),
                               ("skills.py", ("check",)), ("pipeline.py", ("check",))):
                self.succeeds(self.tool(name, *args))
            self.succeeds(self.command(["git", "add", "tools", ".gitignore", "doctrine/schema.json"]))
            self.succeeds(self.tool("check_staged.py"))

            leak = self.root / "upgrade-leak.txt"
            leak.write_text(term + "\n", encoding="utf-8")
            result = self.tool("scrub_check.py")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("never-share term", result.stdout + result.stderr)
            self.assertNotIn(term, result.stdout + result.stderr)
            self.succeeds(self.command(["git", "add", leak.name]))
            leak.write_text("clean\n", encoding="utf-8")
            self.succeeds(self.tool("scrub_check.py"))
            result = self.tool("scrub_check.py", "--staged")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("never-share term", result.stdout + result.stderr)
            self.assertNotIn(term, result.stdout + result.stderr)
            self.succeeds(self.command(["git", "reset", "-q", "HEAD", "--", leak.name]))
            leak.unlink()

            # A legacy adapter may execute a guard from a different checkout.
            adapter_env = dict(self.env, SETT_ROOT=str(self.root))
            for path in (private, journal):
                for op in ("modify", "create-or-overwrite"):
                    result = self.tool("journal_guard.py", data=json.dumps({"op": op, "path": str(path)}),
                                       env=adapter_env, checkout=SOURCE)
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            journal.write_bytes(original[journal] + b"\nmutation\n")
            self.succeeds(self.command(["git", "add", str(journal.relative_to(self.root))]))
            result = self.tool("journal_guard.py", "--staged")
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("journal", (result.stdout + result.stderr).lower())
            self.succeeds(self.command(["git", "reset", "-q", "HEAD", "--", str(journal.relative_to(self.root))]))
            journal.write_bytes(original[journal])

            self.succeeds(self.tool("context.py", "refresh"))
            cache = self.root / ".workspace-cache/context.json"
            self.assertIn("workspace/AGENTS.md", json.loads(cache.read_text())["edges"])
            # Empty malformed packages prove both feature gates run during refresh.
            for folder, gate, diagnostic in (("skills", "skills.py", "missing regular SKILL.md"),
                                             ("pipelines", "pipeline.py", "PIPELINE.md")):
                broken = self.root / "workspace/60_capabilities" / folder / "broken-upgrade"
                broken.mkdir(parents=True)
                result = self.tool(gate, "check")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(diagnostic, result.stdout + result.stderr)
                result = self.tool("context.py", "refresh", "--force")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(diagnostic, result.stdout + result.stderr)
                shutil.rmtree(broken)
                self.succeeds(self.tool("context.py", "refresh", "--force"))
            self.succeeds(self.tool("check_staged.py"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
