"""Public contracts and literal expected outputs. No model judge or hidden tests."""
COMMON = '''Write a synchronous JavaScript function solve(input). Return only JavaScript, without Markdown or exports. Standard ECMAScript only: no filesystem, network, packages, Node globals, timers, or async. Inputs are valid under the contract. Return a JSON-serializable value. Do not mutate built-ins. Each case runs in a fresh QuickJS context with 16 MiB memory and a 100 ms CPU limit. All arithmetic inputs and results fit safe integers. We compare JSON structurally, ignoring object key order but preserving array order. Implement the full contract, not just an example.'''

TASKS = [
 dict(id='split-bill', title='Split a bill', description='Settle shared expenses with weighted shares, refunds, and awkward pennies.',
      example='A $10 bill split three ways leaves one extra cent. Who gets it?',
      contract='''Input: {people: string[], expenses: {paidBy: string, cents: integer, shares: {person: string, weight: positive integer}[]}[]}. People are unique and ordered. All names occur in people. Each expense has unique share recipients, at least one. cents can be negative (a refund) or zero. For each expense, allocate abs(cents) proportional to the weights: floor each exact share, then distribute remaining cents by descending fractional remainder, ties by people order (not shares order). Apply the sign of cents after allocation. Each person's balance = amount paid minus allocated shares; positive means they receive money. Return {balances: integer[], transfers: {from: string, to: string, cents: positive integer}[]}. balances follows people order including zeros. Settle debtors and creditors in people order: transfer min(debt, credit), advance whichever reaches zero, until settled. Do not optimize transaction count or sort by amount.'''),
 dict(id='clean-csv', title='Clean a contact CSV', description='Parse quoted records, merge duplicate contacts, and report rejected rows.',
      example='Two rows use the same email, but one has a newer name and different tags.',
      contract='''Input: {csv: string}. Parse a valid CSV (comma delimiter; LF or CRLF record separator; double-quoted fields may contain commas, line breaks, and escaped double quotes). Preserve embedded line breaks exactly. A trailing record separator does not create an extra record; internal empty records count. CSV may start with one Unicode BOM. The first record is the header: trim and lowercase headers; unique headers include name,email,tags in any order, optionally others. For every following record, trim fields. Reject a record if its field count differs from the header, trimmed name is empty, or email is invalid. Email validity is exactly /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/ after trimming. Lowercase email. Split tags on semicolon, trim and lowercase each, remove empty tags. Merge by normalized email: keep contacts in first accepted appearance order, use the LAST accepted name, union tags in first appearance order with no duplicates. A rejected duplicate does not change a contact. Return {contacts: {name: string, email: string, tags: string[]}[], rejected: integer}. Count each rejected record once. Empty/header-only CSV yields no contacts and zero rejections.'''),
 dict(id='meeting-time', title='Find a meeting time', description='Align time zones, split workdays, busy periods, and recovery buffers.',
      example='One person works UTC+2. Another has a 15-minute buffer after every call.',
      contract='''Input: {window: [start,end], duration: positive integer, step: positive integer, people: {offset: integer, work: [start,end][], busy: [start,end][], buffer: nonnegative integer}[]}. All times are integer minutes on an absolute two-day axis, not clock strings. window uses UTC minutes, 0 <= start < end <= 2880. Every interval is half-open [start,end), with start < end. Per-person work and busy times are LOCAL minutes; convert to UTC by subtracting offset (which can be negative). Intervals may cross midnight, overlap, be unsorted, or fall outside window. Merge overlapping OR touching work intervals; a meeting must fit completely inside their union for every person. Expand each busy interval by that person's buffer on both ends, after conversion. Touching a busy boundary is allowed; overlapping is not. Candidate starts are window[0] + k*step for nonnegative integers k. Return the earliest {start: UTCminute, end: UTCminute} whose entire duration fits window and every person's work and avoids every expanded busy interval; return null if none. Empty people imposes only the window/grid; a person with no work prevents any meeting.'''),
]
for task in TASKS:
    task['prompt'] = COMMON + '\n\n' + task['contract']

def case(label, input, expected):
    return dict(label=label, input=input, expected=expected)

def expense(payer, cents, shares):
    return dict(paidBy=payer, cents=cents, shares=[dict(person=p,weight=w) for p,w in shares])

def bill(label, people, expenses, balances, transfers):
    return case(label,dict(people=people,expenses=expenses),dict(balances=balances,transfers=[dict(from_=a,to=b,cents=c) for a,b,c in transfers]))

