#!/usr/bin/env python3
"""Validate exactly the Git index before commit, never a working-tree substitute.

Scrub and immutable-journal checks run against the original index first. Then
materialize that same index in an isolated temporary repository and run the
metadata, graph, and neutrality gates there. No private store is copied.
"""
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
LOCATION_VARS=('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_PREFIX','GIT_COMMON_DIR',
               'GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES')


def git(*args):
    p=subprocess.run(['git',*args],cwd=ROOT,capture_output=True)
    if p.returncode:
        raise ValueError('Cannot read the Git index.')
    return p.stdout


def snapshot(destination):
    records=[]
    for row in git('ls-files','--stage','-z').split(b'\0'):
        if not row: continue
        head,raw=row.split(b'\t',1)
        mode,oid,stage=head.split()
        rel=os.fsdecode(raw)
        path=PurePosixPath(rel)
        if stage!=b'0' or path.is_absolute() or '..' in path.parts or '.git' in path.parts:
            raise ValueError('Unmerged or unsafe index path; commit refused.')
        if mode not in {b'100644',b'100755',b'120000'}:
            raise ValueError('Unsupported index entry (submodules require a separate workspace).')
        records.append((mode,oid,rel))
    if not records:
        raise ValueError('Cannot validate an empty index.')
    links={rel for mode,_,rel in records if mode==b'120000'}
    for mode,oid,rel in records:
        parts=PurePosixPath(rel).parts
        if any('/'.join(parts[:i]) in links for i in range(1,len(parts))):
            raise ValueError('Index file is nested beneath a symlink; commit refused.')
        p=destination/rel
        p.parent.mkdir(parents=True,exist_ok=True)
        blob=git('cat-file','blob',oid.decode())
        if mode==b'120000':
            target=os.fsdecode(blob)
            try: (p.parent/target).resolve().relative_to(destination.resolve())
            except (ValueError,OSError):
                raise ValueError('Index symlink leaves the workspace; commit refused.')
            os.symlink(target,p)
        else:
            p.write_bytes(blob)
            p.chmod(0o755 if mode==b'100755' else 0o644)


def main():
    for name,args in [('scrub_check.py',['--staged']),('journal_guard.py',['--staged'])]:
        p=subprocess.run([sys.executable,str(ROOT/'tools'/name),*args],cwd=ROOT)
        if p.returncode: return 1
    try:
        with tempfile.TemporaryDirectory(prefix='workspace-index-') as tmp:
            root=Path(tmp)
            snapshot(root)
            env=os.environ.copy()
            for name in LOCATION_VARS: env.pop(name,None)
            subprocess.run(['git','init','-q'],cwd=root,env=env,check=True,capture_output=True)
            for name,args in [('build_catalog.py',['--check']),('check_loop.py',[]),('pipeline.py',['check']),('agnostic_check.py',[])]:
                tool=root/'tools'/name
                if not tool.is_file():
                    raise ValueError('A required gate is absent from the staged snapshot.')
                p=subprocess.run([sys.executable,str(tool),*args],cwd=root,env=env)
                if p.returncode: return 1
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        print(f'check_staged: {exc}',file=sys.stderr)
        return 1
    return 0

if __name__=='__main__': sys.exit(main())
