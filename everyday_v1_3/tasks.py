"""Public, deterministic cases. Version 1.2 inputs remain unchanged."""
from everyday_v1_2.tasks import COMMON, TASKS as TASKS_12, CASES as CASES_12, case

HARD_TASKS = [
 dict(id='build-plan',title='Plan a dependency build',
      description='Resolve a dependency graph, detect cycles, and find the critical path without enumerating every path.',
      example='Two prerequisites run in parallel. The build time follows the longest chain, not the sum of every job.',
      contract='''Input: {jobs: {id: string, duration: nonnegative integer, deps: string[]}[], targets: string[]}. There are at most 240 jobs and 1000 dependency entries. IDs are unique strings of 1 to 24 ASCII letters, digits, or underscores. Every dependency and target names an existing job; repeated dependencies or targets have no extra effect. Ignore jobs not needed by a target, including any cycles in that ignored region. Required jobs are the targets and all their transitive dependencies. If the required graph has a cycle, return {error:"cycle"}. Otherwise return {order:string[], finish:integer, criticalPath:string[]}. order is the lexicographically smallest valid topological ordering of all required IDs: repeatedly take the smallest currently ready ID, not a whole batch. Jobs may execute with unlimited parallel workers; each starts as soon as all its dependencies finish. finish is the earliest time all targets are finished. criticalPath is a dependency chain starting at a dependency-free job and ending at any target with total duration equal to finish; choose the lexicographically smallest ID sequence among tied chains. Compare sequences element-by-element using ASCII order, with a proper prefix smaller than its extension. Empty targets returns {order:[],finish:0,criticalPath:[]}. Do not enumerate all paths: the case set includes a layered graph with exponentially many dependency paths. Times fit safe integers.'''),
 dict(id='job-selection',title='Choose the best jobs',
      description='Find the most profitable schedule under a budget, with cooldowns and deterministic tie-breaking.',
      example='Taking the highest-paying job can earn less than taking two compatible smaller jobs.',
      contract='''Input: {jobs:{id:string,start:integer,end:integer,profit:integer,cost:positive integer}[], budget:nonnegative integer, cooldown:nonnegative integer}. At most 100 jobs; budget <= 80; all times, profits, costs, and cooldown are safe integers of absolute value <= 10000; 0 <= start < end. IDs are unique strings of 1 to 24 ASCII letters, digits, or underscores. Select any subset whose total cost is <= budget and which can be worked by one person: in chronological order, each next.start must be >= previous.end + cooldown. No cooldown is needed before the first or after the last job. Maximize total profit, then minimize total cost, then minimize number of jobs, then choose the lexicographically smallest chronological ID sequence. Compare sequences element-by-element using ASCII order, with a proper prefix smaller than its extension. Returning no jobs is allowed and has profit 0 and cost 0. Return {ids:string[],profit:integer,cost:integer}, with ids in chronological order. Input jobs may be unsorted. Negative and zero profit jobs are valid. Exact optimization is required; greedy selection by profit, earliest finish, or profit/cost is not sufficient. A case with 80 jobs rules out enumerating all subsets under the execution limit.'''),
]
for task in HARD_TASKS:
 task['prompt']=COMMON+'\n\n'+task['contract']
TASKS=HARD_TASKS+[dict(t) for t in TASKS_12]

def job(id,duration,deps=()): return dict(id=id,duration=duration,deps=list(deps))
def build(label,jobs,targets,order=None,finish=0,path=None):
 return case(label,dict(jobs=jobs,targets=targets),dict(error='cycle') if order is None else dict(order=order,finish=finish,criticalPath=path or []))

def paid(id,start,end,profit,cost=1): return dict(id=id,start=start,end=end,profit=profit,cost=cost)
def selection(label,jobs,budget,ids,profit,cost,cooldown=0):
 return case(label,dict(jobs=jobs,budget=budget,cooldown=cooldown),dict(ids=ids,profit=profit,cost=cost))

