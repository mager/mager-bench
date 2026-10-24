"""Run snapshotted CommonJS modules in QuickJS, with no host bindings."""
import json
from pathlib import PurePosixPath
import quickjs
from .cases import cases

MAX_SOURCE_BYTES = 128 * 1024
MAX_FILES = 24
MEMORY_BYTES = 32 * 1024 * 1024
CPU_SECONDS = 0.5
MAX_OUTPUT_BYTES = 2 * 1024 * 1024


def validate_sources(sources):
    if not isinstance(sources,dict) or 'src/index.js' not in sources or not 1<=len(sources)<=MAX_FILES:
        raise ValueError('Expected 1..24 source files including src/index.js')
    total = 0
    for name,code in sources.items():
        path = PurePosixPath(name)
        if (not isinstance(code,str) or not name.startswith('src/') or path.suffix!='.js'
            or '..' in path.parts or str(path)!=name or '\\' in name):
            raise ValueError('Only normalized relative src/*.js paths are allowed')
        total += len(code.encode())
    if total>MAX_SOURCE_BYTES:
        raise ValueError('Source exceeds 128 KiB')


def equal(actual,expected):
    if type(actual) is not type(expected): return False
    if isinstance(expected,dict): return actual.keys()==expected.keys() and all(equal(actual[k],v) for k,v in expected.items())
    if isinstance(expected,list): return len(actual)==len(expected) and all(equal(a,b) for a,b in zip(actual,expected))
    return actual==expected


def execute(sources,value):
    validate_sources(sources)
    ctx = quickjs.Context()
    ctx.set_memory_limit(MEMORY_BYTES)
    ctx.set_max_stack_size(1024*1024)
    ctx.set_time_limit(CPU_SECONDS)
    # Compile all module factories before executing any submitted code. The source
    # map and module resolver are closure locals, not exposed global host bindings.
    program = '''(function(){
      const serialize=JSON.stringify.bind(JSON), parse=JSON.parse.bind(JSON);
      const factories=Object.create(null), cache=Object.create(null);
      const definitions=%s;
      for(const [path,source] of Object.entries(definitions))
        factories[path]=new Function('require','module','exports',source);
      function load(path){
        if(cache[path])return cache[path].exports;
        if(!factories[path])throw new Error('Unknown local module: '+path);
        const module={exports:{}}; cache[path]=module;
        function require(name){
          if(typeof name!=='string'||!name.startsWith('.'))throw new Error('Only relative imports');
          const parts=path.split('/').slice(0,-1);
          for(const bit of name.split('/')){
            if(bit==='.'||bit==='')continue;
            if(bit==='..'){if(parts.length<=1)throw new Error('Outside src');parts.pop();}
            else parts.push(bit);
          }
          let resolved=parts.join('/');if(!resolved.endsWith('.js'))resolved+='.js';
          return load(resolved);
        }
        factories[path](require,module,module.exports);return module.exports;
      }
      const input=parse(%s), before=serialize(input);
      const output=load('src/index.js').solve(input);
      if(serialize(input)!==before)throw new Error('Input was mutated');
      return serialize(output);
    })()''' % (json.dumps(sources),json.dumps(json.dumps(value)))
    result = ctx.eval(program)
    if not isinstance(result,str) or len(result.encode())>MAX_OUTPUT_BYTES:
        raise ValueError('Output is missing or oversized')
    return json.loads(result)


def grade(task_id,sources,seed,level,phase):
    checks = cases(task_id,seed,level,phase)
    rows = []
    for check in checks:
        row = dict(check)
        try:
            actual = execute(sources,check['input'])
            row.update(actual=actual,passed=equal(actual,check['expected']))
        except (ValueError,TypeError,quickjs.JSException) as exc:
            row.update(actual=None,passed=False,error=str(exc)[:500])
        rows.append(row)
    return dict(passed=sum(row['passed'] for row in rows),total=len(rows),cases=rows)
