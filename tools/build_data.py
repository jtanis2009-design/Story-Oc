"""build_data.py: turns the game dump into the Story Archive's data.

Usage: python3 tools/build_data.py <game repo folder> <game history clone> <work folder> <Story-Oc folder>

Reads <work>/game.json, gallery.json, emb/, alt/ (from extract_game.js), the Character Book and the
story script from the game, and every past game version in the history clone (for V1, V2... sprites).
Writes data/universe.json, sprites/*.webp, sprites/alt/*.webp and sprites/ver/*.webp.
Needs Pillow and openpyxl.
"""
import base64, io, json, os, re, shutil, subprocess, sys
import openpyxl
from PIL import Image

GAME, HIST, WORK, OUT = [os.path.abspath(a) for a in sys.argv[1:5]]
G = json.load(open(os.path.join(WORK, 'game.json')))
GAL = json.load(open(os.path.join(WORK, 'gallery.json')))
html_name = next(f for f in sorted(os.listdir(GAME)) if re.match(r'fal125_battle_prototype-v%s\.html$' % G['version'], f))


def clean(v):
    return '' if v is None else str(v).strip()


def trimmed(im):
    im = im.convert('RGBA')
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def save_webp(im, rel, height, quality):
    im = trimmed(im)
    if im.height > height or rel.startswith('sprites/') and rel.count('/') == 1:
        im = im.resize((max(1, round(im.width * height / im.height)), height), Image.LANCZOS)
    os.makedirs(os.path.dirname(os.path.join(OUT, rel)), exist_ok=True)
    im.save(os.path.join(OUT, rel), 'WEBP', quality=quality, method=6)
    return rel


def sig(im):
    im = trimmed(im)
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    g = bg.convert('L').resize((24, 24))
    return list(getattr(g, 'get_flattened_data', g.getdata)())