CASES={**CASES_12,
 'build-plan':[
  build('Parallel prerequisites',[job('compile',4,['fetch','lint']),job('fetch',3),job('lint',5)],['compile'],['fetch','lint','compile'],9,['lint','compile']),
  build('A chain in shuffled order',[job('ship',3,['test']),job('test',4,['build']),job('build',2)],['ship'],['build','test','ship'],9,['build','test','ship']),
  build('Newly ready IDs take priority',[job('Z',2),job('B',1),job('A',1,['B'])],['A','Z'],['B','A','Z'],2,['B','A']),
  build('Shared prerequisite runs once',[job('A',2),job('B',3,['A']),job('C',5,['A']),job('D',1,['B','C'])],['D'],['A','B','C','D'],8,['A','C','D']),
  build('Tied critical paths',[job('B',3),job('A',3),job('C',2,['B','A'])],['C'],['A','B','C'],5,['A','C']),
  build('Only requested targets matter',[job('A',2),job('B',3,['A']),job('unused',9999)],['B'],['A','B'],5,['A','B']),
  build('Ignore an unrelated cycle',[job('A',2),job('X',1,['Y']),job('Y',1,['X'])],['A'],['A'],2,['A']),
  build('A required cycle',[job('A',1,['B']),job('B',1,['A'])],['A']),
  build('Self dependency',[job('A',1,['A'])],['A']),
  build('Duplicate edges and zero-duration detour',[job('__proto__',0),job('constructor',0,['__proto__','__proto__']),job('z',0,['__proto__','constructor'])],['z','z'],['__proto__','constructor','z'],0,['__proto__','constructor','z']),
  build('No targets',[job('X',1,['X'])],[],[],0,[]),
  build('Forty layers of shared dependencies',
        [job(f'{i:02}{letter}',1,[] if i==0 else [f'{i-1:02}a',f'{i-1:02}b']) for i in reversed(range(40)) for letter in ['b','a']],
        ['39b','39a'],[f'{i:02}{letter}' for i in range(40) for letter in ['a','b']],40,[f'{i:02}a' for i in range(40)]),
 ],
 'job-selection':[
  selection('Two smaller jobs beat one big job',[paid('big',0,10,10),paid('early',0,5,6),paid('late',5,10,6)],2,['early','late'],12,2),
  selection('Budget changes the winner',[paid('big',0,10,10,1),paid('early',0,5,6),paid('late',5,10,6)],1,['big'],10,1),
  selection('Profit per dollar is a trap',[paid('cheap',0,10,6,1),paid('best',0,10,10,2)],2,['best'],10,2),
  selection('Cooldown prevents a close pairing',[paid('A',0,5,7),paid('B',5,10,8),paid('C',6,10,6)],2,['A','C'],13,2,1),
  selection('Cooldown boundary is allowed',[paid('B',7,10,6),paid('A',0,5,7)],2,['A','B'],13,2,2),
  selection('Equal profit prefers lower cost',[paid('A',0,10,10,2),paid('B',0,10,10,1)],2,['B'],10,1),
  selection('Then prefer fewer jobs',[paid('A',0,5,5),paid('B',5,10,5),paid('Z',0,10,10,2)],2,['Z'],10,2),
  selection('Then compare the whole ID sequence',[paid('z',0,2,5),paid('a',2,4,5),paid('m',0,1,5),paid('b',1,4,5)],2,['m','a'],10,2),
  selection('Do not buy zero or negative profit',[paid('loss',0,1,-5),paid('zero',1,2,0),paid('gain',2,3,4)],3,['gain'],4,1),
  selection('No budget',[paid('A',0,1,10)],0,[],0,0),
  selection('No jobs',[],80,[],0,0),
  selection('Eighty jobs; exact budgeted optimum',[paid(f'j{i:03}',i*2,i*2+1,1) for i in reversed(range(80))],40,[f'j{i:03}' for i in range(40)],40,40),
 ]}
