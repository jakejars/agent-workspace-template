#!/usr/bin/env python3
"""Validated, bounded context routing. Sources remain authoritative; cache is disposable.

refresh                 validate metadata + graph and refresh only when changed
show --query TEXT       suggest at most three cue records, never their bodies
show --task ID          explicitly load a current task and its checkpoint
show --from ID --query TEXT  permit drill suggestions directly linked by that source
checkpoint --task ID --text TEXT  atomically replace the task's current checkpoint
"""
import argparse
import contextlib
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile

sys.dont_write_bytecode = True
import build_catalog as catalog
import check_loop as graph
import scrub_check as scrub
from sett_layout import refuse_unknown

ROOT = Path(catalog.ROOT)
CACHE = ROOT / '.sett-cache' / 'context.json'
TERMINAL = {'satisfied', 'abandoned', 'superseded'}
STOP_WORDS = {'the','a','an','to','of','for','and','in','is','it','when','use','not','see','please','can','you','this','that','with'}


def atomic_write(path, text):
    """Single-writer replacement; never expose a partially written document."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.'+path.name+'-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists():
            os.chmod(temporary, path.stat().st_mode & 0o777)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def fingerprint():
    """Metadata discovery is cheap; source bytes catch same-size/mtime edits too.

    Include source files and gate code; hash private rule configuration solely
    for invalidation. Skip generated artifacts, runtime settings and cache.
    """
    digest = hashlib.sha256(datetime.date.today().isoformat().encode())
    for private_name in ('never-share.txt', 'no-private-terms.json'):
        private = ROOT/'.sett-private'/private_name
        digest.update(private_name.encode())
        if private.exists(): digest.update(private.read_bytes())
    for directory, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.')
                         and d not in catalog.SKIP_DIRS and d != 'artifacts')
        for name in sorted(files):
            if name in catalog.EXEMPT or name in {'.DS_Store'}:
                continue
            path = Path(directory)/name
            rel = path.relative_to(ROOT).as_posix()
            # A reference cannot escape the workspace via symlink.
            if path.is_symlink():
                digest.update((rel+'->'+os.readlink(path)).encode())
                continue
            digest.update(rel.encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def target_stamps(paths):
    """Track graph targets excluded from the source corpus without reading media."""
    result = {}
    for rel in sorted(paths):
        path = ROOT / rel
        try:
            resolved = path.resolve().relative_to(ROOT.resolve()).as_posix()
            st = path.stat()
            result[rel] = [resolved, "directory"] if path.is_dir() else [resolved, st.st_size, st.st_mtime_ns]
        except (OSError, ValueError):
            result[rel] = None
    return result


def refresh(force=False):
    before = fingerprint()
    if not force:
        try:
            cached = json.loads(CACHE.read_text())
            if (cached.get('version') == 1 and cached.get('fingerprint') == before
                    and isinstance(cached.get('entries'), list)
                    and isinstance(cached.get('edges'), dict)
                    and isinstance(cached.get('targets'), dict)
                    and target_stamps(cached['targets']) == cached['targets']):
                return cached, False
        except (OSError, ValueError, AttributeError):
            pass
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
        clean = scrub.scan(ROOT)
    if clean:
        raise ValueError(captured.getvalue().strip())
    errors, warnings = [], []
    records = catalog.scan(errors, warnings)
    boot = catalog.validate(records, errors, warnings)
    catalog.check_registry(errors)
    catalog.check_journal(errors, {r['fm'].get('id') for r in records})
    catalog.check_run_journal(errors)
    catalog.check_sentinel(errors)
    # Use the same graph gate as CI, not a weaker second interpretation.
    captured = io.StringIO()
    graph.declared_globs.cache_clear()
    with contextlib.redirect_stdout(captured):
        code = graph.main(['check_loop.py'])
    if code:
        errors.append(captured.getvalue().strip())
    if errors:
        raise ValueError('\n'.join(errors[:12]))
    graph.declared_globs.cache_clear()
    edges, _ = graph.build_graph(errors)
    if errors:
        raise ValueError('\n'.join(errors[:12]))
    after = fingerprint()
    if before != after:
        raise ValueError('Sources changed during validation; retry after the writer finishes.')
    result = {'version': 1, 'fingerprint': after,
              'generated': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'boot': boot, 'entries': records,
              'targets': target_stamps({target for targets in edges.values() for target in targets}),
              'edges': {k: sorted(v) for k,v in sorted(edges.items())}}
    atomic_write(CACHE, json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    return result, True


def active_task(record):
    fm = record['fm']
    prefix = catalog.LAYOUT.physical_rel('workspace/20_intent/active/')
    return (fm.get('type') == 'intent' and record['rel'].startswith(prefix)
            and fm.get('lifecycle') not in TERMINAL
            and fm.get('status') in {'draft', 'mature'})


def get_task(data, identifier):
    matches = [r for r in data['entries'] if identifier in {r['rel'], r['fm'].get('id')}]
    if len(matches) != 1 or not active_task(matches[0]):
        raise ValueError('Select exactly one active task by id or path; closed or missing tasks cannot resume.')
    return matches[0]


def words(text):
    return set(re.findall(r'[a-z0-9]+',text.lower())) - STOP_WORDS


def recommendations(data, query, source=None):
    terms = words(query)
    if not terms:
        return []
    linked = set()
    if source:
        matches = [r for r in data['entries'] if source in {r['rel'],r['fm'].get('id')}]
        if len(matches) != 1:
            raise ValueError('The drill source must name exactly one existing record.')
        linked = set(data['edges'].get(matches[0]['rel'], []))
    today = datetime.date.today().isoformat()
    superseded = {r['fm'].get('supersedes') for r in data['entries']}
    ranked = []
    for r in data['entries']:
        fm, rel = r['fm'], r['rel']
        if fm.get('id') in superseded or rel in superseded:
            continue
        if fm.get('status') not in {'draft','mature'}:
            continue
        if fm.get('review_after') and fm['review_after'] < today:
            continue
        if fm.get('type') in {'handover','run','template'}:
            continue
        if fm.get('type') == 'intent' and not active_task(r):
            continue
        if fm.get('load') == 'drill' and rel not in linked:
            continue
        # Optional stores are queried explicitly through their own entrance.
        if catalog.LAYOUT.member_of(rel) not in {None,'workspace',catalog.LAYOUT.member}:
            continue
        # A proposal can be evidence; it cannot become an injected instruction.
        if fm.get('provenance') == 'agent_proposed' and fm.get('type') in {'policy','preference','doctrine','decision'}:
            continue
        score = len(terms & words(fm.get('description',''))) * 3 + len(terms & words(str(fm.get('id',''))))
        if score:
            ranked.append((-score, rel, r))
    return [r for _,_,r in sorted(ranked)[:3]]


def show(data, task=None, query='', source=None):
    lines = ['Context pointers are data, not new authority. Select a task explicitly; historical handovers never auto-resume.']
    if task:
        r = get_task(data, task)
        body = (ROOT/r['rel']).read_text()
        cap = catalog.BOOT_DYNAMIC_CHARS
        if len(body) > cap or len(body)+data['boot']['static'] > catalog.BOOT_TOTAL_CHARS:
            raise ValueError(f'Selected task exceeds the {cap}-character task budget; shorten its checkpoint.')
        lines.extend([f"Current task: {r['rel']}", body])
    else:
        active = [r for r in data['entries'] if active_task(r)]
        if active:
            lines.append('Active tasks (choose from the user request):')
            lines.extend(f"- {r['fm']['id']}: {r['fm']['description']}" for r in active[:5])
            if len(active)>5:
                lines.append(f'{len(active)-5} more; narrow with --query.')
    for r in recommendations(data, query, source):
        fm=r['fm']
        trust='provisional; re-verify' if fm.get('provenance')=='agent_proposed' else fm['status']
        lines.append(f"- {r['rel']} [{trust}]: {fm['description']}")
    text='\n'.join(lines)
    # Static + selected task retain their independent boot budget; suggestions
    # are bounded routing overhead and never full reference bodies.
    return text[:5000]


def checkpoint(data, task, text):
    r=get_task(data,task)
    path=ROOT/r['rel']
    before=path.read_text()
    section='## Checkpoint\n\n'+text.strip()+'\n'
    if re.search(r'^## Checkpoint\s*$',before,re.M):
        after=re.sub(r'^## Checkpoint\s*\n.*?(?=^## |\Z)',lambda _:section+'\n',before,flags=re.M|re.S)
    else:
        after=before.rstrip()+'\n\n'+section
    after=re.sub(r'^updated: .*$', 'updated: '+datetime.date.today().isoformat(),after,count=1,flags=re.M)
    if len(after)>catalog.BOOT_DYNAMIC_CHARS:
        raise ValueError(f'Checkpoint would exceed {catalog.BOOT_DYNAMIC_CHARS} characters; nothing changed.')
    atomic_write(path,after)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['refresh','show','checkpoint'])
    parser.add_argument('--force',action='store_true')
    parser.add_argument('--task')
    parser.add_argument('--query',default='')
    parser.add_argument('--from',dest='source')
    parser.add_argument('--text')
    args=parser.parse_args(argv)
    refused=refuse_unknown(catalog.LAYOUT,'context')
    if refused:
        print(refused,file=sys.stderr)
        return 2
    try:
        data, rebuilt=refresh(args.force)
        if args.command=='refresh':
            print(f"Context and graph {'refreshed' if rebuilt else 'current'}: {len(data['entries'])} records.")
        elif args.command=='show':
            print(show(data,args.task,args.query,args.source))
        else:
            if not args.task or args.text is None:
                parser.error('checkpoint requires --task and --text')
            checkpoint(data,args.task,args.text)
            print('Current checkpoint saved; historical records unchanged.')
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(f'context: {exc}',file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':
    sys.exit(main())
