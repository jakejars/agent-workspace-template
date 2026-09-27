#!/usr/bin/env python3
"""Behavioral context and lifecycle regressions using a real small workspace."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
from test_gates import CLEAN, build

SOURCE = Path(__file__).resolve().parent

class ContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        build(self.tmp.name, CLEAN)
        for p in SOURCE.glob('*.py'):
            shutil.copy2(p, self.root / 'tools' / p.name)
        (self.root/'workspace/00_meta/.uninitialised').touch()
        (self.root / '.gitignore').write_text('.sett-private/\n.sett-cache/\nwork/\nartifacts/\n')

    def run_tool(self, name, *args, data=None):
        p = subprocess.run([sys.executable, str(self.root/'tools'/name), *args],
                           cwd=self.root, input=json.dumps(data) if data else None,
                           capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def record(self, name, text):
        path = self.root / ('workspace/40_knowledge/' + name + '.md')
        path.parent.mkdir(exist_ok=True)
        path.write_text(text)
        door = self.root/'workspace/AGENTS.md'
        door.write_text(door.read_text()+f'\n- [{name}](40_knowledge/{name}.md)\n')
        return path

    def knowledge(self, name, *, load='cue', review='2099-01-01', provenance='authored', kind='knowledge'):
        return self.record(name, f'''---
id: {name}
type: {kind}
status: draft
description: {name} build cache. Use when fixing build cache. Not for runtime (see workspace/AGENTS.md).
load: {load}
provenance: {provenance}
review_after: {review}
updated: 2026-09-06
---

# {name}

BODY MUST NOT BE IN CUE OUTPUT.
''')

    def task(self, name='repair-cache', lifecycle='captured'):
        rel = f'workspace/20_intent/active/{name}.md'
        p = self.root/rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f'''---
id: intent-{name}
type: intent
status: draft
description: Repair cache. Use when fixing cache. Not for history (see workspace/AGENTS.md).
updated: 2026-09-06
---

# Repair cache

## Objective

Fix the cache miss.

## Checkpoint

Next: reproduce the miss.
''')
        # Fixture lacks the intent edge-field declaration; path is enough to
        # distinguish active vs completed without expanding its schema.
        door=self.root/'workspace/AGENTS.md'
        door.write_text(door.read_text()+f'\n- [task]({rel})\n')
        return p

    def test_explicit_task_boot_has_no_implicit_historical_selection(self):
        p=self.root/'workspace/AGENTS.md'
        p.write_text(p.read_text().replace('boot_selector: latest-closed-at','boot_selector: explicit-task').replace('boot_dynamic: workspace/90_runs/*/handover.md','boot_dynamic: workspace/20_intent/active/*.md'))
        self.task()
        code,out=self.run_tool('context.py','refresh')
        self.assertEqual(code,0,out)
        data=json.loads((self.root/'.sett-cache/context.json').read_text())
        self.assertEqual(data['boot']['dynamic'],0)
        self.assertEqual(data['boot']['dynamic_source'],'none')

    def test_refresh_writes_verified_graph_and_reuses_unchanged_cache(self):
        code, out = self.run_tool('context.py','refresh')
        self.assertEqual(code,0,out)
        p=self.root/'.sett-cache/context.json'
        first=json.loads(p.read_text())
        self.assertIn('workspace/AGENTS.md',first['edges'])
        stamp=p.stat().st_mtime_ns
        code,out=self.run_tool('context.py','refresh')
        self.assertEqual(code,0,out)
        self.assertEqual(p.stat().st_mtime_ns,stamp)

    def test_query_returns_cues_not_bodies_drill_or_stale_records(self):
        self.knowledge('cache-evidence',provenance='agent_proposed')
        self.knowledge('cache-stale',review='2000-01-01')
        self.knowledge('cache-deep',load='drill')
        code,out=self.run_tool('context.py','show','--query','build cache')
        self.assertEqual(code,0,out)
        self.assertIn('cache-evidence',out)
        self.assertIn('provisional',out)
        self.assertNotIn('cache-stale',out)
        self.assertNotIn('cache-deep',out)
        self.assertNotIn('BODY MUST',out)

    def test_explicit_task_loads_checkpoint_but_closed_task_is_refused(self):
        p=self.task()
        code,out=self.run_tool('context.py','show','--task','intent-repair-cache')
        self.assertEqual(code,0,out)
        self.assertIn('Next: reproduce',out)
        q=self.root/'workspace/20_intent/satisfied/repair-cache.md'
        q.parent.mkdir(parents=True)
        p.rename(q)
        door=self.root/'workspace/AGENTS.md'
        door.write_text(door.read_text().replace('20_intent/active/repair-cache.md','20_intent/satisfied/repair-cache.md'))
        code,out=self.run_tool('context.py','show','--task','intent-repair-cache')
        self.assertNotEqual(code,0,out)
        self.assertNotIn('Next: reproduce',out)

    def test_source_change_invalidates_cache_and_broken_graph_is_refused(self):
        self.assertEqual(self.run_tool('context.py','refresh')[0],0)
        p=self.root/'workspace/AGENTS.md'
        p.write_text(p.read_text()+'\n[broken](missing.md)\n')
        code,out=self.run_tool('context.py','show','--query','cache')
        self.assertNotEqual(code,0,out)
        self.assertIn('dead link',out)

    def test_routing_is_bounded_with_one_thousand_records(self):
        folder=self.root/'workspace/40_knowledge'
        folder.mkdir(exist_ok=True)
        (folder/'INDEX.md').write_text("---\nid: knowledge-door\ntype: doctrine\nstatus: draft\ndescription: Knowledge map. Use when looking up facts. Not for boot (see workspace/AGENTS.md).\nupdated: 2026-09-06\n---\n\n# Knowledge\n\n<!-- lists: *.md -->\n")
        entrance=self.root/'workspace/AGENTS.md'
        entrance.write_text(entrance.read_text()+'\n[knowledge](40_knowledge/INDEX.md)\n')
        for n in range(1000):
            subject='quasar invalidation' if n==731 else f'cache topic {n}'
            (folder/f'note-{n}.md').write_text(f"---\nid: note-{n}\ntype: knowledge\nstatus: draft\nprovenance: authored\ndescription: {subject}. Use when fixing {subject}. Not for boot (see workspace/AGENTS.md).\nupdated: 2026-09-06\n---\n\nDetailed evidence body should stay on disk.\n")
        code,out=self.run_tool('context.py','show','--query','quasar invalidation')
        self.assertEqual(code,0,out)
        self.assertIn('note-731.md',out)
        self.assertNotIn('Detailed evidence body',out)
        self.assertLess(len(out),1000)
        self.assertLessEqual(sum(line.startswith('- ') for line in out.splitlines()),3)

    def test_deleted_linked_artifact_invalidates_cached_graph(self):
        p=self.root/'artifacts/proof.txt'
        p.parent.mkdir()
        p.write_text('evidence')
        door=self.root/'workspace/AGENTS.md'
        door.write_text(door.read_text()+'\n[proof](artifacts/proof.txt)\n')
        self.assertEqual(self.run_tool('context.py','refresh')[0],0)
        p.unlink()
        code,out=self.run_tool('context.py','refresh')
        self.assertNotEqual(code,0,out)
        self.assertIn('dead link',out)

    def test_private_rule_change_invalidates_previously_clean_cache(self):
        self.knowledge('cache-evidence')
        self.assertEqual(self.run_tool('context.py','refresh')[0],0)
        private=self.root/'.sett-private/never-share.txt'
        private.parent.mkdir()
        private.write_text('cache-evidence\n')
        code,out=self.run_tool('context.py','show','--query','build cache')
        self.assertNotEqual(code,0,out)
        self.assertNotIn('cache-evidence',out)
        self.assertIn('never-share',out)

    def test_checkpoint_is_atomic_and_rejects_oversized_state(self):
        p=self.task()
        code,out=self.run_tool('context.py','checkpoint','--task','intent-repair-cache','--text','Next: verify fixed miss.')
        self.assertEqual(code,0,out)
        self.assertIn('Next: verify fixed miss.',p.read_text())
        before=p.read_bytes()
        code,out=self.run_tool('context.py','checkpoint','--task','intent-repair-cache','--text','x'*4000)
        self.assertNotEqual(code,0,out)
        self.assertEqual(p.read_bytes(),before)

    def test_lifecycle_start_close_and_dirty_hint_have_real_receipts(self):
        code,out=self.run_tool('lifecycle.py','start')
        self.assertEqual(code,0,out)
        p=self.root/'.sett-cache/context.json'
        stamp=p.stat().st_mtime_ns
        code,out=self.run_tool('lifecycle.py','changed')
        self.assertEqual(code,0,out)
        self.assertEqual(p.stat().st_mtime_ns,stamp)
        code,out=self.run_tool('lifecycle.py','close')
        self.assertEqual(code,0,out)
        self.assertEqual(p.stat().st_mtime_ns,stamp)
        code,out=self.run_tool('lifecycle.py','status')
        self.assertEqual(code,0,out)
        self.assertIn('start',out)
        self.assertIn('close',out)
        self.assertIn('observed',out)

    def test_lifecycle_close_reports_new_orphan(self):
        self.assertEqual(self.run_tool('lifecycle.py','start')[0],0)
        p=self.knowledge('unlinked')
        door=self.root/'workspace/AGENTS.md'
        door.write_text(door.read_text().replace('- [unlinked](40_knowledge/unlinked.md)',''))
        code,out=self.run_tool('lifecycle.py','close')
        self.assertNotEqual(code,0,out)
        self.assertIn('orphan',out)

if __name__=='__main__':
    unittest.main()
