function solve({csv}) {
 csv=csv.replace(/^\uFEFF/,'');
 if (!csv) return {contacts:[],rejected:0};
 const rows=[];let row=[],field='',quoted=false,ended=false;
 for(let i=0;i<csv.length;i++) {
  const c=csv[i]; ended=false;
  if(c==='"') {if(quoted && csv[i+1]==='"'){field+='"';i++;}else quoted=!quoted;}
  else if(!quoted && c===','){row.push(field);field='';}
  else if(!quoted && (c==='\r'||c==='\n')){row.push(field);rows.push(row);row=[];field='';if(c==='\r'&&csv[i+1]==='\n')i++;ended=true;}
  else field+=c;
 }
 if(!ended){row.push(field);rows.push(row);}
 const headers=rows.shift().map(x=>x.trim().toLowerCase()),contacts=[],lookup=new Map();let rejected=0;
 for(const r of rows){
  const cells=r.map(x=>x.trim()),name=cells[headers.indexOf('name')],email=(cells[headers.indexOf('email')]||'').toLowerCase();
  if(r.length!==headers.length || !name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)){rejected++;continue;}
  const tags=cells[headers.indexOf('tags')].split(';').map(x=>x.trim().toLowerCase()).filter(Boolean);
  let c=lookup.get(email);
  if(!c){c={name,email,tags:[]};lookup.set(email,c);contacts.push(c);}
  c.name=name;for(const tag of tags)if(!c.tags.includes(tag))c.tags.push(tag);
 }
 return {contacts,rejected};
}
