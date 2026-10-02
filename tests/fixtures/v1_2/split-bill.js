function solve({people, expenses}) {
  const balances = people.map(() => 0);
  for (const e of expenses) {
    const total = e.shares.reduce((s,x) => s+x.weight,0), n = Math.abs(e.cents);
    const shares = e.shares.map(x => ({i:people.indexOf(x.person), cents:Math.floor(n*x.weight/total), remainder:n*x.weight%total}));
    let spare = n-shares.reduce((s,x)=>s+x.cents,0);
    shares.sort((a,b)=>b.remainder-a.remainder || a.i-b.i);
    for (let i=0;i<spare;i++) shares[i].cents++;
    balances[people.indexOf(e.paidBy)] += e.cents;
    for (const x of shares) balances[x.i] -= Math.sign(e.cents)*x.cents;
  }
  const remaining = [...balances], transfers=[];
  let debtor=0,creditor=0;
  while (true) {
    while (debtor<people.length && remaining[debtor]>=0) debtor++;
    while (creditor<people.length && remaining[creditor]<=0) creditor++;
    if (debtor===people.length || creditor===people.length) break;
    const cents=Math.min(-remaining[debtor],remaining[creditor]);
    transfers.push({from:people[debtor],to:people[creditor],cents});
    remaining[debtor]+=cents; remaining[creditor]-=cents;
  }
  return {balances,transfers};
}
