"""Build task repositories and take bounded, symlink-free source snapshots."""
import json
from pathlib import Path
from .tasks import ROOT, prompt
from .cases import cases
from .grader import validate_sources


def prepare(directory,task_id):
    directory = Path(directory)
    (directory/'src').mkdir(parents=True)
    (directory/'test').mkdir()
    files = {
        'package.json': json.dumps(dict(name=task_id,private=True,scripts={'test':'node --test'}),indent=2)+'\n',
        'src/index.js': 'module.exports = require("./engine.js");\n',
        'src/engine.js': (ROOT/'templates'/f'{task_id}.js').read_text(),
        'README.md': '# '+task_id+'\n\nRead WORK_ORDER.md. Run `node --test`. Edit src/ and add tests in test/.\n',
    }
    examples = cases(task_id,0,1,1)[:2]
    files['test/smoke.test.js'] = '''const test=require('node:test');
const assert=require('node:assert/strict');
const {solve}=require('../src/index.js');
const examples=%s;
for(const c of examples)test(c.id,()=>assert.deepStrictEqual(solve(c.input),c.expected));
''' % json.dumps(examples)
    for name,value in files.items():
        (directory/name).write_text(value)
    write_order(directory,task_id,1)
    return {name:value for name,value in files.items() if not name.startswith('src/')}


def write_order(directory,task_id,phase):
    path = Path(directory)/'WORK_ORDER.md'
    if path.is_symlink(): raise ValueError('WORK_ORDER.md must not be a symlink')
    path.write_text(prompt(task_id,phase))


def snapshot(directory):
    root = Path(directory)
    source = root/'src'
    if source.is_symlink() or not source.is_dir(): raise ValueError('src must be a directory')
    files = {}
    for path in source.rglob('*'):
        if path.is_symlink(): raise ValueError('Source symlinks are not allowed')
        if path.is_file():
            if path.stat().st_size>128*1024: raise ValueError('Oversized source file')
            if len(files)>=24: raise ValueError('Too many source files')
            files[path.relative_to(root).as_posix()] = path.read_text()
    validate_sources(files)
    return files


def integrity_errors(directory,locked):
    root = Path(directory)
    errors = []
    for name,expected in locked.items():
        path = root/name
        if any(parent.is_symlink() for parent in [path,*[root/part for part in Path(name).parents if part!=Path('.')]]) or not path.is_file() or path.stat().st_size!=len(expected.encode()) or path.read_text()!=expected:
            errors.append('Protected file changed: '+name)
    return errors
