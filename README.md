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

To turn on GitHub Pages: repository Settings > Pages > Deploy from a branch > pick the branch and `/ (root)`.

## Files

- `index.html`: the whole site.
- `data/universe.json`: characters and worlds, taken from the game (v288) and `FAL125_Character_Book.xlsx`.
- `sprites/*.webp`: small copies of the game sprites.
- `vendor/anthropic-sdk-1.4.0.mjs`: the official Anthropic SDK in one file, used only in API-key mode.
