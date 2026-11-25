"""Builds the Grow page (sermon quotes, newsletter archive, discussion questions) from data/grow.json.
If there is no content yet, no page and no menu link are produced."""
import json, html, os, re
from datetime import date, timedelta

def _e(s): return html.escape(str(s or '').strip(), quote=True)

def _strip_quotes(s):
    return str(s or '').strip().strip('"“”‘’\'').strip()

def _fmt(d, long=False):
    try:
        y, m, dd = [int(x) for x in str(d).split('-')]
        dt = date(y, m, dd)
        return dt.strftime('%B %Y') if long else dt.strftime('%b ') + str(dt.day) + dt.strftime(', %Y')
    except Exception:
        return str(d or '').strip()

def _sortkey(x): return str(x.get('date') or '')

def _pdf(rel):
    rel = str(rel or '').strip().lstrip('/')
    if not rel: return None
    if re.match(r'^https?://', rel): return rel
    full = os.path.normpath(os.path.join('..', rel))
    root = os.path.normpath('../data/media')
    if not full.startswith(root + os.sep) or not os.path.isfile(full):
        print('WARNING: newsletter file not found in data/media, skipping its link:', rel); return None
    return rel

def load():
    d = json.load(open('../data/grow.json', encoding='utf-8'))
    quotes = [q for q in d.get('quotes', []) if _strip_quotes(q.get('quote'))]
    quotes.sort(key=_sortkey, reverse=True)
    issues = [n for n in d.get('newsletters', []) if (n.get('file') or n.get('summary') or n.get('title'))]
    issues.sort(key=_sortkey, reverse=True)
    bulletins = [b for b in d.get('bulletins', []) if b.get('file')]
    bulletins.sort(key=_sortkey, reverse=True)
    disc = d.get('discussion') or {}
    disc = disc if (str(disc.get('url') or '').strip()) else None
    weeks = [w for w in d.get('weeks', []) if (w.get('devotionals') or w.get('step') or w.get('questions'))]
    weeks.sort(key=_sortkey, reverse=True)
    pr = d.get('pray') or {}
    pitems = [i for i in (pr.get('items') or []) if re.match(r'^https?://', str(i.get('url') or '').strip()) and str(i.get('name') or '').strip()]
    pray = {'heading': (pr.get('heading') or 'Make room to pray').strip(), 'intro': (pr.get('intro') or '').strip(), 'items': pitems} if pitems else None
    return {'intro': (d.get('intro') or '').strip(), 'quotes': quotes, 'issues': issues, 'disc': disc, 'weeks': weeks, 'pray': pray, 'bulletins': bulletins}

def latest_pdf(g):
    for n in g['issues']:
        f = _pdf(n.get('file'))
        if f: return f, (n.get('title') or ((_fmt(n['date'], True) + ' newsletter') if n.get('date') else 'Newsletter'))
    return None

def has_content(g): return bool(g['quotes'] or g['issues'] or g['disc'] or g['weeks'] or g['pray'] or g['bulletins'])

def _meta(q):
    bits = []
    if q.get('passage'): bits.append(_e(q['passage']))
    if q.get('sermon'): bits.append('“%s”' % _e(q['sermon']))
    if q.get('date'): bits.append(_e(_fmt(q['date'])))
    return ' &middot; '.join(bits)

def _link(url, text):
    url = str(url or '').strip()
    return '<a class="q-link" href="%s" target="_blank" rel="noopener">%s <span class="arrow" aria-hidden="true">&rarr;</span></a>' % (_e(url), text) if re.match(r'^https?://', url) else ''


def _paras(s): return ''.join('<p>%s</p>' % _e(x) for x in re.split(r'\n\s*\n', str(s or '').strip()) if x.strip())

def _day_iso(w, i):
    try:
        y, m, dd = [int(x) for x in str(w.get('date')).split('-')]
        return (date(y, m, dd) + timedelta(days=i + 1)).isoformat()
    except Exception:
        return ''

