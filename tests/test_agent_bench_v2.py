"""Reference cross-checks, mutation tests, evidence integrity, and runner policy."""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agent_bench_v2.cases import cases
from agent_bench_v2.grader import execute,grade,equal,validate_sources
from agent_bench_v2.oracles import ledger,build,policy
from agent_bench_v2.tasks import TASKS,ROOT,reference_sources,prompt,PHASE_SECONDS,RUN_SECONDS
from agent_bench_v2.runner import command,environment,digest,fingerprint
from agent_bench_v2.workspace import prepare,snapshot,integrity_errors
from agent_bench_v2.evidence import validate


class Contracts(unittest.TestCase):
    def test_reference_oracle_agreement_across_seeds_and_scales(self):
        for task in TASKS:
            for level in (1,3):
                for seed in (0,42,987654):
                    for phase in (1,2):
                        with self.subTest(task=task['id'],level=level,seed=seed,phase=phase):
                            score=grade(task['id'],reference_sources(task['id']),seed,level,phase)
                            self.assertEqual(score['passed'],32,[c for c in score['cases'] if not c['passed']][:1])

    def test_generators_reproducible_and_seed_changes_inputs(self):
        for task in TASKS:
            a=cases(task['id'],123,2,2)
            self.assertEqual(a,cases(task['id'],123,2,2))
            self.assertNotEqual(a,cases(task['id'],124,2,2))
            self.assertEqual(sum(c['group']=='regression' for c in a),8)

    def test_starter_bugs_are_detected_for_each_task(self):
        for task in TASKS:
            source=reference_sources(task['id'])
            source['src/engine.js']=(ROOT/'templates'/f"{task['id']}.js").read_text()
            self.assertLess(grade(task['id'],source,42,1,1)['passed'],32)

    def test_ledger_atomicity_retry_and_versions(self):
        data=dict(balances={'a':5,'b':0},events=[
            dict(id='x',moves=[{'from':'a','to':'b','amount':3},{'from':'a','to':'b','amount':3}]),
            dict(id='x',moves=[{'from':'a','to':'b','amount':2},{'from':'b','to':'a','amount':1}]),
            dict(id='x',moves=[],expected={'a':99}),
        ])
        self.assertEqual(ledger(data),dict(balances={'a':4,'b':1},versions={'a':1,'b':1},receipts=[dict(id='x',status=s) for s in ('rejected','applied','duplicate')]))

    def test_cache_cycle_does_not_partially_commit(self):
        data=dict(nodes=[dict(id='a',deps=[],revision=0),dict(id='b',deps=['a'],revision=0)],requests=[
            dict(targets=['b'],changes=[]),
            dict(targets=['b'],changes=[dict(id='a',revision=1),dict(id='b',deps=['b','a'])]),
            dict(targets=['b'],changes=[dict(id='b',deps=['a'])]),
        ])
        self.assertEqual(build(data),[dict(built=['a','b'],cached=[]),dict(error='cycle',built=[],cached=[]),dict(built=['a','b'],cached=[])])

    def test_policy_expiration_and_cycle_boundaries(self):
        rule=dict(effect='allow',tenant='a',resource='*',action='*',until=10)
        data=dict(roles=[dict(id='r',parents=[],rules=[rule])],users=[dict(id='u',roles=['r'])],queries=[dict(user='u',tenant='a',resource='x',action='r',time=t) for t in (9,10)])
        self.assertEqual(policy(data),['allow','deny'])
        data['roles'][0]['parents']=['r']
        self.assertEqual(policy(data),['deny','deny'])

    def test_mutants_cannot_get_full_scores(self):
        mutations={
            'event-ledger': [('if (accepted.has(e.id))','if (false)'),('balances = next;', 'balances = {...input.balances};')],
            'build-cache': [('cache.get(id).signature === signature','true'),("if (cycle) return {error:'cycle',built:[],cached:[]};","if (cycle) return {built:[],cached:[]};")],
            'access-policy': [("!matched.some(r=>r.effect === 'deny')",'true'),("q.time < r.until","q.time <= r.until"),("if (cycle) return 'deny';",'')],
        }
        for task,pairs in mutations.items():
            for old,new in pairs:
                sources=reference_sources(task)
                self.assertIn(old,sources['src/engine.js'])
                sources['src/engine.js']=sources['src/engine.js'].replace(old,new)
                self.assertLess(grade(task,sources,42,1,2)['passed'],32,(task,old))


