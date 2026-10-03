"""Validate saved v1.3 evidence before exporting it for the website."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from bench_v1_3 import fingerprint, EFFORT_ORDER, CALL_TIMEOUT_SECONDS, OUTPUT_TOKEN_TARGET, GENERATION_BUDGET_SECONDS
from everyday_v1_3.tasks import TASKS, CASES
from everyday_v1_3.grader import grade

def validate(run):
    assert run['benchmark_version']=='1.3' and run['suite_sha256']==fingerprint(), 'Suite mismatch'
    assert run['source']=='subscription' and run['model'].startswith('codex-cli/'), 'Wrong provider'
    assert run['reasoning_effort']==min(run['supported_efforts'],key=EFFORT_ORDER.index), 'Effort is not lowest'
    assert run['call_timeout_seconds']==CALL_TIMEOUT_SECONDS and run['output_token_target']==OUTPUT_TOKEN_TARGET, 'Budget mismatch'
    assert run['generation_budget_seconds']==GENERATION_BUDGET_SECONDS, 'Total budget mismatch'
    assert run['status'] in ('completed','failed'), 'Unfinished run'
    assert len(run['tasks'])<=len(TASKS)
    for index,row in enumerate(run['tasks']):
        task=TASKS[index]
        assert row['id']==task['id'] and row['prompt']==task['prompt'], 'Task/prompt mismatch'
        if row['status']=='completed':
            assert row['score']==grade(row['id'],row['response']), 'Score mismatch'
        else:
            assert row['score'] is None and row.get('error'), 'Invalid failure evidence'
    if run['status']=='completed':
        assert len(run['tasks'])==5 and all(t['status']=='completed' for t in run['tasks'])
        assert run['score']==dict(passed=sum(t['score']['passed'] for t in run['tasks']),total=60)
    else: assert run['score'] is None and run.get('error'), 'Failed run must be unscored'

def main():
    runs=[]
    for path in sorted((ROOT/'runs/v1.3').glob('*.json')):
        run=json.loads(path.read_text());validate(run)
        runs.append(dict(run,id='v1.3-'+path.stem,artifact=str(path.relative_to(ROOT))))
    data=dict(version='1.3',suiteHash=fingerprint(),tasks=[dict(t,cases=CASES[t['id']]) for t in TASKS],runs=runs)
    (ROOT/'web/data/everyday-v1.3.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    print(f'Exported {len(runs)} attempts and 60 public checks')
if __name__=='__main__':main()