def _week_html(w, current):
    wid = 'week-%s' % str(w.get('date') or '').strip()
    title = _e(w.get('sermon') or 'This week')
    meta = ' &middot; '.join(x for x in [_e(w.get('passage')), _e(_fmt(w['date'])) if w.get('date') else ''] if x)
    s = ['<article class="wk" id="%s">' % wid,
         '<div class="wk-head"><h3>%s</h3><p class="q-meta">%s</p>%s</div>' % (title, meta, _link(w.get('watch_url'), 'Watch the sermon'))]
    if w.get('step'):
        s.append('<div class="wk-step"><div class="kicker">Your step this week</div><p>%s</p></div>' % _e(w['step']))
    if w.get('quote'):
        s.append('<figure class="q-card wk-quote"><blockquote><p>&ldquo;%s&rdquo;</p></blockquote></figure>' % _e(_strip_quotes(w['quote'])))
    refs = [r.strip() for r in str(w.get('reflection_scripture') or '').split(';') if r.strip()]
    if refs:
        s.append('<p class="wk-refs"><strong>Read this week:</strong> %s</p>' % '; '.join(_e(r) for r in refs))
    devs = w.get('devotionals') or []
    if devs:
        s.append('<h4 class="wk-sub">Five-day devotional</h4><div class="wk-devs">')
        for i, dv in enumerate(devs):
            iso = _day_iso(w, i)
            did = 'd-' + (iso or 'x%d' % i)
            s.append('<details class="dev" id="%s" data-date="%s"><summary><span class="dev-day">%s</span> <span class="dev-title">%s</span></summary><div class="dev-body">'
                     '<p class="dev-ref"><strong>%s</strong> %s</p>%s<p class="dev-q"><strong>Today&rsquo;s question.</strong> %s</p><p class="dev-pray"><strong>Prayer.</strong> %s</p></div></details>' % (
                     _e(did), _e(iso), _e(dv.get('day')), _e(dv.get('title')), _e(dv.get('scripture')), _e(dv.get('scripture_text')),
                     _paras(dv.get('reflection')), _e(dv.get('question')), _e(dv.get('prayer'))))
        s.append('</div>')
    qs = [q for q in (w.get('questions') or []) if str(q).strip()]
    if qs:
        s.append('<details class="dev wk-disc"><summary><span class="dev-title">Discussion questions for your group or family</span></summary><div class="dev-body">%s<ol>%s</ol></div></details>' % (
                 ('<p>%s</p>' % _e(w['opening_question'])) if w.get('opening_question') else '', ''.join('<li>%s</li>' % _e(q) for q in qs)))
    s.append('</article>')
    return ''.join(s)

def _weeks_html(g):
    ws = g['weeks']
    if not ws: return ''
    out = ['<section id="week"><div class="wrap"><div class="section-head reveal"><span class="kicker">This week</span><h2>Grow this week</h2></div>', _week_html(ws[0], True)]
    old = ws[1:9]
    if old:
        out.append('<div class="wk-archive"><h3>Past weeks</h3>' + ''.join('<details class="dev wk-old"><summary><span class="dev-title">%s</span> <span class="dev-day">%s</span></summary>%s</details>' % (_e(w.get('sermon') or 'Past week'), _e(_fmt(w.get('date'))), _week_html(w, False)) for w in old) + '</div>')
    out.append('</div></section>')
    return ''.join(out)

LADDER = [('Worship with us', 'Sundays at 10:45 AM. Come as you are and sit with someone new.', '#visit'),
          ('Open the Bible with others', 'Wednesday night Bible study, kids and students, and groups.', '#ministries'),
          ('Serve', 'Ask about the ways people serve here. Obscure work still counts.', '#ministries')]

