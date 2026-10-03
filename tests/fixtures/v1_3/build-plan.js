function solve({jobs,targets}) {
 const byId=new Map(jobs.map(j=>[j.id,j])),needed=new Set(),stack=[...targets];
 while(stack.length){const id=stack.pop();if(!needed.has(id)){needed.add(id);stack.push(...byId.get(id).deps);}}
 const deps=new Map([...needed].map(id=>[id,[...new Set(byId.get(id).deps)]]));
 const left=new Set(needed),order=[],times=new Map(),paths=new Map();
 const cmp=(a,b)=>{for(let i=0;i<Math.min(a.length,b.length);i++){if(a[i]!==b[i])return a[i]<b[i]?-1:1;}return a.length-b.length;};
 while(left.size){
  const ready=[...left].filter(id=>deps.get(id).every(d=>times.has(d))).sort();
  if(!ready.length)return {error:'cycle'};
  const id=ready[0];let time=0,path=[];
  for(const d of deps.get(id)){
   const candidate=[...paths.get(d),id];
   if(times.get(d)>time || (times.get(d)===time && (!path.length || cmp(candidate,path)<0))){time=times.get(d);path=candidate;}
  }
  times.set(id,time+byId.get(id).duration);paths.set(id,path.length?path:[id]);order.push(id);left.delete(id);
 }
 let finish=0,criticalPath=[];
 for(const id of new Set(targets))if(times.get(id)>finish || (times.get(id)===finish&&(!criticalPath.length||cmp(paths.get(id),criticalPath)<0))){finish=times.get(id);criticalPath=paths.get(id);}
 return {order,finish,criticalPath};
}