class Isolation(unittest.TestCase):
    def test_js_types_and_module_resolution(self):
        self.assertFalse(equal(True,1))
        sources={'src/index.js':'module.exports=require("./nested/a");','src/nested/a.js':'module.exports={solve:()=>42};'}
        self.assertEqual(execute(sources,{}),42)
        with self.assertRaises(ValueError): validate_sources({'src/../index.js':''})

    def test_host_imports_and_input_mutation_fail(self):
        for source in ['module.exports={solve:()=>require("fs")}','module.exports={solve:x=>{x.a=2;return x}}','module.exports={solve:()=>{while(true){}}}']:
            with self.assertRaises(Exception): execute({'src/index.js':source},{'a':1})
        self.assertEqual(execute({'src/index.js':'module.exports={solve:()=>[typeof process,typeof fetch]}'},{}),['undefined','undefined'])

    def test_workspace_integrity_and_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'repo';locked=prepare(root,'event-ledger')
            self.assertEqual(integrity_errors(root,locked),[])
            self.assertIn('src/index.js',snapshot(root))
            (root/'test/smoke.test.js').write_text('')
            self.assertTrue(integrity_errors(root,locked))
            (root/'src/out.js').symlink_to('/etc/passwd')
            with self.assertRaises(ValueError): snapshot(root)

    def test_environment_and_cli_policy(self):
        with patch.dict(os.environ,{'OPENAI_API_KEY':'secret','CODEX_API_KEY':'secret','CODEX_ACCESS_TOKEN':'secret','OPENAI_BASE_URL':'https://example.com','ARBITRARY_SECRET':'secret'}):
            env=environment()
            self.assertFalse(any('KEY' in k or 'TOKEN' in k or 'SECRET' in k or 'BASE_URL' in k for k in env))
        argv=command('codex-cli/example','low',Path('/tmp/repo'),Path('/tmp/out'))
        for flag in ['--ignore-user-config','--ignore-rules','--ephemeral','workspace-write','forced_login_method="chatgpt"','approval_policy="never"','model_provider="openai"']:
            self.assertIn(flag,argv)
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox',argv)


class Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact=dict(benchmark_version='2.0',kind='evaluation',source='chatgpt-subscription',model='codex-cli/fixture',reasoning_effort='low',supported_efforts=['high','low'],seed=42,level=1,suite_sha256=fingerprint(),phase_seconds=PHASE_SECONDS,budget_seconds=RUN_SECONDS,status='completed',elapsed_ms=100,generation_ms=6,tasks=[],score=dict(passed=192,total=192,tasks_passed=3,tasks_total=3))
        for task in TASKS:
            row=dict(id=task['id'],phases=[])
            for phase in (1,2):
                sources=reference_sources(task['id'])
                row['phases'].append(dict(phase=phase,prompt=prompt(task['id'],phase),status='completed',sources=sources,source_sha256=digest(sources),score=grade(task['id'],sources,42,1,phase),events=[{'type':'turn.completed'}],response='fixture, not model evidence',elapsed_ms=1,integrity_errors=[]))
            cls.artifact['tasks'].append(row)

    def test_replay_and_tamper_rejection(self):
        validate(self.artifact)
        for mutate in [lambda a:a.update(suite_sha256='wrong'),lambda a:a.update(reasoning_effort='high'),lambda a:a['score'].update(passed=191),lambda a:a['tasks'][0]['phases'][0]['score'].update(passed=0),lambda a:a['tasks'][0]['phases'][0].update(prompt='wrong'),lambda a:a['tasks'][0]['phases'][0].update(events=[]),lambda a:a['tasks'].reverse(),lambda a:a.update(seed=123)]:
            artifact=deepcopy(self.artifact);mutate(artifact)
            with self.assertRaises(ValueError): validate(artifact)

    def test_failed_runs_remain_unscored(self):
        artifact=deepcopy(self.artifact)
        artifact.update(status='failed',error='provider failed',score=None)
        artifact['tasks']=[]
        validate(artifact)
        artifact['score']=dict(passed=0,total=192)
        with self.assertRaises(ValueError): validate(artifact)


class RunnerFailures(unittest.TestCase):
    def test_auth_failure_saves_unscored_attempt_without_call(self):
        from agent_bench_v2.runner import run
        with tempfile.TemporaryDirectory() as temp, patch('agent_bench_v2.runner.lowest_effort',return_value=('low',['low'])), patch('agent_bench_v2.runner.preflight',side_effect=RuntimeError('ChatGPT login required')), patch('agent_bench_v2.runner.invoke') as call:
            output=Path(temp)/'attempt.json'
            result=run('codex-cli/fixture',output,42,1)
            self.assertEqual(result['status'],'failed')
            self.assertIsNone(result['score'])
            self.assertEqual(json.loads(output.read_text()),result)
            call.assert_not_called()
            validate(result)

    def test_provider_failure_stops_without_retry_and_keeps_source(self):
        from agent_bench_v2.runner import run
        failed=dict(status='failed',error='budget exhausted',elapsed_ms=120000,events=[{'type':'turn.failed'}],response='',stderr='',usage={},command_count=0)
        with tempfile.TemporaryDirectory() as temp, patch('agent_bench_v2.runner.lowest_effort',return_value=('low',['low'])), patch('agent_bench_v2.runner.preflight',return_value={}), patch('agent_bench_v2.runner.invoke',return_value=failed) as call:
            result=run('codex-cli/fixture',Path(temp)/'attempt.json',42,1)
            self.assertEqual(call.call_count,1)
            self.assertIsNone(result['score'])
            self.assertIn('src/index.js',result['tasks'][0]['phases'][0]['sources'])
            validate(result)

    def test_probe_never_becomes_a_score(self):
        from agent_bench_v2.runner import run
        def invoke(model,effort,workspace,directory,phase,timeout):
            (workspace/'probe.txt').write_text('OK')
            return dict(status='completed',elapsed_ms=10,response='OK',events=[{'type':'turn.completed'}])
        with tempfile.TemporaryDirectory() as temp, patch('agent_bench_v2.runner.lowest_effort',return_value=('low',['low'])), patch('agent_bench_v2.runner.preflight',return_value={}), patch('agent_bench_v2.runner.invoke',side_effect=invoke):
            result=run('codex-cli/fixture',Path(temp)/'attempt.json',42,1,smoke=True)
            self.assertEqual(result['status'],'completed')
            self.assertEqual(result['generation_ms'],10)
            self.assertIsNone(result['score'])
            validate(result)