def main_html(g):
    out = ['<main id="main">',
           '<div class="hero grow-hero"><div class="wrap hero-inner"><span class="kicker" style="color:var(--navy-tint)">Grow</span>'
           '<h1>Grow in Christ</h1>%s</div></div>' % ('<p class="lead">%s</p>' % _e(g['intro']) if g['intro'] else '')]
    out.append(_weeks_html(g))
    qs = g['quotes']
    if qs:
        f = qs[0]
        s = ['<section id="quotes"><div class="wrap"><div class="section-head reveal"><span class="kicker">From the pulpit</span><h2>Quotes from recent sermons</h2></div>',
             '<figure class="q-feature reveal"><blockquote><p>“%s”</p></blockquote><figcaption class="q-meta">%s</figcaption>%s</figure>' % (_e(_strip_quotes(f['quote'])), _meta(f), _link(f.get('url'), 'Watch this sermon'))]
        def _cards(L): return '<div class="q-grid reveal">' + ''.join('<figure class="q-card"><blockquote><p>“%s”</p></blockquote><figcaption class="q-meta">%s</figcaption>%s</figure>' % (_e(_strip_quotes(q['quote'])), _meta(q), _link(q.get('url'), 'Watch')) for q in L) + '</div>'
        if qs[1:4]:
            s.append(_cards(qs[1:4]))
        if qs[4:12]:
            s.append('<details class="q-more reveal"><summary>More quotes (%d)</summary>%s</details>' % (len(qs[4:12]), _cards(qs[4:12])))
        s.append('</div></section>')
        out.append(''.join(s))
    iss = g['issues']
    if iss:
        def label(n): return _e(n.get('title') or ((_fmt(n['date'], True) + ' newsletter') if n.get('date') else 'Newsletter'))
        n0 = iss[0]; f0 = _pdf(n0.get('file'))
        s = ['<section id="newsletter" class="alt"><div class="wrap"><div class="section-head reveal"><span class="kicker">Stay in the loop</span><h2>Monthly newsletter</h2></div>',
             '<div class="nl-latest reveal"><div class="kicker">Latest issue</div><h3>%s</h3>%s%s</div>' % (label(n0), '<p>%s</p>' % _e(n0['summary']) if n0.get('summary') else '', ('<a class="btn solid" href="%s" target="_blank" rel="noopener">Read this issue <span class="arrow" aria-hidden="true">&rarr;</span></a> <a class="btn" href="%s" download>Download PDF</a>' % (_e(f0), _e(f0))) if f0 else '')]
        older = iss[1:13]
        if older:
            s.append('<ul class="nl-list reveal">' + ''.join('<li><span>%s</span>%s</li>' % (label(n), ('<span><a href="%s" target="_blank" rel="noopener">Read <span class="arrow" aria-hidden="true">&rarr;</span></a> &nbsp; <a href="%s" download>Download</a></span>' % (_e(_pdf(n.get('file'))), _e(_pdf(n.get('file'))))) if _pdf(n.get('file')) else '') for n in older) + '</ul>')
        s.append('</div></section>')
        out.append(''.join(s))
    bl = [b for b in g['bulletins'] if _pdf(b.get('file'))]
    if bl:
        def blabel(b): return _e(b.get('title') or ((_fmt(b['date'], True) if False else _fmt(b['date'])) + ' bulletin' if b.get('date') else 'Bulletin'))
        b0 = bl[0]; f0 = _pdf(b0['file'])
        s = ['<section id="bulletins"><div class="wrap"><div class="section-head reveal"><span class="kicker">This week</span><h2>Sunday bulletin</h2></div>',
             '<div class="nl-latest reveal"><div class="kicker">Latest</div><h3>%s</h3>%s<a class="btn solid" href="%s" target="_blank" rel="noopener">Read the bulletin <span class="arrow" aria-hidden="true">&rarr;</span></a> <a class="btn" href="%s" download>Download PDF</a></div>' % (blabel(b0), '<p>%s</p>' % _e(b0['summary']) if b0.get('summary') else '', _e(f0), _e(f0))]
        older = bl[1:13]
        if older:
            s.append('<details class="q-more reveal"><summary>Past bulletins (%d)</summary><ul class="nl-list">%s</ul></details>' % (len(older), ''.join('<li><span>%s</span><span><a href="%s" target="_blank" rel="noopener">Read <span class="arrow" aria-hidden="true">&rarr;</span></a> &nbsp; <a href="%s" download>Download</a></span></li>' % (blabel(b), _e(_pdf(b['file'])), _e(_pdf(b['file']))) for b in older)))
        s.append('</div></section>')
        out.append(''.join(s))
    pr = g['pray']
    if pr:
        out.append('<section id="pray"><div class="wrap"><div class="section-head reveal"><span class="kicker">Prayer</span><h2>%s</h2>%s</div><div class="pray-grid reveal">%s</div></div></section>' % (_e(pr['heading']), '<p class="lead">%s</p>' % _e(pr['intro']) if pr['intro'] else '', ''.join('<div class="nl-latest"><h3>%s</h3><p>%s</p><a class="btn solid" href="%s" target="_blank" rel="noopener">%s <span class="arrow" aria-hidden="true">&rarr;</span></a></div>' % (_e(i['name']), _e(i.get('description')), _e(i['url']), _e(i.get('button') or 'Open')) for i in pr['items'])))
    dd = g['disc']
    s = ['<section id="next"><div class="wrap"><div class="section-head reveal"><span class="kicker">Next steps</span><h2>Keep going between Sundays</h2></div><div class="nl-latest reveal">']
    if dd:
        s.append('<h3>%s</h3>%s<a class="btn solid" href="%s" target="_blank" rel="noopener">Open <span class="arrow" aria-hidden="true">&rarr;</span></a>' % (_e(dd.get('title') or 'Discussion questions'), '<p>%s</p>' % _e(dd['description']) if dd.get('description') else '', _e(dd['url'])))
    else:
        s.append('<h3>Find your people</h3><p>Growing happens best with others. See our Wednesday night Bible study and small groups.</p>')
    s.append('<p style="margin-top:18px"><a class="q-link" href="#ministries">See our ministries <span class="arrow" aria-hidden="true">&rarr;</span></a></p></div>')
    s.append('<ol class="ladder reveal">' + ''.join('<li><a href="%s"><strong>%s</strong><span>%s</span></a></li>' % (h, _e(t), _e(d)) for t, d, h in LADDER) + '</ol></div></section>')
    out.append(''.join(s))
    out.append('</main>')
    return '\n'.join(out)

