import os, re
from datetime import datetime

REPO = "/home/user/investor-information"
RESULTS = f"{REPO}/results"
OUTPUT = f"{REPO}/index.html"

def to_ul(text):
    items = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if line.startswith('- '):
            item = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', line[2:])
            items.append(f'<li>{item}</li>')
    return '<ul>' + ''.join(items) + '</ul>' if items else '<ul><li>Keine Informationen gefunden.</li></ul>'

def to_sources(text):
    out = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if line.startswith('- '):
            item = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', line[2:])
            out.append(f'<div>{item}</div>')
    return ''.join(out) or '<div>Keine Quellen</div>'

def parse(path):
    txt = open(path, encoding='utf-8').read()
    d = {}
    m = re.match(r'^# (.+)', txt, re.MULTILINE)
    d['title'] = m.group(1) if m else 'Unbekannt'
    tm = re.search(r'\(([^)]+)\)', d['title'])
    d['ticker'] = tm.group(1) if tm else ''
    d['company'] = re.sub(r'\s*\([^)]+\)$', '', d['title']).strip()
    for sec in ['Aktuelle Meldungen', 'Management', 'Finanzielles', 'Strategie & Ausblick', 'Quellen']:
        m = re.search(rf'## {re.escape(sec)}\n(.*?)(?=\n## |\Z)', txt, re.DOTALL)
        d[sec] = m.group(1).strip() if m else ''
    return d

meta = {}
for line in open(f"{RESULTS}/_meta.md"):
    if ':' in line:
        k, v = line.split(':', 1)
        meta[k.strip()] = v.strip()

kw, jahr = meta.get('KW','??'), meta.get('JAHR','????')
von, bis = meta.get('ZEITRAUM_VON',''), meta.get('ZEITRAUM_BIS','')
now = datetime.now().strftime('%d.%m.%Y %H:%M')

companies = []
for f in sorted(f for f in os.listdir(RESULTS) if re.match(r'^\d{2}_', f)):
    d = parse(f"{RESULTS}/{f}")
    d['slug'] = f.replace('.md', '')
    companies.append(d)

nav = ''.join(f'<a href="#{c["slug"]}">{c["company"]}</a>' for c in companies)

cards = ''
for c in companies:
    cards += f'''
  <div class="card" id="{c['slug']}">
    <h2>{c['company']} <span class="ticker">{c['ticker']}</span></h2>
    <div class="meta">KW{kw} / {jahr} &nbsp;·&nbsp; {von} – {bis}</div>
    <h3>Aktuelle Meldungen</h3>{to_ul(c['Aktuelle Meldungen'])}
    <h3>Management</h3>{to_ul(c['Management'])}
    <h3>Finanzielles</h3>{to_ul(c['Finanzielles'])}
    <h3>Strategie & Ausblick</h3>{to_ul(c['Strategie & Ausblick'])}
    <h3>Quellen</h3><div class="sources">{to_sources(c['Quellen'])}</div>
  </div>'''

html = f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Investor Radar – KW{kw} / {jahr}</title>
  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#0f1117;color:#e2e8f0;line-height:1.6}}
    header{{background:#1a1f2e;border-bottom:1px solid #2d3748;padding:2rem;text-align:center}}
    header h1{{font-size:1.8rem;color:#63b3ed;font-weight:700}}
    header p{{color:#718096;font-size:.9rem;margin-top:.4rem}}
    nav{{background:#1a1f2e;border-bottom:1px solid #2d3748;padding:1rem 2rem;display:flex;flex-wrap:wrap;gap:.5rem;justify-content:center}}
    nav a{{color:#90cdf4;text-decoration:none;font-size:.8rem;padding:.25rem .6rem;border:1px solid #2d3748;border-radius:4px;transition:background .2s}}
    nav a:hover{{background:#2d3748}}
    main{{max-width:960px;margin:2rem auto;padding:0 1.5rem;display:grid;gap:1.5rem}}
    .card{{background:#1a1f2e;border:1px solid #2d3748;border-radius:8px;padding:1.5rem}}
    .card h2{{font-size:1.1rem;color:#63b3ed;margin-bottom:.3rem;display:flex;align-items:center;gap:.6rem}}
    .card .ticker{{font-size:.75rem;color:#718096;font-weight:400}}
    .card .meta{{font-size:.78rem;color:#4a5568;margin-bottom:1rem}}
    .card h3{{font-size:.8rem;text-transform:uppercase;letter-spacing:.05em;color:#4a5568;margin:1rem 0 .4rem}}
    .card ul{{padding-left:1.2rem;font-size:.88rem;color:#cbd5e0}}
    .card ul li{{margin-bottom:.25rem}}
    .card .sources{{margin-top:1rem;font-size:.8rem}}
    .card .sources a{{color:#4a5568;text-decoration:none;display:block;margin-bottom:.2rem}}
    .card .sources a:hover{{color:#90cdf4}}
    footer{{text-align:center;padding:2rem;font-size:.78rem;color:#4a5568;border-top:1px solid #2d3748;margin-top:2rem}}
  </style>
</head>
<body>
<header>
  <h1>&#128202; Investor Radar</h1>
  <p>KW{kw} / {jahr} &nbsp;&middot;&nbsp; {von} &ndash; {bis} &nbsp;&middot;&nbsp; {len(companies)} Unternehmen</p>
</header>
<nav>{nav}</nav>
<main>{cards}</main>
<footer>Automatisch erstellt von Claude Code &nbsp;&middot;&nbsp; {now}</footer>
</body>
</html>'''

open(OUTPUT, 'w', encoding='utf-8').write(html)
print(f"OK: {len(companies)} Karten → {OUTPUT}")