def diff(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


# ---- Character Book ----
wb = openpyxl.load_workbook(os.path.join(GAME, 'data', 'FAL125_Character_Book.xlsx'), data_only=True)
ws = wb['Characters']
hdr = [c.value for c in ws[1]]
book = {}
for row in ws.iter_rows(min_row=2, values_only=True):
    d = dict(zip(hdr, row))
    if d.get('ID') is not None:
        book[int(d['ID'])] = d
BOOK_FIELDS = [('ability', 'Ability'), ('abilityPlus', 'Ability+'), ('containment', 'Containment Level'), ('scent', 'Scent'),
               ('threat', 'Threat LV'), ('bookType', 'Type'), ('awakened', 'Awakened'), ('notes', 'Notes'), ('source', 'Source')]

# ---- sprite versions from the game's history (V1, V2 ...) ----
keys = [c['key'] for c in G['chars']]
keyset = set(keys)
rx = re.compile(r'(?:EMBED\.([a-z0-9_]+)\s*=\s*|"([a-z0-9_]+)":\s*)"(data:image/[a-z]+;base64,[A-Za-z0-9+/=]+)"')
hist, lastraw, seen_ver = {}, {}, set()
commits = subprocess.check_output(['git', '-C', HIST, 'log', '--reverse', '--format=%h', '--', '*.html']).decode().split()
for c in commits:
    files = [f for f in subprocess.check_output(['git', '-C', HIST, 'ls-tree', '-r', '--name-only', c]).decode().split('\n')
             if re.match(r'fal125_battle_prototype-v\d+\.html$', f)]
    if not files:
        continue
    f = files[0]
    ver = re.search(r'v(\d+)', f).group(1)
    if ver in seen_ver:
        continue
    seen_ver.add(ver)
    text = subprocess.check_output(['git', '-C', HIST, 'show', f'{c}:{f}']).decode('utf8', 'ignore')
    found = {}
    for m in rx.finditer(text):
        k = m.group(1) or m.group(2)
        if k in keyset:
            found[k] = m.group(3)
    for k, d in found.items():
        if lastraw.get(k) == d:
            hist[k][-1]['last'] = ver
            continue
        lastraw[k] = d
        raw = base64.b64decode(d.split(',', 1)[1])
        s = sig(Image.open(io.BytesIO(raw)))
        L = hist.setdefault(k, [])
        if L and diff(L[-1]['sig'], s) < 7:      # tiny clean-ups are not a new version
            L[-1]['last'] = ver
            L[-1]['raw'] = raw
            continue
        L.append({'first': ver, 'last': ver, 'sig': s, 'raw': raw})
print('build_data: read %d game versions' % len(seen_ver))

# ---- fresh picture folders ----
for sub in ('sprites/alt', 'sprites/ver'):
    shutil.rmtree(os.path.join(OUT, sub), ignore_errors=True)
alt_files = {os.path.splitext(f)[0]: os.path.join(WORK, 'alt', f) for f in os.listdir(os.path.join(WORK, 'alt'))}

chars, seen_ids = [], set()
for c in G['chars']:
    b = book.get(int(c['id']))
    seen_ids.add(int(c['id']))
    c['book'] = {k: clean(b.get(src)) for k, src in BOOK_FIELDS} if b else None
    emb = next((os.path.join(WORK, 'emb', c['key'] + '.' + e) for e in ('webp', 'png', 'jpeg', 'jpg') if os.path.exists(os.path.join(WORK, 'emb', c['key'] + '.' + e))), None)
    c['sprite'] = save_webp(Image.open(emb), 'sprites/%s.webp' % c['key'], 220, 82) if emb else ''
    c['origin'] = 'game'
    vsigs, vers = [], []
    L = hist.get(c['key'], [])
    if len(L) > 1:
        for i, e in enumerate(L):
            im = Image.open(io.BytesIO(e['raw']))
            rel = save_webp(im, 'sprites/ver/%s_v%d.webp' % (c['key'], i + 1), 360, 86)
            vsigs.append(e['sig'])
            note = 'game v%s' % e['first'] + ('' if e['first'] == e['last'] else '–v%s' % e['last'])
            vers.append({'label': 'V%d' % (i + 1) + (' (now)' if i == len(L) - 1 else ''), 'note': note, 'src': rel})
    c['versions'] = vers
    if emb:
        vsigs.append(sig(Image.open(emb)))
    res, seen = [], []
    for it in GAL.get(c['key'], []):
        if 'img' not in it:
            res.append(it)
            continue
        src = alt_files.get(it['img'])
        if not src:
            continue
        im = Image.open(src)
        s = sig(im)
        if any(diff(s, x) < 7 for x in seen + vsigs):   # the same picture twice, or an old sprite kept as a skin
            continue
        seen.append(s)
        res.append({'label': it['label'], 'kind': it['kind'], 'src': save_webp(im, 'sprites/alt/%s.webp' % it['img'], 360, 84)})
    c['gallery'] = res
    chars.append(c)
for i, b in sorted(book.items()):
    if i in seen_ids:
        continue
    chars.append({'key': 'book%d' % i, 'name': clean(b.get('Name')), 'id': '%04d' % i, 'role': clean(b.get('Role (game)')), 'type': clean(b.get('Type')),
                  'title': '', 'color': '#888888', 'build': '', 'stats': None, 'passive': '', 'ident': '', 'skills': [], 'archive': [], 'recruit': [],
                  'sprite': '', 'origin': 'book', 'versions': [], 'gallery': [], 'book': {k: clean(b.get(src)) for k, src in BOOK_FIELDS}})
chars.sort(key=lambda c: int(c['id']))

# ---- story scenes ----
html = open(os.path.join(GAME, html_name), encoding='utf8').read()
s = html.index('const STORY_SCRIPT = [')
block = html[s:html.index('\n];', s)]


def lines_of(txt):
    out = []
    for m in re.finditer(r'`((?:[^`\\]|\\.)*)`', txt):
        t = m.group(1).replace('${T_()}', '[Tank]').replace('${H_()}', '[Healer]').replace('${D_()}', '[Damage]')
        out.append(re.sub(r'\$\{[^}]*\}', '…', t))
    return out


story = []
for p in re.split(r'\{\s*start\s*:', block)[1:]:
    mi, en = re.search(r'\bmid\s*:', p), re.search(r'\bend\s*:', p)
    seg = {'start': p[:mi.start()] if mi else p, 'mid': p[mi.start():en.start()] if mi and en else '', 'end': p[en.start():] if en else ''}
    story.append({k: [{'place': m.group(2), 'lines': lines_of(m.group(3))}
                      for m in re.finditer(r"\[\s*(['\"`])(.+?)\1\s*,\s*\[(.*?)\]\s*\]", t, re.S)] for k, t in seg.items()})
worlds = G['worlds']
for i, w in enumerate(worlds):
    w['story'] = story[i] if i < len(story) and not w['side'] and not w['preview'] else None

json.dump({'version': 'FAL-125 v' + G['version'], 'characters': chars, 'worlds': worlds},
          open(os.path.join(OUT, 'data', 'universe.json'), 'w'), ensure_ascii=False, indent=0)
print('build_data: v%s, %d characters, %d with sprite versions, %d gallery pictures' % (
    G['version'], len(chars), sum(1 for c in chars if c['versions']), sum(len([g for g in c['gallery'] if 'src' in g]) for c in chars)))
