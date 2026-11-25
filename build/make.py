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
import grow
_G=grow.load()
_HAS_GROW=grow.has_content(_G)
import json, html as _h, urllib.parse as _u
_S=json.load(open('../data/site.json',encoding='utf-8'))
def _e(v): return _h.escape(str(v).strip(),quote=True).replace('\u2013','&ndash;')
_d=re.sub(r'\D','',_S['phone'])[-10:]
assert len(_d)==10, 'phone in data/site.json needs 10 digits'
CFG={
 'SUN_TIME':_e(_S['sunday_time']),
 'WED_TIME':_e(_S['wednesday_time']),
 'MON_TIME':_e(_S['monday_time']),
 'PHONE':_e(_S['phone']),
 'PHONE_TEL':'+1'+_d,
 'PHONE_LD':'+1-%s-%s-%s'%(_d[:3],_d[3:6],_d[6:]),
 'STREET':_e(_S['street']),
 'CITY':_e(_S['city']),
 'STATE':_e(_S['state']),
 'ZIP':_e(_S['zip']),
 'ADDR_LINE':_e('%s, %s, %s'%(_S['street'],_S['city'],_S['state'])),
 'MAP_QUERY':_u.quote_plus('%s %s %s %s'%(_S['street'],_S['city'],_S['state'],_S['zip'])),
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
{"@context":"https://schema.org","@type":"Church","name":"Prairie Valley Church","telephone":"{{PHONE_LD}}","url":"@@DOM@@/","logo":"@@DOM@@/assets/logo.png","image":"@@DOM@@/assets/og.jpg","address":{"@type":"PostalAddress","streetAddress":"{{STREET}}","addressLocality":"{{CITY}}","addressRegion":"{{STATE}}","postalCode":"{{ZIP}}","addressCountry":"US"},"areaServed":[{"@type":"City","name":"Campbell"},{"@type":"City","name":"Lone Oak"},{"@type":"City","name":"Greenville"}],"sameAs":["https://www.facebook.com/pvbchurch.org","https://www.instagram.com/prairievalleychurch/","https://www.tiktok.com/@pvbchurch","https://www.youtube.com/@prairievalleybaptistchurch9414","https://pvbchurch.churchcenter.com"]}
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
t=t.replace("2417+FM+513+Campbell+TX+75422","{{MAP_QUERY}}").replace("2417 FM 513<br>Campbell, TX 75422","{{STREET}}<br>{{CITY}}, {{STATE}} {{ZIP}}").replace("2417 FM 513, Campbell, TX 75422","{{ADDR_LINE}} {{ZIP}}").replace("2417 FM 513, Campbell, TX","{{ADDR_LINE}}").replace("2417 FM 513","{{STREET}}")
assert '2417' not in t, 'a hard-coded address is still in the page'
t=t.replace("10:45 AM","{{SUN_TIME}}").replace("6:00&ndash;7:30 PM","{{WED_TIME}}")
t=t.replace("6:00 PM","{{MON_TIME}}").replace("903.662.5275","{{PHONE}}").replace("+19036625275","{{PHONE_TEL}}")
t=t.replace('<!--MINROWS-->',_MINROWS)  # ministries are inserted after the site-wide replacements so what staff type is what shows
open('template.html','w',encoding='utf-8').write(t)

out=t
for k,v in CFG.items(): out=out.replace('{{'+k+'}}',v)
assert '{{' not in out, re.findall(r'\{\{.*?\}\}',out)
open('index.html','w',encoding='utf-8').write(out)
print('ok',len(out))

# ================= PRODUCTION BUILD (dist/) =================
import os, shutil, zipfile
DOM='https://prairievalleychurch.com'
NOINDEX=True  # TEMPORARY: preview is public on github.io; set False at launch
if os.path.exists('dist'): shutil.rmtree('dist')
os.makedirs('dist/assets')
shutil.copytree('fonts','dist/assets/fonts')
def raw(u): return base64.b64decode(u.split(',',1)[1])
files={}
files[logo]='assets/logo.png'; files[fav]='assets/favicon-64.png'; files[apple]='apple-touch-icon.png'
files[H1]='assets/hero.jpg'; files[H2]='assets/worship.jpg'
prod=out
for uri,path in files.items():
    assert uri in prod,path
    open('dist/'+path,'wb').write(raw(uri)); prod=prod.replace(uri,path)
os.makedirs('dist/assets/people',exist_ok=True)
for _n,_b in _PIMGS.items(): open('dist/assets/people/'+_n,'wb').write(_b)
os.makedirs('dist/assets/site-photos',exist_ok=True)
for _n,_b in _SPHOTOS.items(): open('dist/assets/site-photos/'+_n,'wb').write(_b)
Image.open('images/favicon-source.png').convert('RGBA').save('dist/favicon.ico',sizes=[(16,16),(32,32),(48,48)])
# installable web app: icons + manifest
def _app_icon(size, frac):
    c=Image.new('RGBA',(size,size),(2,2,125,255)); d=int(size*frac)
    l=Image.open(SRC).convert('RGBA').resize((d,d),Image.LANCZOS); c.alpha_composite(l,((size-d)//2,(size-d)//2)); return c.convert('RGB')
os.makedirs('dist/assets/app',exist_ok=True)
_app_icon(192,.86).save('dist/assets/app/icon-192.png',optimize=True)
_app_icon(512,.86).save('dist/assets/app/icon-512.png',optimize=True)
_app_icon(512,.66).save('dist/assets/app/icon-maskable-512.png',optimize=True)
open('dist/manifest.webmanifest','w',encoding='utf-8').write(json.dumps({"name":"Prairie Valley Church","short_name":"Prairie Valley","description":"Prairie Valley Church in Campbell, Texas","start_url":"./","scope":"./","display":"standalone","background_color":"#02027D","theme_color":"#02027D","icons":[{"src":"assets/app/icon-192.png","sizes":"192x192","type":"image/png","purpose":"any"},{"src":"assets/app/icon-512.png","sizes":"512x512","type":"image/png","purpose":"any"},{"src":"assets/app/icon-maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]},indent=1))
# social share image 1200x630: aerial photo + logo
ph=Image.open('images/hero-source.png').convert('RGB').crop((0,40,2000,1090)).resize((1200,630),Image.LANCZOS)
lg=Image.open(SRC).convert('RGBA'); lg=lg.resize((210,int(210*lg.size[1]/lg.size[0])),Image.LANCZOS)
ph=ph.convert('RGBA'); ph.alpha_composite(lg,(48,630-48-lg.size[1])); ph.convert('RGB').save('dist/assets/og.jpg','JPEG',quality=82,optimize=True)
head='<meta name="theme-color" content="#02027D">'
assert prod.count(head)==1
prod=prod.replace('@@DOM@@',DOM)
prod=prod.replace(head,head+'\n<link rel="canonical" href="%s/">\n<meta property="og:url" content="%s/">\n<meta property="og:site_name" content="Prairie Valley Church">\n<meta property="og:image" content="%s/assets/og.jpg">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">\n<link rel="icon" href="favicon.ico" sizes="any">\n<link rel="manifest" href="manifest.webmanifest">\n<meta name="apple-mobile-web-app-title" content="Prairie Valley">\n<meta name="mobile-web-app-capable" content="yes">'%(DOM,DOM,DOM)+('\n<meta name="robots" content="noindex">' if NOINDEX else ''))
# ---- optional OneSignal push (does nothing until data/site.json has onesignal_app_id) ----
_OS=str(_S.get('onesignal_app_id') or '').strip()
if _OS:
    assert re.match(r'^[0-9a-fA-F-]{36}$',_OS), 'onesignal_app_id in data/site.json should look like xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
    open('dist/OneSignalSDKWorker.js','w').write('importScripts("https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.sw.js");\n')
    _osh='<script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script>\n<script>window.OneSignalDeferred=window.OneSignalDeferred||[];OneSignalDeferred.push(async function(OneSignal){await OneSignal.init({appId:"%s"});});</script>'%_OS
    assert prod.count('</head>')==1
    prod=prod.replace('</head>',_osh+'\n</head>',1)
    _nf='''<div class="wrap notify" id="notify"><div><strong>Church notifications</strong><p id="notify-msg">Get announcements from Prairie Valley on your phone. You choose; you can turn them off anytime.</p></div><button type="button" id="notify-btn">Turn on notifications</button></div>
<style>.notify{display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap;border-top:1px solid rgba(255,255,255,.16);margin-top:30px;padding-top:22px;color:#fff;}.notify p{margin:4px 0 0;color:var(--navy-tint);max-width:56ch;}.notify button{font:inherit;font-weight:700;background:#fff;color:#02027D;border:0;border-radius:999px;padding:13px 26px;cursor:pointer;}.notify button[hidden]{display:none;}</style>
<script>(function(){var b=document.getElementById("notify-btn"),m=document.getElementById("notify-msg");if(!b)return;var ua=navigator.userAgent||"",ios=/iPad|iPhone|iPod/.test(ua)||(navigator.platform==="MacIntel"&&navigator.maxTouchPoints>1),sa=window.navigator.standalone===true||matchMedia("(display-mode: standalone)").matches||matchMedia("(display-mode: fullscreen)").matches;
if(ios&&!sa){b.hidden=true;m.textContent="On iPhone: tap the Share button in Safari, choose Add to Home Screen, then open the Prairie Valley icon from your home screen and come back to this button.";return;}
window.OneSignalDeferred=window.OneSignalDeferred||[];
OneSignalDeferred.push(function(OneSignal){try{if(OneSignal.Notifications.permission){m.textContent="Notifications are on. Thank you!";b.hidden=true;}}catch(e){}});
b.addEventListener("click",function(){OneSignalDeferred.push(async function(OneSignal){try{await OneSignal.Notifications.requestPermission();if(OneSignal.Notifications.permission){m.textContent="Notifications are on. Thank you!";b.hidden=true;}else{m.textContent="Notifications are off. You can change this in your phone settings.";}}catch(e){m.textContent="Sorry, something went wrong. Please try again later.";}});});})();</script>
'''
    _fb='<div class="wrap foot-bottom">'
    assert prod.count(_fb)==1
    prod=prod.replace(_fb,_nf+_fb,1)
open('dist/index.html','w',encoding='utf-8').write(prod)
if _HAS_GROW:
    os.makedirs('dist/grow',exist_ok=True)
    open('dist/grow/index.html','w',encoding='utf-8').write(grow.page(prod,_G,DOM))
open('dist/robots.txt','w').write('User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n'%DOM)
open('dist/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>%s/</loc><lastmod>2026-11-23</lastmod></url>%s</urlset>\n'%(DOM,('<url><loc>%s/grow/</loc></url>'%DOM) if _HAS_GROW else ''))
open('dist/_headers','w').write('/assets/*\n  Cache-Control: public, max-age=86400\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n')
open('dist/404.html','w',encoding='utf-8').write('''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found | Prairie Valley Church</title><meta name="robots" content="noindex"><link rel="icon" href="/assets/favicon-64.png"><style>body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#02027D;color:#fff;font-family:Calibri,Candara,Arial,sans-serif;text-align:center;padding:24px}img{width:84px;height:84px;margin-bottom:20px}h1{font-family:Georgia,serif;font-size:2.2rem;margin:0 0 12px}p{margin:0 0 28px;font-size:1.1rem;color:#C0C4EE}a{display:inline-block;background:#fff;color:#02027D;font-weight:700;padding:14px 30px;border-radius:999px;text-decoration:none}</style></head><body><main><img src="/assets/logo.png" alt=""><h1>We couldn't find that page</h1><p>It may have moved. Sundays at 10:45 AM, though, you'll find us right where we always are.</p><a href="/">Back to the home page</a></main></body></html>''')
_p='dist/404.html'; _404=open(_p,encoding='utf-8').read().replace('10:45 AM',CFG['SUN_TIME']); open(_p,'w',encoding='utf-8').write(_404)
with zipfile.ZipFile('prairie-valley-church-site.zip','w',zipfile.ZIP_DEFLATED) as z:
    for r,_,fs in os.walk('dist'):
        for f in fs:
            p=os.path.join(r,f); z.write(p,os.path.relpath(p,'dist'))
print('dist ok',os.path.getsize('dist/index.html'),os.path.getsize('prairie-valley-church-site.zip'))

# Publish: copy the finished site to the repo-root dist/ folder (this is what Netlify serves)
if os.path.exists('../dist'): shutil.rmtree('../dist')
shutil.copytree('dist','../dist')
print('copied to ../dist')