JS = """<script>(function(){try{var d=document.querySelectorAll('.wk-devs .dev');if(!d.length)return;var h=(location.hash||'').slice(1),t=new Date(),iso=t.getFullYear()+'-'+('0'+(t.getMonth()+1)).slice(-2)+'-'+('0'+t.getDate()).slice(-2),hit=null;
for(var i=0;i<d.length;i++){if(d[i].id===h)hit=d[i];}if(!hit){for(var j=0;j<d.length;j++){if(d[j].getAttribute('data-date')===iso)hit=d[j];}}
for(var k=0;k<d.length;k++){d[k].open=(d[k]===hit);}if(hit&&h===hit.id){setTimeout(function(){hit.scrollIntoView();},50);}}catch(e){}})();</script>"""

CSS = '''
.grow-hero{min-height:0;padding-block:150px 64px;}
.grow-hero .lead{max-width:60ch;}
@media (max-width:760px){.grow-hero{padding-block:116px 36px;}}
.q-feature{margin:0;padding:34px 36px;background:var(--panel);border-left:5px solid var(--navy);border-radius:0 12px 12px 0;}
.q-feature blockquote,.q-card blockquote{margin:0;}
.q-feature p{font-family:var(--serif);font-size:clamp(1.3rem,2.3vw,1.85rem);line-height:1.4;color:var(--navy);margin:0 0 16px;}
.q-meta{font-size:.95rem;opacity:.8;}
.q-link{display:inline-block;margin-top:12px;font-weight:700;color:var(--navy);}
.q-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-top:28px;}
.q-card{margin:0;padding:22px 24px;border:1px solid var(--line);border-radius:12px;background:var(--white);}
.q-card p{font-family:var(--serif);font-size:1.08rem;line-height:1.5;color:var(--navy);margin:0 0 12px;}
.nl-latest{background:var(--white);border:1px solid var(--line);border-radius:12px;padding:30px 32px;}
#next .nl-latest{background:var(--panel);border:0;}
.nl-latest h3{margin:6px 0 10px;}
.nl-latest p{max-width:62ch;}
.nl-list{list-style:none;margin:26px 0 0;padding:0;border-top:1px solid var(--line);}
.nl-list li{display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap;padding:14px 0;border-bottom:1px solid var(--line);}
.nl-list a{font-weight:700;color:var(--navy);}
.q-more{margin-top:24px;}
.q-more summary{cursor:pointer;font-weight:700;color:var(--navy);padding:10px 0;}
.pray-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;margin-top:8px;}
.wk{background:var(--white);border:1px solid var(--line);border-radius:12px;padding:30px 32px;}
.wk-head h3{margin:0 0 4px;}
.wk-step{margin:22px 0;padding:22px 24px;background:var(--panel);border-left:5px solid var(--navy);border-radius:0 12px 12px 0;}
.wk-step p{font-family:var(--serif);font-size:1.2rem;line-height:1.45;color:var(--navy);margin:6px 0 0;}
.wk-refs{margin:16px 0;}
.wk-sub{margin:28px 0 12px;}
.dev{border:1px solid var(--line);border-radius:10px;margin:10px 0;background:var(--white);}
.dev summary{cursor:pointer;padding:14px 18px;font-weight:700;color:var(--navy);display:flex;gap:12px;flex-wrap:wrap;align-items:baseline;}
.dev-day{font-size:.82rem;letter-spacing:.08em;text-transform:uppercase;opacity:.75;}
.dev-body{padding:4px 20px 18px;max-width:68ch;}
.dev-q,.dev-pray{margin-top:14px;}
.wk-archive{margin-top:36px;}
.ladder{list-style:none;margin:28px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;counter-reset:l;}
.ladder li{counter-increment:l;}
.ladder a{display:block;height:100%;padding:20px 22px;border:1px solid var(--line);border-radius:12px;color:inherit;text-decoration:none;}
.ladder a:before{content:counter(l);display:block;font-family:var(--serif);font-size:1.6rem;color:var(--navy);}
.ladder strong{display:block;color:var(--navy);}
.ladder span{display:block;margin-top:4px;}
@media (max-width:760px){.wk{padding:22px 18px;}.q-feature{padding:24px 22px;}.nl-latest{padding:24px 22px;}}
'''

def page(prod, g, DOM):
    """Derive the Grow page from the finished home page so header, footer, styles and scripts are shared."""
    a = prod.index('<main id="main">'); b = prod.index('</main>') + len('</main>')
    p = prod[:a] + main_html(g) + prod[b:]
    p = p.replace('<head>', '<head>\n<base href="../">', 1)
    if g['weeks']: p = p.replace('</body>', JS + '</body>', 1)
    desc = 'Quotes from recent sermons, the monthly newsletter, and next steps for growing in Christ at Prairie Valley Church in Campbell, Texas.'
    p = re.sub(r'<title>.*?</title>', '<title>Grow in Christ | Prairie Valley Church</title>', p, count=1, flags=re.S)
    p = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % desc, p, count=1)
    p = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s/grow/">' % DOM, p, count=1)
    p = re.sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="%s/grow/">' % DOM, p, count=1)
    p = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Grow in Christ | Prairie Valley Church">', p, count=1)
    p = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % desc, p, count=1)
    return p
