#!/usr/bin/env python3
"""doc-compare — визуальное сравнение markdown-документов с подсветкой правок.

В НЕ-diff режиме:
  - документы режутся на блоки (заголовки/абзацы/списки/таблицы);
  - через difflib вычисляются изменённые блоки;
  - слева подсвечивается красным (удалено/изменено), справа — зелёным (добавлено/изменено);
  - внутри правок — пословная подсветка (зачёркнутое красным / добавленное зелёным);
  - кнопка «Только изменения» прячет неизменённые блоки.

Формат --pair: "ЛеваяМетка|левый_файл|ПраваяМетка|правый_файл"
Префикс gh:owner/repo@ref:path — подтянуть файл из GitHub через `gh api`.
"""
import argparse, base64, difflib, html, os, re, subprocess, sys, tempfile, webbrowser

def fetch_gh(spec):
    """Pull a file from a public GitHub repo via `gh api`.

    Hardened against hangs: runs in its own process group and is SIGKILLed on
    timeout so a stuck/misbehaving `gh` can never block the comparison.
    """
    import signal as _signal
    rest = spec[3:]
    if '@' in rest:
        repo, path = rest.split('@', 1)
    else:
        repo, path = rest, 'main'
    if ':' in path:
        ref, fpath = path.split(':', 1)
    else:
        ref, fpath = 'main', path
    url = f"repos/{repo}/contents/{fpath}"
    if ref and ref != 'main':
        url += f"?ref={ref}"
    try:
        proc = subprocess.Popen(
            ['gh', 'api', url, '--jq', '.content'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, stdin=subprocess.DEVNULL, start_new_session=True,
        )
    except FileNotFoundError:
        sys.exit(f"[doc-compare] gh CLI not found; install gh or use a local file path ({spec})")
    try:
        out, err = proc.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), _signal.SIGKILL)
        except Exception:
            pass
        sys.exit(f"[doc-compare] gh fetch timed out ({spec})")
    if proc.returncode != 0:
        sys.exit(f"[doc-compare] gh fetch failed ({spec}): {err.strip()}")
    try:
        data = base64.b64decode(out)
    except Exception as e:
        sys.exit(f"[doc-compare] bad base64 from gh ({spec}): {e}")
    tf = tempfile.NamedTemporaryFile(delete=False, suffix='.md', prefix='doccmp_')
    tf.write(data); tf.close()
    return tf.name

def resolve_path(spec):
    return fetch_gh(spec) if spec.startswith('gh:') else spec

def read_text(spec):
    p = resolve_path(spec)
    try:
        with open(p, encoding='utf-8') as f:
            return f.read()
    except OSError as e:
        sys.exit(f"[doc-compare] cannot read {spec}: {e}")

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*(?!\*)(.+?)\*(?!\*)', r'<em>\1</em>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    return s

def strip_md(t):
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    t = re.sub(r'`([^`]+)`', r'\1', t)
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)\*(?!\*)', r'\1', t)
    return t

def norm(t):
    return re.sub(r'\s+', ' ', t).strip()

