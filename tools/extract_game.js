'use strict';
/* extract_game.js: runs the FAL-125 game headless and dumps what the Story Archive needs.
   Usage: node tools/extract_game.js <game repo folder> <work folder>
   Writes into <work folder>: game.json (characters + worlds), gallery.json (extra pictures per
   character), emb/<key>.<ext> (each fighter's sprite) and alt/<name>.<ext> (poses, forms, skins). */
const path = require('path'), fs = require('fs'), vm = require('vm');
const GAME = path.resolve(process.argv[2] || '.');
const OUT = path.resolve(process.argv[3] || 'work');
const html = fs.readdirSync(GAME).filter(f => /^fal125_battle_prototype-v\d+\.html$/.test(f))
  .sort((a, b) => +b.match(/v(\d+)/)[1] - +a.match(/v(\d+)/)[1])[0];
if (!html) throw new Error('No fal125_battle_prototype-vNNN.html in ' + GAME);
const { load } = require(path.join(GAME, 'tools', 'fal125_headless.js'));
const L = load({ html: path.join(GAME, html) });
const ev = s => { try { return vm.runInContext(s, L.sb); } catch (e) { return undefined; } };

const C = ev('CHARACTERS'), SK = ev('SKILLS'), AL = ev('ARC_LORE') || {}, RL = ev('RL') || {}, E = ev('EMBED') || {};
const ES = ev('typeof EMBED_SKIN!=="undefined"?EMBED_SKIN:{}') || {}, SKINS = ev('typeof SKINS!=="undefined"?SKINS:{}') || {};
const W = ev('WORLD_DATA'), EN = ev('ENEMIES') || {};
fs.mkdirSync(path.join(OUT, 'emb'), { recursive: true });
fs.mkdirSync(path.join(OUT, 'alt'), { recursive: true });

const chars = C.map(c => ({
  key: c.key, name: c.name, id: c.id, role: c.role, type: c.type, title: c.title, color: c.color, build: c.build,
  stats: { hp: c.hp, atk: c.atk, def: c.def, spd: c.spd }, passive: c.passive, ident: c.ident || '',
  skills: (c.skills || []).map(k => SK[k] ? { name: SK[k].name, desc: SK[k].desc || '' } : { name: k, desc: '' }),
  archive: (AL[c.key] || []).filter(s => s != null && String(s).trim() && String(s).trim() !== 'null')
    .map(s => String(s).replace(/\[\[|\]\]/g, '').replace(/\{id\}/g, 'FAL-' + c.id)),
  recruit: (RL[c.key] || []).map(a => a && a[0]).filter(Boolean)
}));
const worlds = W.map((w, i) => ({ index: i, name: w.name, side: !!w.side, preview: !!w.preview, floors: w.floors || [],
  bosses: (w.bosses || []).map(k => (EN[k] && EN[k].name) || k), win: w.win || '', note: w.note || '' }));
fs.writeFileSync(path.join(OUT, 'game.json'), JSON.stringify({ version: html.match(/v(\d+)/)[1], chars, worlds }));

const save = (dir, name, data) => {
  if (typeof data !== 'string' || !data.startsWith('data:image/')) return null;
  const m = data.match(/^data:image\/(\w+);base64,(.*)$/); if (!m) return null;
  fs.writeFileSync(path.join(OUT, dir, name + '.' + m[1]), Buffer.from(m[2], 'base64')); return name;
};
const copy = (name, p) => { if (!fs.existsSync(p)) return null; fs.copyFileSync(p, path.join(OUT, 'alt', name + '.png')); return name; };
for (const c of C) save('emb', c.key, E[c.key]);

/* Extra forms the game uses for a fighter. Add a line here when the game gets a new one. */
const FORMS = {
  shatter: [['shatter_active', 'Active form', 'form']], lycion: [['lycion_rage', 'Rage Form', 'form']], velara: [['velara_sinner', 'Sinner form', 'form']],
  hole: [['hole_devil', 'Devil Form', 'form']], bonesaw: [['bonesaw_friend', 'His friend', 'form'], ['@bonesaw_uzi', 'With the uzi', 'form']],
  fuja: [['pro_fuja_h', 'Prologue look (temporary art)', 'form']], radiant: [['pro_radiant_h', 'Prologue look (temporary art)', 'form']],
  clownx25: [['clown_x25', 'Fused, enemy form', 'form'], ['clown_x25a', 'Armored half (mini form)', 'mini'], ['clown_x25doll', 'The doll (mini form)', 'mini'], ['clown_x25_unfused', 'Unfused (both minis side by side)', 'mini']],
  clownx2: [['clown_x2', "Enemy form (Clown's Massacre)", 'form']], clownx33: [['clown_x33', "Enemy form (Clown's Massacre)", 'form']],
  vendor: ['show', 'greet', 'offer', 'thanks', 'poor', 'shock', 'sly', 'full'].map(p => ['kp_vendor_' + p, 'Shop pose: ' + p, 'pose'])
};
const gallery = {};
for (const c of C) {
  const g = [];
  for (const [suf, lab] of [['_atk', 'Attack pose'], ['_ko', 'Knocked out']]) { const n = save('alt', c.key + suf, E[c.key + suf]); if (n) g.push({ label: lab, kind: 'pose', img: n }); }
  const h = copy(c.key + '_heal', path.join(GAME, 'sprites', c.key + '_heal.png')); if (h) g.push({ label: 'Heal pose (not used in the game yet)', kind: 'pose', img: h });
  for (const [k, lab, kind] of (FORMS[c.key] || [])) {
    const n = k[0] === '@' ? copy(k.slice(1), path.join(GAME, 'sprites', k.slice(1) + '.png')) : (save('alt', k, E[k]) || copy(k, path.join(GAME, 'sprites', k + '.png')));
    if (n) g.push({ label: lab, kind, img: n });
  }
  for (const s of (SKINS[c.key] || [])) {
    if (s.art) { const n = save('alt', 'skin_' + s.art, ES[s.art]) || copy('skin_' + s.art, path.join(GAME, 'sprites', 'skins', s.art + '.png')); if (n) g.push({ label: s.name, kind: /drawing|scribble/.test(s.art) ? 'drawing' : 'skin', img: n }); }
    else if (s.filter && s.id !== 'default') g.push({ label: s.name, kind: 'recolour', filter: s.filter });
  }
  if (g.length) gallery[c.key] = g;
}
fs.writeFileSync(path.join(OUT, 'gallery.json'), JSON.stringify(gallery));
console.log(`extract_game: ${html}, ${chars.length} characters, ${worlds.length} worlds, ${Object.keys(gallery).length} with extra pictures`);
