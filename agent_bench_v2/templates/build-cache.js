// Cache currently keys only on a node's own revision.
function solve(input) {
  const nodes=new Map(input.nodes.map(n=>[n.id,{...n}])), cache=new Map();
  return input.requests.map(r=>{
    r.changes.forEach(c=>Object.assign(nodes.get(c.id),c));
    const needed=new Set();
    function visit(id){if(needed.has(id))return;needed.add(id);nodes.get(id).deps.forEach(visit);}
    r.targets.forEach(visit);
    const built=[],cached=[];
    for(const id of [...needed].sort()){
      const n=nodes.get(id);
      if(cache.get(id)===n.revision)cached.push(id);
      else {cache.set(id,n.revision);built.push(id);}
    }
    return {built,cached};
  });
}
module.exports={solve};
