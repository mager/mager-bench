"""No host bindings: QuickJS has no filesystem, process or network APIs."""
import json
import re
import quickjs
from everyday_v1_3.tasks import CASES

MEMORY_BYTES = 16 * 1024 * 1024
CPU_SECONDS = 0.1
MAX_SOURCE_BYTES = 65536

def extract(response):
    source = response.strip()
    match = re.fullmatch(r'```(?:javascript|js)?\s*\n(.*?)\n```', source, re.S)
    if match: source = match.group(1).strip()
    if not source or len(source.encode()) > MAX_SOURCE_BYTES:
        raise ValueError('Empty or oversized response is unscored')
    return source

def equal(actual, expected):
    # JSON booleans must not compare equal to Python integers.
    if type(actual) is not type(expected): return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(equal(actual[k],v) for k,v in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(equal(a,b) for a,b in zip(actual,expected))
    return actual == expected

def grade(task_id, response):
    source = extract(response)
    results = []
    for c in CASES[task_id]:
        ctx = quickjs.Context()
        ctx.set_memory_limit(MEMORY_BYTES)
        ctx.set_max_stack_size(256 * 1024)
        ctx.set_time_limit(CPU_SECONDS)
        # Keep serialization and input outside the submission's lexical scope.
        program = '''(function(){const serialize=JSON.stringify; const input=JSON.parse(%s);
const fn=(function(){%s\n;return solve;})(); return serialize(fn(input));})()''' % (json.dumps(json.dumps(c['input'])), source)
        row = dict(c)
        try:
            encoded = ctx.eval(program)
            if not isinstance(encoded,str) or len(encoded) > MAX_SOURCE_BYTES:
                raise ValueError('Result must be bounded JSON')
            row['actual'] = json.loads(encoded)
            row['passed'] = equal(row['actual'],c['expected'])
        except (quickjs.JSException, ValueError, TypeError) as exc:
            row.update(actual=None,passed=False,error=str(exc)[:500])
        results.append(row)
    return dict(passed=sum(c['passed'] for c in results),total=len(results),cases=results)
