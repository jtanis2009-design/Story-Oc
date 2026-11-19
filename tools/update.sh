#!/usr/bin/env bash
# update.sh: refresh the Story Archive from the newest FAL-125 game version.
#   bash tools/update.sh          only rebuilds when the game has a newer version than data/universe.json
#   bash tools/update.sh --force  always rebuilds
# Prints "NO CHANGE" or "UPDATED vOLD -> vNEW". Needs git, node, python3 with Pillow and openpyxl.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GAME_URL="https://github.com/jtanis2009-design/fal-125-project-game"
TMP="${TMPDIR:-/tmp}/fal125-archive-update"
mkdir -p "$TMP"

# newest game version, without downloading the game
NEW=$(git ls-remote "$GAME_URL" HEAD | cut -f1)
OLD_V=$(python3 -c "import json;print(json.load(open('$ROOT/data/universe.json'))['version'].split('v')[-1])" 2>/dev/null || echo 0)

rm -rf "$TMP/game"
GIT_LFS_SKIP_SMUDGE=1 git clone -q --depth 1 "$GAME_URL" "$TMP/game"
NEW_V=$(ls "$TMP/game" | sed -n 's/^fal125_battle_prototype-v\([0-9]*\)\.html$/\1/p' | sort -n | tail -1)
echo "game: v$NEW_V (commit ${NEW:0:7}), archive: v$OLD_V"
if [ "${1:-}" != "--force" ] && [ "$NEW_V" = "$OLD_V" ]; then echo "NO CHANGE"; exit 0; fi

# full history, but file contents only on demand (for V1, V2 ... sprites)
if [ -d "$TMP/hist/.git" ]; then git -C "$TMP/hist" fetch -q origin && git -C "$TMP/hist" reset -q --soft FETCH_HEAD
else rm -rf "$TMP/hist"; git clone -q --filter=blob:none --no-checkout "$GAME_URL" "$TMP/hist"; fi

rm -rf "$TMP/work"
cp "$ROOT/data/universe.json" "$TMP/universe-before.json" 2>/dev/null || true
node "$ROOT/tools/extract_game.js" "$TMP/game" "$TMP/work"
python3 "$ROOT/tools/build_data.py" "$TMP/game" "$TMP/hist" "$TMP/work" "$ROOT"
python3 - "$TMP/universe-before.json" "$ROOT/data/universe.json" <<'PY'
import json, sys
try: a = {c['key']: c for c in json.load(open(sys.argv[1]))['characters']}
except Exception: a = {}
b = {c['key']: c for c in json.load(open(sys.argv[2]))['characters']}
new = [b[k]['name'] for k in b if k not in a]
spr = [b[k]['name'] for k in b if k in a and b[k].get('sprite') and a[k].get('versions', []) != b[k].get('versions', [])]
gal = [b[k]['name'] for k in b if k in a and len(b[k].get('gallery', [])) != len(a[k].get('gallery', []))]
print('NEW CHARACTERS: ' + (', '.join(new) or 'none'))
print('NEW SPRITE VERSIONS: ' + (', '.join(spr) or 'none'))
print('CHANGED EXTRA PICTURES: ' + (', '.join(gal) or 'none'))
PY
echo "UPDATED v$OLD_V -> v$NEW_V"
