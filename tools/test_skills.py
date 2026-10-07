#!/usr/bin/env python3
"""Positive and planted-negative cases for native skills and copy exports.

  python3 tools/test_skills.py

All commands run against a throwaway source tree; no runtime settings change.
"""

import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parent.parent


class SkillTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="workspace-skills-")
        self.home = Path(self.temp.name)
        self.root = self.home / "source"
        (self.root / "tools").mkdir(parents=True)
        for name in ("skills.py", "build_catalog.py", "workspace_layout.py", "scrub_check.py"):
            source = SOURCE / "tools" / name
            if source.exists():
                shutil.copy2(source, self.root / "tools" / name)
        (self.root / "doctrine").mkdir()
        shutil.copy2(SOURCE / "doctrine/schema.json",
                     self.root / "doctrine/schema.json")
        self.shelf = self.root / "workspace/60_capabilities/skills"
        self.shelf.mkdir(parents=True)
        (self.root / "workspace/AGENTS.md").write_text("# Entrance\n")
        (self.root / "workspace/00_meta").mkdir()
        (self.root / "workspace/00_meta/.uninitialised").write_text("")
        (self.shelf / "README.md").write_text("# Skills\n")
        self.output = self.home / "native-skills"

    def tearDown(self):
        self.temp.cleanup()

    def run_tool(self, *args):
        result = subprocess.run(
            [sys.executable, str(self.root / "tools/skills.py"), *args],
            cwd=self.root, capture_output=True, text=True)
        return result.returncode, result.stdout + result.stderr

    def skill(self, name="sample-skill", **overrides):
        fm = {"id": name, "type": "skill", "status": "draft", "name": name,
              "description": "Test skill. Use when testing. Not for policy "
              "(see workspace/60_capabilities/skills/README.md).",
              "owner": "agent", "provenance": "agent_proposed",
              "updated": "2026-10-07"}
        fm.update(overrides)
        path = self.shelf / name
        path.mkdir(exist_ok=True)
        content = "---\n" + "".join(f"{key}: {value}\n" for key, value in fm.items()
                                      if value is not None)
        (path / "SKILL.md").write_text(content + "---\n\n# Run the skill\n")
        return path

    def approval(self, name="skill-promotion", **overrides):
        path = self.root / "workspace/80_governance/approvals" / (name + ".md")
        path.parent.mkdir(parents=True, exist_ok=True)
        fm = {"id": name, "type": "approval", "status": "draft",
              "description": "Skill approval. Use when checking trust. Not for "
              "skills (see workspace/60_capabilities/skills/README.md).",
              "updated": "2026-10-07", "scope": "workspace", "what": "skill use",
              "packet": "skill-proposal", "class": "B", "granted_by": "human",
              "granted": "2026-10-07", "expiry": "2099-12-31"}
        fm.update(overrides)
        path.write_text("---\n" + "".join(f"{key}: {value}\n"
                                         for key, value in fm.items()
                                         if value is not None) + "---\n")
        return "../80_governance/approvals/" + path.name

    def ledger(self, rows):
        path = self.root / "workspace/60_capabilities/installed.md"
        path.write_text("# Ledger\n\n"
                        "| capability | version | sha256 | source | installed | trust | approval |\n"
                        "|---|---|---|---|---|---|---|\n" +
                        "".join(f"| {name} | 1 | abcdef123456 | local | 2026-10-07 | {trust} | {approval} |\n"
                                for name, trust, approval in rows))

    def test_clean_skill_and_optional_payloads_pass(self):
        skill = self.skill()
        for folder, filename in (("scripts", "run.py"),
                                 ("references", "notes.md"),
                                 ("assets", "icon.bin")):
            (skill / folder).mkdir()
            (skill / folder / filename).write_bytes(b"payload\n")
        code, out = self.run_tool("check")
        self.assertEqual(code, 0, out)
        self.assertIn("1 skill", out)

    def test_bad_name_is_rejected(self):
        self.skill("Bad_name")
        code, out = self.run_tool("check")
        self.assertEqual(code, 1, out)
        self.assertIn("name", out)

    def test_frontmatter_name_must_equal_directory(self):
        path = self.skill()
        text = (path / "SKILL.md").read_text()
        (path / "SKILL.md").write_text(text.replace("name: sample-skill", "name: other-name"))
        code, out = self.run_tool("check")
        self.assertEqual(code, 1, out)
        self.assertIn("directory", out)

    def test_name_length_is_bounded(self):
        self.skill("a" * 65)
        code, out = self.run_tool("check")
        self.assertEqual(code, 1, out)
        self.assertIn("64", out)

    def test_overlong_description_is_rejected(self):
        self.skill(description="x" * 1025)
        code, out = self.run_tool("check")
        self.assertEqual(code, 1, out)
        self.assertIn("description", out)

    def test_native_description_length_precedes_house_normalization(self):
        self.skill(description="Test" + " " * 1024 + "skill. Use when testing. Not for policy "
                   "(see workspace/60_capabilities/skills/README.md).")
        code, out = self.run_tool("check")
        self.assertEqual(code, 1, out)
        self.assertIn("1024", out)

    def test_string_fields_reject_list_values(self):
        for field in ("id", "name", "description"):
            with self.subTest(field=field):
                path = self.skill()
                text = (path / "SKILL.md").read_text()
                lines = [f"{field}: [foo]" if line.startswith(field + ":") else line
                         for line in text.splitlines()]
                (path / "SKILL.md").write_text("\n".join(lines) + "\n")
                code, out = self.run_tool("check")
                self.assertEqual(code, 1, out)
                self.assertIn(field, out)

    def test_house_description_limit_is_preserved(self):
        self.skill(description="x" * 181)
        code, out = self.run_tool("check")
        self.assertEqual(code, 1, out)
        self.assertIn("180", out)

    def test_all_template_fields_are_required(self):
        for missing in ("id", "type", "status", "updated", "owner", "provenance"):
            with self.subTest(missing=missing):
                self.skill(**{missing: None})
                code, out = self.run_tool("check")
                self.assertEqual(code, 1, out)
                self.assertIn(missing, out)

    def test_reserved_skill_still_requires_owner_and_provenance(self):
        self.skill(status="reserved", owner=None, provenance=None)
        code, out = self.run_tool("check")
        self.assertEqual(code, 1, out)
        self.assertIn("owner", out)
        self.assertIn("provenance", out)

    def test_root_payload_file_is_rejected(self):
        (self.skill() / "notes.md").write_text("wrong location\n")
        code, out = self.run_tool("check")
        self.assertEqual(code, 1, out)
        self.assertIn("notes.md", out)

    def test_missing_skill_file_is_rejected(self):
        (self.shelf / "missing-skill").mkdir()
        code, out = self.run_tool("check")
        self.assertEqual(code, 1, out)
        self.assertIn("SKILL.md", out)

    def test_source_symlinks_are_rejected(self):
        skill = self.skill()
        (skill / "scripts").mkdir()
        secret = self.home / "outside.txt"
        secret.write_text("outside\n")
        (skill / "scripts/link.txt").symlink_to(secret)
        code, out = self.run_tool("check")
        self.assertEqual(code, 1, out)
        self.assertIn("symlink", out)

    def test_dangling_shelf_symlink_is_rejected(self):
        shutil.rmtree(self.shelf)
        self.shelf.symlink_to(self.home / "missing-shelf", target_is_directory=True)
        code, out = self.run_tool("check")
        self.assertEqual(code, 1, out)
        self.assertIn("symlink", out)

    def test_skill_shelf_file_has_a_plain_diagnostic(self):
        shutil.rmtree(self.shelf)
        self.shelf.write_text("not a skill directory\n")
        code, out = self.run_tool("check")
        self.assertEqual(code, 1, out)
        self.assertIn("directory", out)
        self.assertNotIn("Traceback", out)

    def test_export_copies_and_refreshes_owned_directory(self):
        skill = self.skill()
        code, out = self.run_tool("export", "--to", str(self.output))
        self.assertEqual(code, 0, out)
        exported = self.output / skill.name
        self.assertEqual((exported / "SKILL.md").read_bytes(),
                         (skill / "SKILL.md").read_bytes())
        self.assertFalse((exported / "SKILL.md").is_symlink())
        (exported / "stale.txt").write_text("old export\n")
        (skill / "scripts").mkdir()
        (skill / "scripts/run.py").write_text("print('ready')\n")
        code, out = self.run_tool("export", "--to", str(self.output))
        self.assertEqual(code, 0, out)
        self.assertFalse((exported / "stale.txt").exists())
        self.assertTrue((exported / "scripts/run.py").is_file())

    def test_foreign_directory_is_preserved_without_partial_export(self):
        self.skill("first-skill")
        self.skill("foreign-skill")
        foreign = self.output / "foreign-skill"
        foreign.mkdir(parents=True)
        keeper = foreign / "keep.txt"
        keeper.write_text("human file\n")
        code, out = self.run_tool("export", "--to", str(self.output))
        self.assertEqual(code, 1, out)
        self.assertIn("ownership", out)
        self.assertEqual(keeper.read_text(), "human file\n")
        self.assertFalse((self.output / "first-skill").exists())

    def test_source_and_support_destinations_are_refused(self):
        self.skill()
        for target in (self.shelf / "nested", self.root / "workspace/new-output",
                       self.root / "doctrine/native", self.root / "tools/native",
                       self.root / "registry/native", self.root):
            with self.subTest(target=target):
                code, out = self.run_tool("export", "--to", str(target))
                self.assertEqual(code, 1, out)
                self.assertIn("source", out)

    def test_destination_symlink_is_refused(self):
        self.skill()
        self.output.symlink_to(self.home / "actual-output", target_is_directory=True)
        code, out = self.run_tool("export", "--to", str(self.output))
        self.assertEqual(code, 1, out)
        self.assertIn("symlink", out)
        self.assertFalse((self.home / "actual-output").exists())

    def test_invalid_source_refuses_export_before_creating_destination(self):
        self.skill()
        self.skill("bad-name", provenance=None)
        code, out = self.run_tool("export", "--to", str(self.output))
        self.assertEqual(code, 1, out)
        self.assertFalse(self.output.exists())

    def test_trusted_only_uses_ledger_and_human_approval(self):
        self.skill("trusted-skill")
        self.skill("local-skill", status="mature", provenance="promoted", owner="human")
        self.skill("untrusted-skill")
        approval = self.approval()
        self.ledger([("trusted-skill", "trusted", approval),
                     ("untrusted-skill", "untrusted", "")])
        code, out = self.run_tool("export", "--to", str(self.output), "--trusted-only")
        self.assertEqual(code, 0, out)
        self.assertTrue((self.output / "trusted-skill/SKILL.md").is_file())
        self.assertFalse((self.output / "local-skill").exists())
        self.assertFalse((self.output / "untrusted-skill").exists())

    def test_newest_withdrawal_overrides_previous_trust(self):
        self.skill()
        approval = self.approval()
        self.ledger([("sample-skill", "withdrawn", approval),
                     ("sample-skill", "trusted", approval)])
        code, out = self.run_tool("export", "--to", str(self.output), "--trusted-only")
        self.assertEqual(code, 0, out)
        self.assertFalse((self.output / "sample-skill").exists())

    def test_trusted_only_removes_previously_owned_withdrawn_export(self):
        self.skill()
        approval = self.approval()
        self.ledger([("sample-skill", "trusted", approval)])
        code, out = self.run_tool("export", "--to", str(self.output), "--trusted-only")
        self.assertEqual(code, 0, out)
        foreign = self.output / "foreign-skill"
        foreign.mkdir()
        (foreign / "SKILL.md").write_text("human-owned runtime skill\n")
        self.ledger([("sample-skill", "withdrawn", approval)])
        code, out = self.run_tool("export", "--to", str(self.output), "--trusted-only")
        self.assertEqual(code, 0, out)
        self.assertIn("removed", out)
        self.assertFalse((self.output / "sample-skill").exists())
        self.assertEqual((foreign / "SKILL.md").read_text(), "human-owned runtime skill\n")

    def test_owned_export_symlink_refuses_removal_before_other_exports(self):
        self.skill()
        code, out = self.run_tool("export", "--to", str(self.output))
        self.assertEqual(code, 0, out)
        secret = self.home / "outside.txt"
        secret.write_text("outside\n")
        (self.output / "sample-skill/link.txt").symlink_to(secret)
        self.skill("trusted-skill")
        self.ledger([("sample-skill", "withdrawn", ""),
                     ("trusted-skill", "trusted", self.approval())])
        code, out = self.run_tool("export", "--to", str(self.output), "--trusted-only")
        self.assertEqual(code, 1, out)
        self.assertIn("symlink", out)
        self.assertFalse((self.output / "trusted-skill").exists())
        self.assertEqual(secret.read_text(), "outside\n")

    def test_missing_and_malformed_approvals_do_not_grant_trust(self):
        self.skill()
        for approval in ("", "../80_governance/approvals/missing.md",
                         self.approval(name="incomplete", granted=None),
                         self.approval(name="unopened", status="reserved", granted=None),
                         self.approval(name="wrong-class", **{"class": "C"})):
            with self.subTest(approval=approval):
                self.ledger([("sample-skill", "trusted", approval)])
                code, out = self.run_tool("export", "--to", str(self.output), "--trusted-only")
                self.assertEqual(code, 0, out)
                self.assertFalse((self.output / "sample-skill").exists())

    def test_historical_promotion_approval_does_not_withdraw_trust(self):
        self.skill()
        approval = self.approval(expiry="2000-01-01", granted="1999-01-01")
        self.ledger([("sample-skill", "trusted", approval)])
        code, out = self.run_tool("export", "--to", str(self.output), "--trusted-only")
        self.assertEqual(code, 0, out)
        self.assertTrue((self.output / "sample-skill/SKILL.md").is_file())

    def test_export_scrubs_selected_bytes_without_printing_private_term(self):
        skill = self.skill()
        term = "private-" + "alder-nine"
        private = self.root / ".workspace-private"
        private.mkdir()
        (private / "never-share.txt").write_text(term + "\n")
        (skill / "references").mkdir()
        secret = skill / "references/private.md"
        secret.write_text(term + "\n")
        before = secret.read_bytes()
        code, out = self.run_tool("export", "--to", str(self.output))
        self.assertEqual(code, 1, out)
        self.assertNotIn(term, out)
        self.assertIn("never-share", out)
        self.assertEqual(secret.read_bytes(), before)
        self.assertFalse(self.output.exists())

    def test_export_obeys_existing_text_only_distribution_rule(self):
        skill = self.skill()
        (skill / "assets").mkdir()
        (skill / "assets/image.bin").write_bytes(b"\x00\xff")
        code, out = self.run_tool("export", "--to", str(self.output))
        self.assertEqual(code, 1, out)
        self.assertIn("text", out)
        self.assertFalse(self.output.exists())

    def test_extracted_workspace_uses_its_local_chamber(self):
        self.skill()
        for child in list((self.root / "workspace").iterdir()):
            shutil.move(str(child), self.root / child.name)
        (self.root / "workspace").rmdir()
        (self.root / "70_seams").mkdir()
        code, out = self.run_tool("check")
        self.assertEqual(code, 0, out)
        self.assertIn("1 skill", out)
        private = self.root / ".workspace-private"
        private.mkdir()
        (private / "no-private-terms.json").write_text('{"version": 1, "confirmed": true}')
        code, out = self.run_tool("export", "--to", str(self.output))
        self.assertEqual(code, 0, out)
        self.assertTrue((self.output / "sample-skill/SKILL.md").is_file())
        for chamber in ("00_meta", "10_identity", "20_intent", "30_memory", "40_knowledge",
                        "50_registers", "60_capabilities", "70_seams", "80_governance", "90_runs",
                        "boards", "fields"):
            with self.subTest(chamber=chamber):
                code, out = self.run_tool("export", "--to", str(self.root / chamber / "native"))
                self.assertEqual(code, 1, out)
                self.assertIn("source", out)

    def registry(self, kind="skill", source="SKILL.md", target=None):
        capability = self.root / "registry/sample-skill"
        files = capability / "files"
        files.mkdir(parents=True, exist_ok=True)
        local = self.skill()
        shutil.copy2(local / "SKILL.md", files / source)
        digest = hashlib.sha256((files / source).read_bytes()).hexdigest()
        target = target or "60_capabilities/skills/sample-skill/" + source
        kind_line = "" if kind is None else f"kind: {kind}\n"
        (capability / "manifest.yml").write_text(
            "name: sample-skill\n" + kind_line + "version: 1\n"
            "description: Test bundle. Use when testing. Not for policy "
            "(see registry/README.md).\nupdated: 2026-10-07\nfiles:\n"
            f"  - src: {source}\n    target: {target}\n    sha256: {digest}\n")

    def registry_check(self):
        script = "import build_catalog; errors=[]; build_catalog.check_registry(errors); print('\\n'.join(errors)); raise SystemExit(bool(errors))"
        result = subprocess.run([sys.executable, "-c", script],
                                cwd=self.root / "tools", capture_output=True, text=True)
        return result.returncode, result.stdout + result.stderr

    def test_registry_skill_bundle_checksums_and_shape_pass(self):
        self.registry()
        code, out = self.registry_check()
        self.assertEqual(code, 0, out)
        code, out = self.run_tool("check")
        self.assertEqual(code, 0, out)
        self.assertIn("2 skill", out)

    def test_registry_legacy_manifest_remains_valid(self):
        self.registry(kind=None)
        code, out = self.registry_check()
        self.assertEqual(code, 0, out)

    def test_registry_unknown_kind_is_rejected(self):
        self.registry(kind="unknown")
        code, out = self.registry_check()
        self.assertEqual(code, 1, out)
        self.assertIn("kind", out)

    def test_registry_missing_skill_and_root_strays_are_rejected(self):
        for source in ("README.md", "notes.md"):
            with self.subTest(source=source):
                shutil.rmtree(self.root / "registry", ignore_errors=True)
                self.registry(source=source)
                code, out = self.registry_check()
                self.assertEqual(code, 1, out)
                self.assertIn("SKILL.md", out)

    def test_registry_mismatched_skill_target_is_rejected(self):
        self.registry(target="60_capabilities/wrong/SKILL.md")
        code, out = self.registry_check()
        self.assertEqual(code, 1, out)
        self.assertIn("target", out)


if __name__ == "__main__":
    unittest.main()
