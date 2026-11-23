#!/usr/bin/env python3
"""Regenerate static translations using English pages as layout/content sources.
Run from any directory: python3 scripts/build-translations.py
Edit translations/*.json when English copy changes. No third-party dependencies.
"""
from pathlib import Path
from html import escape, unescape
from html.parser import HTMLParser
import json, re
ROOT=Path(__file__).resolve().parents[1]
BASE='https://linuxobservatory.github.io'
PAGES=['/','/about/','/start-here/']
LANGS={'en':'English','da':'Dansk','de':'Deutsch','zh-Hans':'简体中文'}
LOCALES={'en':'en_US','da':'da_DK','de':'de_DE','zh-Hans':'zh_CN'}

def url(lang,page): return ('' if lang=='en' else '/'+lang.lower())+page

def clean(s): return re.sub(r'<!-- i18n:start -->.*?<!-- i18n:end -->','',s,flags=re.S)

def block(s): return '<!-- i18n:start -->'+s+'<!-- i18n:end -->'

class Translate(HTMLParser):
 def __init__(self,mapping,lang):
  super().__init__(convert_charrefs=False); self.mapping=mapping; self.lang=lang; self.out=[]; self.skip=False
 def value(self,v): return self.mapping.get(v.strip(),v.strip())
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style'): self.skip=True
  new=[]
  for k,v in attrs:
   if v is not None:
    if k in ('alt','aria-label','title','data-watch-label','data-error-label') or (tag=='meta' and k=='content'): v=self.value(v)
    if k=='href' and v in PAGES: v=url(self.lang,v)
    if tag=='html' and k=='lang': v=self.lang
   new.append(k if v is None else k+'="'+escape(v,quote=True)+'"')
  self.out.append('<'+tag+(' '+' '.join(new) if new else '')+'>')
 def handle_startendtag(self,tag,attrs):
  self.handle_starttag(tag,attrs);self.out[-1]=self.out[-1][:-1]+'/>'
 def handle_endtag(self,tag):
  self.out.append('</'+tag+'>')
  if tag in ('script','style'):self.skip=False
 def handle_data(self,s):
  if self.skip or not s.strip():self.out.append(s);return
  self.out.append(s[:len(s)-len(s.lstrip())]+escape(self.value(s),quote=False)+s[len(s.rstrip()):])
 def handle_entityref(self,n):self.out.append('&'+n+';')
 def handle_charref(self,n):self.out.append('&#'+n+';')
 def handle_decl(self,d):self.out.append('<!'+d+'>')
 def handle_comment(self,d):self.out.append('<!--'+d+'-->')

# English is the source of truth. Localized content is rendered at build time,
# so it is readable and indexable without JavaScript.
for index,page in enumerate(PAGES):
 source=ROOT/(page.strip('/')+'/' if page!='/' else '')/'index.html'
 original=clean(source.read_text())
 original=original.replace('/assets/site.js?v=20261111','/assets/site.js?v=20261117-i18n')
 # Translate complete text nodes, including entity references in English copy.
 for lang in LANGS:
  data={} if lang=='en' else json.loads((ROOT/'translations'/f'{lang.lower()}.json').read_text())
  result=original
  if lang!='en':
   # Resolve entities in text before parsing so compound text (e.g. Contact & attribution) stays together.
   class Joined(Translate):
    def __init__(self,mapping,lang):
     super().__init__(mapping,lang);self.convert_charrefs=True
   parser=Joined(data['strings'],lang);parser.feed(original); result=''.join(parser.out)
  canonical=BASE+url(lang,page)
  title=re.search(r'<title>(.*?)</title>',result,re.S).group(1)
  description=(re.search(r'<meta name="description" content="(.*?)"',original).group(1) if lang=='en' else data['descriptions'][index])
  for key in ['description','og:description','twitter:description']:
   result=re.sub(r'(<meta (?:name|property)="'+key+r'" content=")[^"]*',lambda m:m[1]+escape(unescape(description),quote=True),result)
  result=re.sub(r'(<link rel="canonical" href=")[^"]*',lambda m:m[1]+canonical,result)
  result=re.sub(r'(<meta property="og:url" content=")[^"]*',lambda m:m[1]+canonical,result)
  if lang!='en':
   result=re.sub(r'(<meta property="og:image:alt" content=")[^"]*',lambda m:m[1]+data['image'],result)
  def schema(m):
   d=json.loads(m[1]);d.update(name=unescape(title),description=unescape(description),url=canonical,inLanguage=lang)
   return '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False)+'</script>'
  result=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,result,flags=re.S)
  head='\n'+''.join(f'<link rel="alternate" hreflang="{l}" href="{BASE+url(l,page)}">\n' for l in LANGS)
  head+=f'<link rel="alternate" hreflang="x-default" href="{BASE+page}">\n<meta property="og:locale" content="{LOCALES[lang]}">\n'
  head+=''.join(f'<meta property="og:locale:alternate" content="{LOCALES[l]}">\n' for l in LANGS if l!=lang)
  head+='<link rel="stylesheet" href="/assets/languages.css?v=20261117">\n<script src="/assets/languages.js?v=20261117"></script>\n'
  result=result.replace('</head>',block(head)+'</head>')
  label=data.get('label','Language')
  nav=f'<nav class="language-nav" aria-label="{label}"><div class="shell language-inner"><span>{label}</span>'
  for l,name in LANGS.items():
   current=' aria-current="page"' if l==lang else ''
   nav+=f'<a href="{url(l,page)}" lang="{l}" hreflang="{l}" data-language="{l}"{current}>{name}</a>'
  nav+='</div></nav>'
  result=result.replace('</header>','</header>'+block(nav),1)
  if lang!='en':
   result=result.replace('<footer class="site-footer">',block('<div class="shell language-note"><p>'+data['note']+'</p></div>')+'<footer class="site-footer">')
   # Supply localized strings to the original interaction code, without altering metrics.
   result=result.replace('<body ', '<body data-nav-open="'+escape(data['open'],quote=True)+'" data-nav-close="'+escape(data['close'],quote=True)+'" ',1)
   result=result.replace('data-frame-demo>', 'data-frame-demo data-smooth="'+escape(data['smooth'],quote=True)+'" data-jitter="'+escape(data['jitter'],quote=True)+'">')
  dest=ROOT/url(lang,page).strip('/')/'index.html'
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(result)
# Preserve existing sitemap entries and Jekyll's dynamic blog loop.
sitemap=ROOT/'sitemap.xml'; xml=clean(sitemap.read_text())
xml=xml.replace('</urlset>',block('\n'+''.join(f'  <url><loc>{BASE+url(l,p)}</loc></url>\n' for l in LANGS if l!='en' for p in PAGES))+'</urlset>')
sitemap.write_text(xml)
txt=ROOT/'sitemap.txt';existing=txt.read_text().splitlines()
for l in LANGS:
 for p in PAGES:
  entry=BASE+url(l,p)
  if entry not in existing:existing.append(entry)
txt.write_text('\n'.join(existing)+'\n')
print('Generated 12 static pages and updated both sitemaps.')
