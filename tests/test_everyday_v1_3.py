"""Independent small exhaustive oracles and deliberate shortcut checks."""
import itertools
import json
import random
import time
import unittest
from pathlib import Path
from unittest.mock import patch
import tempfile
import quickjs
import bench_v1_3 as runner
from everyday_v1_3.tasks import TASKS, CASES
from everyday_v1_3.grader import grade


def source(task):
 version='v1_3' if task in ('build-plan','job-selection') else 'v1_2'
 return Path('tests/fixtures',version,task+'.js').read_text()


def execute(task,input):
 ctx=quickjs.Context();ctx.set_time_limit(.1);ctx.set_memory_limit(16*1024*1024)
 return json.loads(ctx.eval(source(task)+'\nJSON.stringify(solve('+json.dumps(input)+'))'))


def brute_jobs(data):
 best=(0,0,0,())
 jobs=data['jobs']
 for mask in range(1<<len(jobs)):
  chosen=sorted([j for i,j in enumerate(jobs) if mask>>i&1],key=lambda j:(j['start'],j['end'],j['id']))
  cost=sum(j['cost'] for j in chosen)
  if cost>data['budget']:continue
  if any(a['end']+data['cooldown']>b['start'] for a,b in zip(chosen,chosen[1:])):continue
  key=(-sum(j['profit'] for j in chosen),cost,len(chosen),tuple(j['id'] for j in chosen))
  best=min(best,key)
 return dict(ids=list(best[3]),profit=-best[0],cost=best[1])


def brute_graph(data):
 jobs={j['id']:j for j in data['jobs']};needed=set()
 def visit(id):
  if id in needed:return
  needed.add(id)
  for d in jobs[id]['deps']:visit(d)
 for t in data['targets']:visit(t)
 def valid(order):
  seen=set()
  for id in order:
   if not set(jobs[id]['deps'])<=seen:return False
   seen.add(id)
  return True
 orders=(p for p in itertools.permutations(sorted(needed)) if valid(p))
 order=next(orders,None)
 if order is None:return dict(error='cycle')
 def paths(id):
  if not jobs[id]['deps']:return [(jobs[id]['duration'],(id,))]
  return [(time+jobs[id]['duration'],p+(id,)) for d in set(jobs[id]['deps']) for time,p in paths(d)]
 choices=[(-time,p) for id in set(data['targets']) for time,p in paths(id)]
 finish,path=min(choices) if choices else (0,())
 return dict(order=list(order),finish=-finish,criticalPath=list(path))


