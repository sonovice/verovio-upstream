#!/usr/bin/env python3
"""Generate a public, synthetic two-staff score for render benchmarks (no third-party score data)."""
from pathlib import Path
import sys
from xml.etree import ElementTree as ET
M='http://www.music-encoding.org/ns/mei'; X='{http://www.w3.org/XML/1998/namespace}'
ET.register_namespace('',M)
def add(parent,tag,**attrs):return ET.SubElement(parent,'{'+M+'}'+tag,{k.replace('_','.'):str(v) for k,v in attrs.items()})
def make(count,path):
 root=ET.Element('{'+M+'}mei',{'meiversion':'5.1'});head=add(root,'meiHead');fd=add(head,'fileDesc');ts=add(fd,'titleStmt');add(ts,'title').text='Synthetic render benchmark';add(fd,'pubStmt')
 score=add(add(add(add(root,'music'),'body'),'mdiv'),'score');sd=add(score,'scoreDef',meter_count=4,meter_unit=4);sg=add(sd,'staffGrp',symbol='brace',bar_thru='true');add(sg,'staffDef',n=1,lines=5,clef_shape='G',clef_line=2);add(sg,'staffDef',n=2,lines=5,clef_shape='F',clef_line=4);section=add(score,'section')
 for m in range(count):
  measure=add(section,'measure',n=m+1)
  for staffn in (1,2):
   layer=add(add(measure,'staff',n=staffn),'layer',n=1)
   for n in range(4):
    note=add(layer,'note',pname='cdefgab'[(m+n)%7],oct=5 if staffn==1 else 3,dur=4);note.set(X+'id',f'n{m}_{staffn}_{n}')
 path.write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True))
if __name__=='__main__':
 out=Path(sys.argv[1] if len(sys.argv)>1 else '.');out.mkdir(parents=True,exist_ok=True)
 for n in (2,14,64):make(n,out/f'benchmark-{n}.mei')