CASES = {
 'split-bill': [
  bill('Dinner for two',['Ada','Bo'],[expense('Ada',4200,[('Ada',1),('Bo',1)])],[2100,-2100],[('Bo','Ada',2100)]),
  bill('An extra penny',['A','B','C'],[expense('A',1000,[('A',1),('B',1),('C',1)])],[666,-333,-333],[('B','A',333),('C','A',333)]),
  bill('Weighted shares',['A','B','C'],[expense('B',1000,[('A',1),('B',2),('C',3)])],[-167,667,-500],[('A','B',167),('C','B',500)]),
  bill('Tie uses people order',['A','B','C'],[expense('C',2,[('C',1),('B',1),('A',1)])],[-1,-1,2],[('A','C',1),('B','C',1)]),
  bill('Payer does not participate',['A','B','C'],[expense('A',501,[('B',1),('C',1)])],[501,-251,-250],[('B','A',251),('C','A',250)]),
  bill('Partial refund',['A','B'],[expense('A',1001,[('A',1),('B',1)]),expense('A',-201,[('A',1),('B',1)])],[400,-400],[('B','A',400)]),
  bill('Refund only',['A','B','C'],[expense('B',-5,[('A',1),('C',1)])],[3,-5,2],[('B','A',3),('B','C',2)]),
  bill('Multiple creditors',['A','B','C','D'],[expense('A',80,[('C',1)]),expense('B',50,[('D',1)])],[80,50,-80,-50],[('C','A',80),('D','B',50)]),
  bill('Debtor crosses creditors',['A','B','C'],[expense('A',70,[('C',1)]),expense('B',30,[('C',1)])],[70,30,-100],[('C','A',70),('C','B',30)]),
  bill('Already settled',['A','B'],[expense('A',20,[('A',1),('B',1)]),expense('B',20,[('B',1),('A',1)])],[0,0],[]),
  bill('Empty and zero expenses',['A','B'],[expense('B',0,[('A',3)])],[0,0],[]),
  bill('Largest remainder wins',['A','B','C'],[expense('C',10,[('A',1),('B',2),('C',4)])],[-1,-3,4],[('A','C',1),('B','C',3)]),
 ],
 'clean-csv': [
  case('Trim and normalize',{'csv':'name,email,tags\n Ada , ADA@X.CO , Work ; friend '},{'contacts':[{'name':'Ada','email':'ada@x.co','tags':['work','friend']}],'rejected':0}),
  case('Quoted comma',{'csv':'name,email,tags\n"Bo, Jr.",bo@x.co,team'},{'contacts':[{'name':'Bo, Jr.','email':'bo@x.co','tags':['team']}],'rejected':0}),
  case('Escaped quotes',{'csv':'name,email,tags\n"Ada ""Ace""",a@x.co,'},{'contacts':[{'name':'Ada "Ace"','email':'a@x.co','tags':[]}],'rejected':0}),
  case('Embedded CRLF',{'csv':'name,email,tags\r\n"Ada\r\nLovelace",a@x.co,x\r\n'},{'contacts':[{'name':'Ada\r\nLovelace','email':'a@x.co','tags':['x']}],'rejected':0}),
  case('Merge duplicates',{'csv':'name,email,tags\nAda,A@X.CO,one;two\nAda L,a@x.co,two;THREE'},{'contacts':[{'name':'Ada L','email':'a@x.co','tags':['one','two','three']}],'rejected':0}),
  case('BOM and reordered headers',{'csv':'\ufeff Tags , EMAIL , Name ,extra\nx,a@x.co,Ada,ignored'},{'contacts':[{'name':'Ada','email':'a@x.co','tags':['x']}],'rejected':0}),
  case('Invalid emails',{'csv':'name,email,tags\nA,a@x,\nB,b b@x.co,\nC,c@@x.co,\nD,d@x.co,'},{'contacts':[{'name':'D','email':'d@x.co','tags':[]}],'rejected':3}),
  case('Wrong number of fields',{'csv':'name,email,tags\nA,a@x.co\nB,b@x.co,x,extra\nC,c@x.co,'},{'contacts':[{'name':'C','email':'c@x.co','tags':[]}],'rejected':2}),
  case('Internal blank record',{'csv':'name,email,tags\n\nA,a@x.co,\n'},{'contacts':[{'name':'A','email':'a@x.co','tags':[]}],'rejected':1}),
  case('Rejected duplicate stays rejected',{'csv':'name,email,tags\nA,a@x.co,one\n ,a@x.co,two'},{'contacts':[{'name':'A','email':'a@x.co','tags':['one']}],'rejected':1}),
  case('First appearance order',{'csv':'name,email,tags\nB,b@x.co,;One;one;;\nA,a@x.co,two\nBee,B@X.CO,three'},{'contacts':[{'name':'Bee','email':'b@x.co','tags':['one','three']},{'name':'A','email':'a@x.co','tags':['two']}],'rejected':0}),
  case('Header only',{'csv':'name,email,tags\n'},{'contacts':[],'rejected':0}),
 ],
}
# Convert the reserved Python keyword to the contract's literal JSON key.
for c in CASES['split-bill']:
    for t in c['expected']['transfers']: t['from'] = t.pop('from_')

def person(work, busy=None, offset=0, buffer=0):
    return dict(work=work,busy=busy or [],offset=offset,buffer=buffer)
def meeting(label, people, expected, window=(540,1020), duration=30, step=15):
    return case(label,dict(window=list(window),duration=duration,step=step,people=people),None if expected is None else dict(start=expected,end=expected+duration))
CASES['meeting-time'] = [
 meeting('Open morning',[person([[540,1020]])],540),
 meeting('Different time zones',[person([[660,1140]],offset=120),person([[300,780]],offset=-300)],600),
 meeting('Buffer after a call',[person([[540,1020]],[[540,600]],buffer=15)],615),
 meeting('Busy boundary is allowed',[person([[540,1020]],[[570,600]])],540),
 meeting('Unsorted overlapping busy periods',[person([[540,1020]],[[585,630],[540,600]])],630),
 meeting('Touching work periods merge',[person([[560,590],[540,560]])],540,duration=50),
 meeting('Split workday gap',[person([[540,560],[600,660]])],600),
 meeting('Grid anchored to window',[person([[550,900]])],562,window=(547,700)),
 meeting('No common opening',[person([[540,570]]),person([[570,600]])],None),
 meeting('Across midnight',[person([[1380,1560]],[[1430,1460]],offset=60,buffer=10)],1410,window=(1380,1600),duration=60),
 meeting('Nobody to constrain it',[],540),
 meeting('Missing working hours',[person([])],None),
]