class HardCodingTests(unittest.TestCase):
 def test_all_five_reference_programs(self):
  self.assertEqual(sum(len(v) for v in CASES.values()),60)
  for t in TASKS:
   result=grade(t['id'],source(t['id']))
   self.assertEqual(result['passed'],12,[c for c in result['cases'] if not c['passed']])
 def test_scheduler_against_exhaustive_oracle(self):
  rng=random.Random(1203)
  for _ in range(80):
   jobs=[]
   for i in range(rng.randrange(1,9)):
    start=rng.randrange(0,12)
    jobs.append(dict(id=chr(65+i),start=start,end=start+rng.randrange(1,6),profit=rng.randrange(-2,10),cost=rng.randrange(1,5)))
   rng.shuffle(jobs)
   data=dict(jobs=jobs,budget=rng.randrange(0,10),cooldown=rng.randrange(0,3))
   self.assertEqual(execute('job-selection',data),brute_jobs(data),data)
 def test_graph_against_all_orders_and_paths(self):
  rng=random.Random(1302)
  for _ in range(60):
   n=rng.randrange(1,7);ids=[chr(65+i) for i in range(n)];rng.shuffle(ids)
   jobs=[dict(id=id,duration=rng.randrange(0,5),deps=[p for p in ids[:i] if rng.random()<.5]) for i,id in enumerate(ids)]
   rng.shuffle(jobs)
   data=dict(jobs=jobs,targets=[id for id in ids if rng.random()<.6])
   self.assertEqual(execute('build-plan',data),brute_graph(data),data)
 def test_prefix_tie_at_targets(self):
  data=dict(jobs=[dict(id='A',duration=0,deps=[]),dict(id='B',duration=0,deps=['A'])],targets=['B','A'])
  self.assertEqual(execute('build-plan',data),dict(order=['A','B'],finish=0,criticalPath=['A']))
 def test_greedy_profit_fails_known_trap(self):
  greedy='''function solve({jobs,budget,cooldown}) {let chosen=[],cost=0,profit=0;
   for(const j of [...jobs].sort((a,b)=>b.profit-a.profit))if(j.profit>0&&cost+j.cost<=budget&&chosen.every(x=>x.end+cooldown<=j.start||j.end+cooldown<=x.start)){chosen.push(j);cost+=j.cost;profit+=j.profit;}
   chosen.sort((a,b)=>a.start-b.start);return {ids:chosen.map(j=>j.id),cost,profit};}'''
  results=grade('job-selection',greedy)
  self.assertFalse(results['cases'][0]['passed'])
  self.assertEqual(results['cases'][0]['actual']['profit'],10)
  self.assertEqual(results['cases'][0]['expected']['profit'],12)
 def test_exponential_graph_walk_exceeds_limit(self):
  slow=source('build-plan').replace('times.set(id,time+byId.get(id).duration);', '''function duration(id){const j=byId.get(id);return j.duration+Math.max(0,...j.deps.map(duration));}times.set(id,duration(id));''')
  result=grade('build-plan',slow)['cases'][-1]
  self.assertFalse(result['passed']);self.assertIn('interrupted',result['error'])
 @patch('providers.has_key',return_value=True)
 @patch('providers.CodexCLIProvider')
 def test_generation_waiting_budget_is_shared(self,provider,login):
  provider.return_value.complete.side_effect=[source(t['id']) for t in TASKS]
  with tempfile.TemporaryDirectory() as temp,patch.object(runner.time,'perf_counter',side_effect=[0,0,80,80,90,170,170,180,260,260,270,300,300,301]):
   output=Path(temp)/'run.json'
   self.assertEqual(runner.run('codex-cli/test',output,'low',['low']),1)
   data=json.loads(output.read_text())
   self.assertIsNone(data['score'])
   self.assertEqual(data['error'],'Total generation waiting budget exhausted')
   self.assertEqual(provider.return_value.complete.call_count,4)


class PublicationTests(unittest.TestCase):
 @patch('providers.has_key',return_value=True)
 @patch('providers.CodexCLIProvider')
 def test_full_run_and_export_validation(self,provider,login):
  import importlib.util
  spec=importlib.util.spec_from_file_location('export_v13','web/scripts/sync-everyday-v1.3-data.py')
  exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
  provider.return_value.complete.side_effect=[source(t['id']) for t in TASKS]
  with tempfile.TemporaryDirectory() as temp:
   output=Path(temp)/'run.json'
   self.assertEqual(runner.run('codex-cli/test',output,'low',['low','high']),0)
   data=json.loads(output.read_text());exporter.validate(data)
   self.assertEqual(data['score'],dict(passed=60,total=60))
   data['generation_budget_seconds']=450
   with self.assertRaises(AssertionError):exporter.validate(data)
 def test_old_fingerprints_are_unchanged(self):
  from bench_v1_1 import suite_fingerprint
  from bench_v1_2 import fingerprint
  self.assertEqual(suite_fingerprint(),'a56a4aadf5b20a319c7a57309608477d9e523da3d99c37a69bb6353f6b16f0c1')
  self.assertEqual(fingerprint(),'476008a7e08dc0604c5c139afc995d6583d76c21a60e67feb0bd7962b8090bcc')

if __name__=='__main__':unittest.main()
