# FAL-125 Story Archive

A website for the FAL-125 universe:

- **Files**: every character file (136 from the game and the Character Book, plus your new ones). Search, filter, notes.
- **Lore**: the whole story in order, from the founding of Fal-125 to the Climax, with every world's scenes. Add your own entries in the right place.
- **Review**: upload a drawing or describe a character. Claude reviews it honestly, finds similar characters you already have, and says where it fits.
- **Abilities**: an ability generator that avoids abilities you already have, with a cost and a battle-game version.
- **Critic**: honest criticism of story ideas, checked against all your characters and lore.

Inspirations always come with links.

## Two ways to use it

1. **In the Claude app** (the published Artifact): uses your Claude account, no key needed. Your work is saved in your Claude account. Claude cannot search the web there, so links open a web search.
2. **As a normal website** (GitHub Pages, or open `index.html` through any web server): add a Claude API key in Setup. Claude then searches the web and shows the pages it used. Your work is saved in that browser; use Export a backup.

The main drawings now show on the GitHub Pages copy too: `data/art.json` is a snapshot of all your drawing records (names, dates, notes, picture centers), with the pictures in `drawings/` (small card versions in `drawings/thumb/`). In the Claude app the live records win. The snapshot is refreshed by asking Claude to export it.

To turn on GitHub Pages: repository Settings > Pages > Deploy from a branch > pick the branch and `/ (root)`.

## Files

- `index.html`: the whole site.
- `data/universe.json`: characters and worlds, taken from the game (v288) and `FAL125_Character_Book.xlsx`.
- `sprites/*.webp`: small copies of the game sprites.
- `vendor/anthropic-sdk-1.4.0.mjs`: the official Anthropic SDK in one file, used only in API-key mode.

## Pictures

- Every file has a **Main drawings** section: upload your own drawings of the character, rename them, and pick which one is the main one. The main drawing becomes the file's picture (you can switch back to the game sprite). On the Files page, "Main drawings" in the picture menu shows them on the cards.
- **Sprites in the game** shows every extra picture the game has for that character: forms (Lycion's Rage Form, Hole's Devil Form, Velara's Sinner form...), mini forms (Clown.x25's armored half and doll), attack and knocked-out poses, drawings already in the game, skins and recolours. Click one to see it big.
- These live in `sprites/alt/`.
- **Sprite versions**: when a character's game sprite was replaced, every version is kept as V1, V2... (`sprites/ver/`, taken from the game's history, v258 to v289). Pick a version under the In game tab.
- **Drawing versions**: give each drawing a date ("Set date", or the date Claude reads from the sheet). When a character has several drawings, buttons with the years (2022, 2024, 2026...) above the big picture switch between the old and new versions.
- On the Files cards a drawing is centred on the character. The site finds the character by itself; use "Center on card" under a drawing to fix it by clicking the middle of the character.

## drawings/

The author's main drawings (character sheets), kept here as a backup copy, and `notes.json` with the notes written on each sheet. In the Claude app version they are uploaded into the archive as the main drawing of each file, and their notes are the ability text.
