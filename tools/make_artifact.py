"""make_artifact.py: prepares the Claude-app copy of the site.

Usage: python3 tools/make_artifact.py <output folder> [<git commit last published>]
Writes <output>/fal125-story-archive.html (index.html without the outer <html>/<head>/<body>,
which the Artifact publish adds) and <output>/files-N.json: the data and picture files to publish,
in groups of at most 250. With a commit, only files changed since that commit are listed.
"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.abspath(sys.argv[1]); since = sys.argv[2] if len(sys.argv) > 2 else ''
os.makedirs(out, exist_ok=True)
s = open(os.path.join(ROOT, 'index.html'), encoding='utf8').read()
s = s.replace('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n', '', 1)
s = s.replace('</style>\n</head>\n<body>\n', '</style>\n\n', 1).replace('\n</body>\n</html>\n', '\n')
assert not s.startswith('<!doctype') and '</body>' not in s, 'index.html layout changed; update make_artifact.py'
open(os.path.join(out, 'fal125-story-archive.html'), 'w', encoding='utf8').write(s)
if since:
    names = subprocess.check_output(['git', '-C', ROOT, 'diff', '--name-only', '--diff-filter=AM', since, 'HEAD', '--', 'data', 'sprites']).decode().split()
else:
    names = ['data/universe.json'] + sorted(os.path.relpath(os.path.join(d, f), ROOT) for d, _, fs in os.walk(os.path.join(ROOT, 'sprites')) for f in fs if f.endswith('.webp'))
names = [n for n in names if os.path.exists(os.path.join(ROOT, n))]
for old in [f for f in os.listdir(out) if f.startswith('files-')]:
    os.remove(os.path.join(out, old))
groups = [names[i:i + 250] for i in range(0, len(names), 250)] or [[]]
for i, g in enumerate(groups, 1):
    json.dump([{'path': n} for n in g], open(os.path.join(out, 'files-%d.json' % i), 'w'))
print('make_artifact: page written, %d files in %d group(s)' % (len(names), len(groups)))
