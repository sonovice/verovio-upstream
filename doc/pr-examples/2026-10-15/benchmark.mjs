// npm install, then: node benchmark.mjs /path/to/verovio-module.mjs --reps 7 --out measurements.json
// The supplied module is built from the revision being measured. The npm package supplies the JS API wrapper.
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { VerovioToolkit } from 'verovio/esm';
const args = process.argv.slice(2), modulePath = args.shift();
const reps = args.includes('--reps') ? Number(args[args.indexOf('--reps')+1]) : 7;
const output = args.includes('--out') ? args[args.indexOf('--out')+1] : 'measurements.json';
const createModule = (await import(modulePath)).default;
const module = await createModule();
const now = () => { const t=process.threadCpuUsage(); return (t.user+t.system)/1000; };
const measure = (times,name,fn) => { const start=now();const result=fn();times[name]=(times[name]??0)+now()-start;return result; };
const results=[];
for (const measures of [2,14,64]) {
 const mei=readFileSync(new URL(`benchmark-${measures}.mei`,import.meta.url),'utf8');
 for (const additional of [false,true]) {
  const runs=[];
  for(let r=0;r<reps;r++) {
   const tk=new VerovioToolkit(module), times={}, start=now();
   tk.setOptions({header:'none',footer:'none',scale:40,xmlIdSeed:1,svgAdditionalAttribute:additional?['note@n','note@oct','note@pname']:[]});
   measure(times,'loadData',()=>tk.loadData(mei));
   for (const pageWidth of [1200,2100]) {
    tk.setOptions({pageWidth,pageHeight:1600,breaks:'smart'});
    measure(times,'redoLayout',()=>tk.redoLayout());
    for(let p=1;p<=tk.getPageCount();p++) measure(times,'renderToSVG',()=>tk.renderToSVG(p));
   }
   times.total=now()-start;runs.push(times);tk.destroy();
  }
  const best=Object.fromEntries(Object.keys(runs[0]).map(k=>[k,Math.min(...runs.map(r=>r[k]))]));
  results.push({measures,additionalAttributes:additional,...best});
 }
}
writeFileSync(output,JSON.stringify(results,null,2)+'\n');
console.log(JSON.stringify(results,null,2));
