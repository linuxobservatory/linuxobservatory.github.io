#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import json,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
PAGES=['/','/about/','/start-here/'];LANGS=['en','da','de','zh-Hans'];BASE='https://linuxobservatory.github.io'
class Page(HTMLParser):
 def __init__(self,s):
  super().__init__();self.tags=[];self.feed(s)
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def attrs(self,t,**kw):return [a for tag,a in self.tags if tag==t and all(a.get(k)==v for k,v in kw.items())]
for lang in LANGS:
 for page in PAGES:
  route=('' if lang=='en' else '/'+lang.lower())+page
  f=ROOT/route.strip('/')/'index.html';s=f.read_text();p=Page(s)
  assert p.attrs('html',lang=lang),f
  assert p.attrs('link',rel='canonical')[0]['href']==BASE+route,f
  alts=p.attrs('link',rel='alternate');langs={a['hreflang']:a['href'] for a in alts if 'hreflang' in a}
  assert set(langs)==set(LANGS+['x-default']),f
  for l in LANGS:assert langs[l]==BASE+('' if l=='en' else '/'+l.lower())+page,f
  schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)[1])
  assert schema['inLanguage']==lang and schema['url']==BASE+route,f
  assert len(p.attrs('a',**{'data-language':lang,'aria-current':'page'}))==1,f
  assert len([a for t,a in p.tags if t=='a' and 'data-language' in a])==4,f
  # All local resources and destination pages exist; fragment targets also exist.
  for tag,a in p.tags:
   value=a.get('src') if tag=='script' or tag=='img' else a.get('href') if tag in ['a','link'] else None
   if not value or not value.startswith('/') or value.startswith('//'):continue
   path=value.split('#')[0].split('?')[0];dest=ROOT/path.lstrip('/')
   if path.endswith('/'):dest=dest/'index.html'
   assert dest.exists(),(f,value)
   if '#' in value:
    fragment=value.split('#')[1];target=Page(dest.read_text())
    assert any(at.get('id')==fragment for _,at in target.tags),(f,value)
  # Assets, external destinations and metrics must agree with the English source.
  en=Page((ROOT/page.strip('/')/'index.html').read_text())
  assert [a['src'] for t,a in p.tags if t=='img']==[a['src'] for t,a in en.tags if t=='img'],f
  assert [a['href'] for t,a in p.tags if t=='a' and a.get('href','').startswith('https://')]==[a['href'] for t,a in en.tags if t=='a' and a.get('href','').startswith('https://')],f
  if page=='/':
   for value in ['32K VSR','Gallium_HUD','17.6 ms','data-fps>60','data-latest-grid','href="#latest-videos"','id="latest-videos"']:
    assert value in s,(f,value)
  assert BASE+route in (ROOT/'sitemap.xml').read_text(),f
# Regeneration is deterministic.
paths=[ROOT/('' if l=='en' else l.lower())/p.strip('/')/'index.html' for l in LANGS for p in PAGES]+[ROOT/'sitemap.xml',ROOT/'sitemap.txt']
before={p:p.read_bytes() for p in paths}
subprocess.run(['python3',str(ROOT/'scripts/build-translations.py')],check=True)
assert all(p.read_bytes()==v for p,v in before.items()),'Non-deterministic generator'
print('PASS: 12 pages, reciprocal hreflang, schema, canonical URLs, local links and fragments, assets, metrics, English content, deterministic generation.')