def parse_blocks(md):
    lines = md.split('\n'); blocks = []; i = 0; n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1; continue
        if line.strip() == '---':
            blocks.append({'html': '<hr>', 'src_s': i, 'src_e': i, 'raw': '---'}); i += 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            lv = len(m.group(1))
            blocks.append({'html': f'<h{lv}>{inline(m.group(2))}</h{lv}>', 'src_s': i, 'src_e': i, 'raw': line}); i += 1; continue
        if re.match(r'^\s*\|.*\|\s*$', line) and i + 1 < n \
                and re.match(r'^\s*\|?[\s:|-]+\|?\s*$', lines[i+1]) and '-' in lines[i+1]:
            s = i; rows = []
            while i < n and re.match(r'^\s*\|.*\|\s*$', lines[i]):
                rows.append(lines[i]); i += 1
            def cells(r):
                return [inline(c.strip()) for c in r.strip().strip('|').split('|')]
            header = cells(rows[0]); body = [cells(r) for r in rows[2:]]
            thead = '<tr>' + ''.join(f'<th>{h}</th>' for h in header) + '</tr>'
            tbody = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in body)
            blocks.append({'html': f'<table class="md-table"><thead>{thead}</thead><tbody>{tbody}</tbody></table>',
                           'src_s': s, 'src_e': i - 1, 'raw': '\n'.join(rows), 'table': True}); continue
        if re.match(r'^\s*-\s+', line):
            items = []; s = i
            while i < n and re.match(r'^\s*-\s+', lines[i]):
                items.append(f'<li>{inline(re.sub(r"^\s*-\s+", "", lines[i]))}</li>'); i += 1
            blocks.append({'html': '<ul>' + ''.join(items) + '</ul>', 'src_s': s, 'src_e': i - 1, 'raw': '\n'.join(lines[s:i])}); continue
        if re.match(r'^\s*\d+\.\s+', line):
            items = []; s = i
            while i < n and re.match(r'^\s*\d+\.\s+', lines[i]):
                items.append(f'<li>{inline(re.sub(r"^\s*\d+\.\s+", "", lines[i]))}</li>'); i += 1
            blocks.append({'html': '<ol>' + ''.join(items) + '</ol>', 'src_s': s, 'src_e': i - 1, 'raw': '\n'.join(lines[s:i])}); continue
        para = []; s = i
        while (i < n and lines[i].strip() and not re.match(r'^(#{1,6})\s+', lines[i])
               and not re.match(r'^\s*-\s+', lines[i]) and not re.match(r'^\s*\d+\.\s+', lines[i])
               and lines[i].strip() != '---' and not re.match(r'^\s*\|.*\|\s*$', lines[i])):
            para.append(lines[i]); i += 1
        raw = '\n'.join(para)
        blocks.append({'html': '<p>' + inline(' '.join(para)) + '</p>', 'src_s': s, 'src_e': i - 1, 'raw': raw})
    return blocks

def word_diff(left_text, right_text):
    def tok(t):
        return re.split(r'(\s+)', strip_md(t))
    lt, rt = tok(left_text), tok(right_text)
    sm = difflib.SequenceMatcher(None, lt, rt, autojunk=False)
    lo, ro = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        ls, rs = ''.join(lt[i1:i2]), ''.join(rt[j1:j2])
        if tag == 'equal':
            lo.append(html.escape(ls)); ro.append(html.escape(rs))
        elif tag == 'delete':
            lo.append(f'<span class="w-del">{html.escape(ls)}</span>')
        elif tag == 'insert':
            ro.append(f'<span class="w-add">{html.escape(rs)}</span>')
        else:  # replace
            lo.append(f'<span class="w-del">{html.escape(ls)}</span>')
            ro.append(f'<span class="w-add">{html.escape(rs)}</span>')
    return ''.join(lo), ''.join(ro)

def wrap_changed(block, inner, cls):
    if block.get('table'):
        return f'<div class="block chg-{cls}">{inner}</div>'
    hm = re.match(r'<(h[1-6])>', block['html'])
    if hm:
        return f'<{hm.group(1)} class="block chg-{cls}">{inner}</{hm.group(1)}>'
    return f'<div class="block chg-{cls}">{inner}</div>'

