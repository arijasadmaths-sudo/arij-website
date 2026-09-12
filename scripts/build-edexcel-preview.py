#!/usr/bin/env python3
"""Create a self-contained review of the exact draft pages; no deployment."""
from pathlib import Path
import re,json,base64
ROOT=Path(__file__).resolve().parents[1]
HOME='edexcel-textbook-companions.html'
ORDER=[(HOME,'Overview'),('edexcel-pure-year-1.html','Pure Year 1'),('edexcel-pure-year-2.html','Pure Year 2'),('edexcel-statistics-mechanics-year-1.html','Statistics & Mechanics Year 1'),('edexcel-statistics-mechanics-year-2.html','Statistics & Mechanics Year 2'),('edexcel-core-pure-1.html','Core Pure 1'),('edexcel-core-pure-2.html','Core Pure 2'),('resources.html','Resources page')]
data={'home':HOME,'pages':{},'downloads':{}}
for path,label in ORDER:
 text=(ROOT/path).read_text();body=re.search(r'<body([^>]*)>(.*?)</body>',text,re.S)
 body_class=re.search(r'class="([^"]*)"',body[1])[1]
 html=re.sub(r'<script\b[^>]*>.*?</script>','',body[2],flags=re.S)
 data['pages'][path]={'label':label,'bodyClass':body_class,'html':html}
for p in (ROOT/'assets/textbook-practice').glob('*'):
 if p.suffix in ['.pdf','.zip']:
  data['downloads'][p.relative_to(ROOT).as_posix()]={'type':'application/pdf' if p.suffix=='.pdf' else 'application/zip','data':base64.b64encode(p.read_bytes()).decode()}
css='\n'.join((ROOT/p).read_text() for p in ['site.css','topic-practice.css','paper-navigation.css','textbook-companions.css'])
css=css.replace(':root {','#edexcel-review {')
fragment=(ROOT/'scripts/edexcel-preview-template.html').read_text().replace('/* REVIEW_STYLES */',css).replace('REVIEW_DATA',json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/'))
if len(fragment.encode())>=1000000: raise RuntimeError(f'Preview fragment too large: {len(fragment.encode())}')
Path('/workspace/edexcel-companions-review.html').write_text(fragment)
review=ROOT/'.review';review.mkdir(exist_ok=True)
(review/'edexcel-preview.html').write_text('<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Edexcel companions — draft preview</title><style>body{margin:0}</style></head><body>'+fragment+'</body></html>')
print('Preview bytes:',len(fragment.encode()),'; pages:',len(data['pages']),'; embedded downloads:',len(data['downloads']))
