// node check_outputs.mjs /path/to/baseline.mjs /path/to/candidate.mjs
import { readFileSync } from 'node:fs';
import { VerovioToolkit } from 'verovio/esm';
function canonical(xml) {
 const ids = new Map();
 for (const m of xml.matchAll(/(?:xml:)?id="([^"]+)"/g)) if(!ids.has(m[1])) ids.set(m[1],`id${ids.size}`);
 return xml.replace(/[A-Za-z_][\w.-]*/g,s=>ids.get(s)??s)
  .replace(/6\.4\.0-dev-[a-f0-9]+/g,'VERSION')
  .replace(/isodate="[^"]*"/g,'isodate="DATE"');
}
async function outputs(path) {
 const module=await (await import(path)).default(); const result=[];
 for(const measures of [2,14,64]) for(const additional of [false,true]) {
  const tk=new VerovioToolkit(module);
  tk.setOptions({header:'none',footer:'none',scale:40,xmlIdSeed:1,svgAdditionalAttribute:additional?['note@n','note@oct','note@pname']:[]});
  if(!tk.loadData(readFileSync(new URL(`benchmark-${measures}.mei`,import.meta.url),'utf8')))throw Error('loadData');
  result.push(canonical(tk.getMEI()),tk.renderToMIDI());
  for(const pageWidth of [1200,2100]) {
   tk.setOptions({pageWidth,pageHeight:1600,breaks:'smart'});tk.redoLayout();
   for(let p=1;p<=tk.getPageCount();p++)result.push(canonical(tk.renderToSVG(p)));
  }
  tk.destroy();
 }
 return result;
}
const a=await outputs(process.argv[2]),b=await outputs(process.argv[3]);
if(a.length!==b.length)throw Error('page count mismatch');
for(let i=0;i<a.length;i++) if(a[i]!==b[i]) {
 const {writeFileSync}=await import('node:fs');writeFileSync('/tmp/before-output.txt',a[i]);writeFileSync('/tmp/after-output.txt',b[i]);throw Error(`output ${i} differs`);
}
console.log(`${a.length} MEI, MIDI and SVG outputs match (IDs/version/date normalized).`);
