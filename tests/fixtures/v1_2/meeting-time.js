function solve({window,duration,step,people}) {
 const schedules=people.map(p=>{
  const sorted=p.work.map(([a,b])=>[a-p.offset,b-p.offset]).sort((a,b)=>a[0]-b[0]),work=[];
  for(const span of sorted){const last=work[work.length-1];if(last&&span[0]<=last[1])last[1]=Math.max(last[1],span[1]);else work.push(span);}
  return {work,busy:p.busy.map(([a,b])=>[a-p.offset-p.buffer,b-p.offset+p.buffer])};
 });
 for(let start=window[0];start+duration<=window[1];start+=step){const end=start+duration;
  if(schedules.every(p=>p.work.some(([a,b])=>a<=start&&end<=b)&&p.busy.every(([a,b])=>end<=a||start>=b)))return {start,end};
 }
 return null;
}
