#!/usr/bin/env python3
"""The commit gate must validate the index, independent of working-tree repairs."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.dont_write_bytecode=True
from test_gates import CLEAN, ENTRY, JOURNAL_TREE, build

class StagedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        build(self.tmp.name,CLEAN)
        for name in ('check_staged.py','journal_guard.py'):
            p=Path(__file__).parent/name
            if p.exists(): shutil.copy2(p,self.root/'tools'/name)
        (self.root/'.gitignore').write_text('.workspace-private/\n')
        (self.root/'workspace/00_meta/.uninitialised').touch()
        self.git('init','-q')
        self.git('config','user.name','Gate Fixture')
        self.git('config','user.email','fixture@example.invalid')
        self.git('add','-A')
        self.git('-c','core.hooksPath=/dev/null','commit','-qm','baseline')

    def git(self,*args):
        p=subprocess.run(['git',*args],cwd=self.root,text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        return p.stdout

    def gate(self):
        return subprocess.run([sys.executable,str(self.root/'tools/check_staged.py')],cwd=self.root,text=True,capture_output=True)

    def skill(self):
        chamber=self.root/'workspace/60_capabilities'
        shelf=chamber/'skills'
        record=shelf/'sample-skill/SKILL.md'
        record.parent.mkdir(parents=True)
        (chamber/'INDEX.md').write_text('''---
id: capabilities-index
type: doctrine
status: draft
description: Capabilities map. Use when finding a skill. Not for session entry (see workspace/AGENTS.md).
updated: 2026-10-07
---

# Capabilities

[Skills](skills/README.md).
''')
        (shelf/'README.md').write_text('''---
id: skills-door
type: doctrine
status: draft
description: Skills door. Use when finding reusable behaviour. Not for the capability map (see workspace/60_capabilities/INDEX.md).
updated: 2026-10-07
---

# Skills

<!-- lists: */SKILL.md -->
''')
        record.write_text('''---
id: skill-sample-skill
name: sample-skill
type: skill
status: draft
description: Sample skill. Use when checking staged skills. Not for the capability map (see workspace/60_capabilities/INDEX.md).
owner: agent
provenance: agent_proposed
updated: 2026-10-07
---

# Sample skill

Inspect the staged snapshot.
''')
        entrance=self.root/'workspace/AGENTS.md'
        entrance.write_text(entrance.read_text()+
                            '\n[Capabilities](60_capabilities/INDEX.md).\n')
        return record

    def test_valid_staged_skill_passes(self):
        self.skill()
        self.git('add','-A')
        result=self.gate()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_staged_skill_defect_cannot_hide_behind_repaired_worktree(self):
        record=self.skill()
        stray=record.parent/'stray.txt'
        stray.write_text('This file is outside the allowed skill subfolders.\n')
        self.git('add','-A')
        stray.unlink()
        result=self.gate()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('skills',result.stdout+result.stderr)
        self.assertIn('stray.txt',result.stdout+result.stderr)

    def test_valid_staged_skill_ignores_unstaged_invalid_name(self):
        record=self.skill()
        self.git('add','-A')
        record.write_text(record.read_text().replace('name: sample-skill',
                                                    'name: different-name'))
        result=self.gate()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_invalid_staged_metadata_cannot_hide_behind_repaired_worktree(self):
        p=self.root/'workspace/70_seams/SHARED.md'
        original=p.read_text()
        p.write_text(original.replace('status: mature','status: broken'))
        self.git('add',str(p))
        p.write_text(original)
        result=self.gate()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('status',result.stdout+result.stderr)

    def test_valid_index_ignores_unstaged_broken_metadata(self):
        p=self.root/'workspace/70_seams/SHARED.md'
        p.write_text(p.read_text().replace('status: mature','status: broken'))
        result=self.gate()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_staged_journal_edit_cannot_hide_behind_unstaged_symlink(self):
        build(self.tmp.name,JOURNAL_TREE)
        (self.root/'workspace/00_meta/.uninitialised').unlink()
        private=self.root/'.workspace-private'
        private.mkdir()
        (private/'never-share.txt').write_text('fixture-private-literal\n')
        entrance=self.root/'workspace/AGENTS.md'
        entrance.write_text(entrance.read_text()+
                            '\n[Memory](30_memory/INDEX.md). [Runs](90_runs/INDEX.md).\n')
        self.git('add','-A')
        self.git('-c','core.hooksPath=/dev/null','commit','-qm','journal')
        result=self.gate()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

        record=self.root/ENTRY
        record.write_text(record.read_text()+'\nChanged committed event.\n')
        self.git('add',ENTRY)
        record.unlink()
        record.symlink_to(self.root/'workspace/70_seams/SHARED.md')
        result=self.gate()
        self.assertNotEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('staged mutation',result.stdout+result.stderr)
        self.assertIn(ENTRY,result.stdout+result.stderr)

    def test_staged_extracted_journal_edit_ignores_unstaged_entrance_symlink(self):
        build(self.tmp.name,JOURNAL_TREE)
        workspace=self.root/'workspace'
        for path in workspace.iterdir():
            path.rename(self.root/path.name)
        workspace.rmdir()
        self.git('add','-A')
        self.git('-c','core.hooksPath=/dev/null','commit','-qm','extracted journal')

        entry=ENTRY.split('/',1)[1]
        record=self.root/entry
        record.write_text(record.read_text()+'\nChanged committed event.\n')
        self.git('add',entry)
        command=[sys.executable,str(self.root/'tools/journal_guard.py'),'--staged']
        result=subprocess.run(command,cwd=self.root,text=True,capture_output=True)
        self.assertEqual(result.returncode,2,result.stdout+result.stderr)

        entrance=self.root/'AGENTS.md'
        entrance.unlink()
        entrance.symlink_to('absent-entrance.md')
        result=subprocess.run(command,cwd=self.root,text=True,capture_output=True)
        self.assertEqual(result.returncode,2,result.stdout+result.stderr)
        self.assertIn(entry,result.stdout+result.stderr)

    def test_staged_symlink_cannot_escape_snapshot(self):
        (self.root/'escape').symlink_to('../outside')
        self.git('add','escape')
        result=self.gate()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('symlink',result.stdout+result.stderr)

    def test_initial_commit_and_index_graph_are_checked(self):
        p=self.root/'workspace/AGENTS.md'
        original=p.read_text()
        p.write_text(original+'\n[broken](absent.md)\n')
        self.git('add',str(p))
        p.write_text(original)
        result=self.gate()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('dead link',result.stdout+result.stderr)

if __name__=='__main__': unittest.main()
