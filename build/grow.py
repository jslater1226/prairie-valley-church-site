"""Builds the Grow page (sermon quotes, newsletter archive, discussion questions) from data/grow.json.
If there is no content yet, no page and no menu link are produced."""
import json, html, os, re
from datetime import date

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
    disc = d.get('discussion') or {}
    disc = disc if (str(disc.get('url') or '').strip()) else None
    return {'intro': (d.get('intro') or '').strip(), 'quotes': quotes, 'issues': issues, 'disc': disc}

def has_content(g): return bool(g['quotes'] or g['issues'] or g['disc'])

def _meta(q):
    bits = []
    if q.get('passage'): bits.append(_e(q['passage']))
    if q.get('sermon'): bits.append('“%s”' % _e(q['sermon']))
    if q.get('date'): bits.append(_e(_fmt(q['date'])))
    return ' &middot; '.join(bits)

def _link(url, text):
    url = str(url or '').strip()
    return '<a class="q-link" href="%s" target="_blank" rel="noopener">%s <span class="arrow">&rarr;</span></a>' % (_e(url), text) if re.match(r'^https?://', url) else ''

def main_html(g):
    out = ['<main id="main">',
           '<div class="hero grow-hero"><div class="wrap hero-inner"><span class="kicker" style="color:var(--navy-tint)">Grow</span>'
           '<h1>Grow in Christ</h1>%s</div></div>' % ('<p class="lead">%s</p>' % _e(g['intro']) if g['intro'] else '')]
    qs = g['quotes']
    if qs:
        f = qs[0]
        s = ['<section id="quotes"><div class="wrap"><div class="section-head reveal"><span class="kicker">From the pulpit</span><h2>Quotes from recent sermons</h2></div>',
             '<figure class="q-feature reveal"><blockquote><p>“%s”</p></blockquote><figcaption class="q-meta">%s</figcaption>%s</figure>' % (_e(_strip_quotes(f['quote'])), _meta(f), _link(f.get('url'), 'Watch this sermon'))]
        rest = qs[1:9]
        if rest:
            s.append('<div class="q-grid reveal">' + ''.join('<figure class="q-card"><blockquote><p>“%s”</p></blockquote><figcaption class="q-meta">%s</figcaption>%s</figure>' % (_e(_strip_quotes(q['quote'])), _meta(q), _link(q.get('url'), 'Watch')) for q in rest) + '</div>')
        s.append('</div></section>')
        out.append(''.join(s))
    iss = g['issues']
    if iss:
        def label(n): return _e(n.get('title') or ((_fmt(n['date'], True) + ' newsletter') if n.get('date') else 'Newsletter'))
        n0 = iss[0]; f0 = _pdf(n0.get('file'))
        s = ['<section id="newsletter" class="alt"><div class="wrap"><div class="section-head reveal"><span class="kicker">Stay in the loop</span><h2>Monthly newsletter</h2></div>',
             '<div class="nl-latest reveal"><div class="kicker">Latest issue</div><h3>%s</h3>%s%s</div>' % (label(n0), '<p>%s</p>' % _e(n0['summary']) if n0.get('summary') else '', '<a class="btn solid" href="%s" target="_blank" rel="noopener">Read this issue <span class="arrow">&rarr;</span></a>' % _e(f0) if f0 else '')]
        older = iss[1:13]
        if older:
            s.append('<ul class="nl-list reveal">' + ''.join('<li><span>%s</span>%s</li>' % (label(n), ('<a href="%s" target="_blank" rel="noopener">Read <span class="arrow">&rarr;</span></a>' % _e(_pdf(n.get('file')))) if _pdf(n.get('file')) else '') for n in older) + '</ul>')
        s.append('</div></section>')
        out.append(''.join(s))
    dd = g['disc']
    s = ['<section id="next"><div class="wrap"><div class="section-head reveal"><span class="kicker">Next steps</span><h2>Keep going between Sundays</h2></div><div class="nl-latest reveal">']
    if dd:
        s.append('<h3>%s</h3>%s<a class="btn solid" href="%s" target="_blank" rel="noopener">Open <span class="arrow">&rarr;</span></a>' % (_e(dd.get('title') or 'Discussion questions'), '<p>%s</p>' % _e(dd['description']) if dd.get('description') else '', _e(dd['url'])))
    else:
        s.append('<h3>Find your people</h3><p>Growing happens best with others. See our Wednesday night Bible study and small groups.</p>')
    s.append('<p style="margin-top:18px"><a class="q-link" href="#ministries">See our ministries <span class="arrow">&rarr;</span></a></p></div></div></section>')
    out.append(''.join(s))
    out.append('</main>')
    return '\n'.join(out)

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
@media (max-width:760px){.q-feature{padding:24px 22px;}.nl-latest{padding:24px 22px;}}
'''

def page(prod, g, DOM):
    """Derive the Grow page from the finished home page so header, footer, styles and scripts are shared."""
    a = prod.index('<main id="main">'); b = prod.index('</main>') + len('</main>')
    p = prod[:a] + main_html(g) + prod[b:]
    p = p.replace('<head>', '<head>\n<base href="../">', 1)
    desc = 'Quotes from recent sermons, the monthly newsletter, and next steps for growing in Christ at Prairie Valley Church in Campbell, Texas.'
    p = re.sub(r'<title>.*?</title>', '<title>Grow in Christ | Prairie Valley Church</title>', p, count=1, flags=re.S)
    p = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % desc, p, count=1)
    p = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s/grow/">' % DOM, p, count=1)
    p = re.sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="%s/grow/">' % DOM, p, count=1)
    p = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Grow in Christ | Prairie Valley Church">', p, count=1)
    p = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % desc, p, count=1)
    return p
