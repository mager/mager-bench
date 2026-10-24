// Current transfer handler. Receipts and versions are part of the public API.
function solve(input) {
  const balances={...input.balances};
  const versions=Object.fromEntries(Object.keys(balances).map(k=>[k,0]));
  const receipts=input.events.map(e=>{
    if(balances[e.from]<e.amount)return {id:e.id,status:'rejected'};
    balances[e.from]-=e.amount;balances[e.to]+=e.amount;
    versions[e.from]++;versions[e.to]++;
    return {id:e.id,status:'applied'};
  });
  return {balances,versions,receipts};
}
module.exports={solve};