def build_visual(pairs):
    tabs, panes = [], []
    for idx, (ll, lf, rl, rf) in enumerate(pairs):
        active = ' active' if idx == 0 else ''
        lb = parse_blocks(read_text(lf)); rb = parse_blocks(read_text(rf))
        la = [norm(b['raw']) for b in lb]; ra = [norm(b['raw']) for b in rb]
        sm = difflib.SequenceMatcher(None, la, ra, autojunk=False)
        lparts, rparts = [], []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                for b in lb[i1:i2]:
                    lparts.append(f'<div class="block unchanged">{b["html"]}</div>')
                for b in rb[j1:j2]:
                    rparts.append(f'<div class="block unchanged">{b["html"]}</div>')
            elif tag == 'replace':
                if (i2 - i1) == 1 and (j2 - j1) == 1 and not lb[i1].get('table') and not rb[j1].get('table'):
                    lo, ro = word_diff(lb[i1]['raw'], rb[j1]['raw'])
                    lparts.append(wrap_changed(lb[i1], lo, 'del'))
                    rparts.append(wrap_changed(rb[j1], ro, 'add'))
                else:
                    for b in lb[i1:i2]:
                        lparts.append(f'<div class="block chg-del">{b["html"]}</div>')
                    for b in rb[j1:j2]:
                        rparts.append(f'<div class="block chg-add">{b["html"]}</div>')
            elif tag == 'delete':
                for b in lb[i1:i2]:
                    lparts.append(f'<div class="block chg-del">{b["html"]}</div>')
            else:  # insert
                for b in rb[j1:j2]:
                    rparts.append(f'<div class="block chg-add">{b["html"]}</div>')
        tabs.append(f'<button class="tab-btn{active}" data-tab="t{idx}">{html.escape(ll)} ⇄ {html.escape(rl)}</button>')
        panes.append(f'''<div class="tabpane{active}" id="t{idx}"><div class="compare">
          <div class="pane left"><h2 class="doc-title">{html.escape(ll)}</h2><div class="content">{''.join(lparts)}</div></div>
          <div class="pane right"><h2 class="doc-title">{html.escape(rl)}</h2><div class="content">{''.join(rparts)}</div></div>
        </div></div>''')
    return tabs, panes

CSS = """
* { box-sizing: border-box; }
body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; color:#1a1a1a; }
header { position:sticky; top:0; z-index:10; background:#1f2937; color:#fff; padding:10px 16px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
header h1 { font-size:15px; margin:0; font-weight:600; }
.tabs { display:flex; gap:8px; flex-wrap:wrap; }
.tab-btn { background:#374151; color:#d1d5db; border:none; padding:6px 14px; border-radius:6px; cursor:pointer; font-size:13px; }
.tab-btn.active { background:#2563eb; color:#fff; }
.btn-toggle { background:#0ea5e9; color:#fff; border:none; padding:6px 14px; border-radius:6px; cursor:pointer; font-size:13px; }
.btn-toggle.active { background:#16a34a; }
.legend { margin-left:auto; font-size:12px; color:#9ca3af; display:flex; gap:14px; }
.legend .sw { display:inline-block; width:11px; height:11px; border-radius:2px; vertical-align:middle; margin-right:4px; }
.legend .add { background:#16a34a; } .legend .del { background:#dc2626; }
.tabpane { display:none; }
.tabpane.active { display:block; }
.compare { display:flex; height:calc(100vh - 52px); }
.pane { flex:1 1 50%; overflow:auto; padding:20px 28px; }
.pane.left { border-right:2px solid #e5e7eb; background:#fafafa; }
.pane.right { background:#fff; }
.doc-title { position:sticky; top:0; background:inherit; margin-top:0; padding:8px 0; font-size:14px; color:#6b7280; border-bottom:1px solid #e5e7eb; }
.content { line-height:1.6; font-size:14px; }
.content h1 { font-size:22px; } .content h2 { font-size:18px; border-bottom:1px solid #eee; padding-bottom:4px; }
.content h3 { font-size:16px; } .content a { color:#2563eb; }
.content code { background:#f3f4f6; padding:1px 4px; border-radius:3px; font-size:13px; }
.content hr { border:none; border-top:1px solid #e5e7eb; margin:18px 0; }
.content ul, .content ol { padding-left:22px; }
.block { margin:0 0 12px 0; padding:4px 10px; border-left:4px solid transparent; border-radius:3px; }
.block.chg-add { background:#ecfdf5; border-left-color:#16a34a; }
.block.chg-del { background:#fef2f2; border-left-color:#dc2626; }
body.only-changes .block.unchanged { display:none; }
.w-add { background:#86efac; border-radius:2px; }
.w-del { background:#fca5a5; border-radius:2px; text-decoration:line-through; }
table.md-table { border-collapse:collapse; width:100%; margin:6px 0; font-size:13px; }
table.md-table th, table.md-table td { border:1px solid #e5e7eb; padding:4px 8px; text-align:left; vertical-align:top; }
table.md-table th { background:#f3f4f6; }
table.diff { width:100%; border-collapse:collapse; font-family:ui-monospace,Menlo,Consolas,monospace; font-size:13px; }
table.diff th { background:#1f2937; color:#fff; padding:6px 10px; text-align:left; }
table.diff td { padding:4px 8px; vertical-align:top; border-bottom:1px solid #eee; white-space:pre-wrap; }
.diff_add { background:#dcfce7; } .diff_chg { background:#fef9c3; } .diff_sub { background:#fee2e2; }
"""

