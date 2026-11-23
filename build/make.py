import re, base64, io
from PIL import Image

SRC='images/logo.png'
im=Image.open(SRC).convert('RGBA')

def data_uri(img):
    b=io.BytesIO(); img.save(b,'PNG',optimize=True)
    return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()

# square-pad then resize
w,h=im.size; s=max(w,h)
sq=Image.new('RGBA',(s,s),(0,0,0,0)); sq.paste(im,((s-w)//2,(s-h)//2))
logo=data_uri(sq.resize((136,136),Image.LANCZOS))
ic=Image.open('images/favicon-source.png').convert('RGBA')
fav=data_uri(ic.resize((64,64),Image.LANCZOS))
apple=data_uri(ic.resize((180,180),Image.LANCZOS))

# ---- SINGLE SOURCE OF TRUTH: edit here, rebuild ----
CFG={
 'SUN_TIME':'10:45 AM',
 'WED_TIME':'6:00&ndash;7:30 PM',
 'MON_TIME':'6:00 PM',
 'PHONE':'430.808.2655',
 'PHONE_TEL':'+14308082655',
 'LOGO_HEADER':logo,'FAV':fav,'APPLE':apple,
}

t=open('template_prev.html',encoding='utf-8').read()

# logo
t=re.sub(r'<!-- STAND-IN LOGO.*?</svg>','<img class="logo" src="{{LOGO_HEADER}}" alt="" width="52" height="52">',t,flags=re.S,count=1)
t=t.replace(".brand svg{width:48px;height:48px;flex:none;filter:drop-shadow(0 2px 8px rgba(0,0,0,.2));}",
 ".brand img{width:52px;height:52px;flex:none;display:block;filter:drop-shadow(0 2px 8px rgba(0,0,0,.25));}")
# menu bug: header must sit above the full-screen menu
t=t.replace("z-index:100;height:84px","z-index:200;height:84px")
t=t.replace("backdrop-filter:blur(10px);border-color","-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);border-color")
# tagline legibility
t=t.replace("font-size:.6rem;letter-spacing:.2em;font-family:var(--sans)","font-size:.66rem;letter-spacing:.12em;font-family:var(--sans)")
t=t.replace("  @media (max-width:960px){nav.links{display:none;}",
 "  @media (max-width:520px){.brand-word b{display:none;}.brand-word{font-size:1.25rem;}}\n  @media (max-width:960px){nav.links{display:none;}",1)
# head: favicon, theme color
t=t.replace('<meta name="description"','<meta name="theme-color" content="#02027D">\n<link rel="icon" type="image/png" href="{{FAV}}">\n<link rel="apple-touch-icon" href="{{APPLE}}">\n<meta name="description"',1)
# structured data: only what is verified
t=re.sub(r'<script type="application/ld\+json">.*?</script>','''<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Church","name":"Prairie Valley Church","telephone":"+1-430-808-2655","alternateName":"Prairie Valley Baptist Church","address":{"@type":"PostalAddress","streetAddress":"2417 FM 513","addressLocality":"Campbell","addressRegion":"TX","postalCode":"75422","addressCountry":"US"}}
</script>''',t,flags=re.S,count=1)
# dead-end groups button
t=re.sub(r'\s*<div style="margin-top:34px" class="reveal"><a class="btn" href="https://pvbchurch.churchcenter.com/groups".*?</div>','',t,flags=re.S,count=1)
# filler tile
t=t.replace("<div><b>Men's Prayer Meeting</b><span>Check the calendar for the current day and time</span></div>",
            "<div><b>Everything else</b><span>Special events and schedule changes are always on the full calendar</span></div>")
t=t.replace(">Church Center</a>",">Open Church Center</a>")
t=t.replace(' aria-live="polite"','')
t=t.replace('.hero-inner{position:relative;z-index:3;max-width:780px;}','.hero-inner{position:relative;z-index:3;width:100%;}.hero-inner>*{max-width:780px;}')
t=t.replace('.foot-bottom{border-top:1px solid rgba(255,255,255,.16);margin-top:38px;','.foot-bottom{border-top:0;position:relative;margin-top:38px;')
t=t.replace('</style>','.foot-bottom::before{content:"";position:absolute;left:24px;right:24px;top:0;border-top:1px solid rgba(255,255,255,.16);}\n@media (max-width:600px){.foot-bottom::before{left:20px;right:20px;}}\n</style>',1)
t=t.replace('up to 4th grade','through 5th grade')
exec(open('copyedit.txt').read())
# tokens (single source)
t=t.replace("10:45 AM","{{SUN_TIME}}").replace("6:00&ndash;7:30 PM","{{WED_TIME}}")
t=t.replace("6:00 PM","{{MON_TIME}}").replace("903.662.5275","{{PHONE}}").replace("+19036625275","{{PHONE_TEL}}")
open('template.html','w',encoding='utf-8').write(t)

out=t
for k,v in CFG.items(): out=out.replace('{{'+k+'}}',v)
assert '{{' not in out, re.findall(r'\{\{.*?\}\}',out)
open('index.html','w',encoding='utf-8').write(out)
print('ok',len(out))

# ================= PRODUCTION BUILD (dist/) =================
import os, shutil, zipfile
DOM='https://prairievalleychurch.com'
if os.path.exists('dist'): shutil.rmtree('dist')
os.makedirs('dist/assets')
def raw(u): return base64.b64decode(u.split(',',1)[1])
files={}
files[logo]='assets/logo.png'; files[fav]='assets/favicon-64.png'; files[apple]='apple-touch-icon.png'
files[H1]='assets/hero.jpg'; files[H2]='assets/worship.jpg'
for k,v in P.items(): files[v]='assets/staff-%s.jpg'%k.lower()
prod=out
for f in os.listdir('images/events'):
    shutil.copy('images/events/'+f,'dist/assets/event-'+f)
for uri,path in files.items():
    assert uri in prod,path
    open('dist/'+path,'wb').write(raw(uri)); prod=prod.replace(uri,'/'+path)
Image.open('images/favicon-source.png').convert('RGBA').save('dist/favicon.ico',sizes=[(16,16),(32,32),(48,48)])
# social share image 1200x630: aerial photo + logo
ph=Image.open('images/hero-source.png').convert('RGB').crop((0,40,2000,1090)).resize((1200,630),Image.LANCZOS)
lg=Image.open(SRC).convert('RGBA'); lg=lg.resize((210,int(210*lg.size[1]/lg.size[0])),Image.LANCZOS)
ph=ph.convert('RGBA'); ph.alpha_composite(lg,(48,630-48-lg.size[1])); ph.convert('RGB').save('dist/assets/og.jpg','JPEG',quality=82,optimize=True)
head='<meta name="theme-color" content="#02027D">'
assert prod.count(head)==1
prod=prod.replace(head,head+'\n<link rel="canonical" href="%s/">\n<meta property="og:url" content="%s/">\n<meta property="og:site_name" content="Prairie Valley Church">\n<meta property="og:image" content="%s/assets/og.jpg">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">\n<link rel="icon" href="/favicon.ico" sizes="any">'%(DOM,DOM,DOM))
open('dist/index.html','w',encoding='utf-8').write(prod)
open('dist/robots.txt','w').write('User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n'%DOM)
open('dist/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>%s/</loc><lastmod>2026-11-23</lastmod></url></urlset>\n'%DOM)
open('dist/_headers','w').write('/assets/*\n  Cache-Control: public, max-age=86400\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n')
open('dist/404.html','w',encoding='utf-8').write('''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found | Prairie Valley Church</title><meta name="robots" content="noindex"><link rel="icon" href="/assets/favicon-64.png"><style>body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#02027D;color:#fff;font-family:Calibri,Candara,Arial,sans-serif;text-align:center;padding:24px}img{width:84px;height:84px;margin-bottom:20px}h1{font-family:Georgia,serif;font-size:2.2rem;margin:0 0 12px}p{margin:0 0 28px;font-size:1.1rem;color:#C0C4EE}a{display:inline-block;background:#fff;color:#02027D;font-weight:700;padding:14px 30px;border-radius:999px;text-decoration:none}</style></head><body><main><img src="/assets/logo.png" alt=""><h1>We couldn't find that page</h1><p>It may have moved. Sundays at 10:45 AM, though, you'll find us right where we always are.</p><a href="/">Back to the home page</a></main></body></html>''')
with zipfile.ZipFile('prairie-valley-church-site.zip','w',zipfile.ZIP_DEFLATED) as z:
    for r,_,fs in os.walk('dist'):
        for f in fs:
            p=os.path.join(r,f); z.write(p,os.path.relpath(p,'dist'))
print('dist ok',os.path.getsize('dist/index.html'),os.path.getsize('prairie-valley-church-site.zip'))

# Publish: copy the finished site to the repo-root dist/ folder (this is what Netlify serves)
if os.path.exists('../dist'): shutil.rmtree('../dist')
shutil.copytree('dist','../dist')
print('copied to ../dist')