def build(pairs, diff_mode):
    if diff_mode:
        tabs, panes = [], []
        for idx, (ll, lf, rl, rf) in enumerate(pairs):
            active = ' active' if idx == 0 else ''
            L = read_text(lf).splitlines(); R = read_text(rf).splitlines()
            table = difflib.HtmlDiff(wrapcolumn=120).make_table(L, R, html.escape(ll), html.escape(rl))
            table = table.replace('<table', '<table class="diff"', 1)
            tabs.append(f'<button class="tab-btn{active}" data-tab="t{idx}">{html.escape(ll)} ⇄ {html.escape(rl)}</button>')
            panes.append(f'<div class="tabpane{active}" id="t{idx}"><div style="padding:16px">{table}</div></div>')
        return tabs, panes
    return build_visual(pairs)

def main():
    ap = argparse.ArgumentParser(description="doc-compare: side-by-side markdown comparison with change highlighting")
    ap.add_argument('--pair', action='append', required=True,
                   help='ЛеваяМетка|левый_файл|ПраваяМетка|правый_файл (префикс gh: для GitHub)')
    ap.add_argument('--diff', action='store_true', help='режим подсветки изменений (difflib, построчно)')
    ap.add_argument('--out', default='/tmp/doc_compare.html')
    ap.add_argument('--no-open', action='store_true')
    args = ap.parse_args()
    pairs = []
    for p in args.pair:
        parts = p.split('|')
        if len(parts) != 4:
            sys.exit(f"[doc-compare] bad --pair (need 4 parts): {p}")
        pairs.append(tuple(parts))
    tabs, panes = build(pairs, args.diff)
    js = """document.querySelectorAll('.tab-btn').forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('.tab-btn').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.tabpane').forEach(p=>p.classList.remove('active'));b.classList.add('active');document.getElementById(b.dataset.tab).classList.add('active');});});
document.getElementById('onlyChg').addEventListener('click',function(){document.body.classList.toggle('only-changes');this.classList.toggle('active');this.textContent=document.body.classList.contains('only-changes')?'Показать всё':'Только изменения';});"""
    doc = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>doc-compare</title><style>{CSS}</style></head>
<body><header><h1>doc-compare</h1><div class="tabs">{"".join(tabs)}</div>
<button class="btn-toggle" id="onlyChg">Только изменения</button>
<div class="legend"><span><span class="sw add"></span>добавлено/изменено (справа)</span><span><span class="sw del"></span>удалено/изменено (слева)</span></div></header>
{"".join(panes)}<script>{js}</script></body></html>"""
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(doc)
    print(f"[doc-compare] written {args.out}")
    if not args.no_open:
        try:
            webbrowser.open('file://' + os.path.abspath(args.out))
            print("[doc-compare] opened in browser")
        except Exception as e:
            sys.stderr.write(f"[doc-compare] cannot open browser: {e}\n")

if __name__ == '__main__':
    main()
