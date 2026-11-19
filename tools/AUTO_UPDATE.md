# Automatic update from the game

A scheduled Claude task runs this twice a day. Steps, in order:

1. Work in the Story-Oc repository on branch `ccr-268c17b7-m1nixn` (the site's main branch):
   `git fetch origin ccr-268c17b7-m1nixn && git checkout ccr-268c17b7-m1nixn && git reset --hard origin/ccr-268c17b7-m1nixn`
2. Run `bash tools/update.sh` (it can take about 10 minutes when there is a new version).
   - If it prints `NO CHANGE`: stop. Reply in one line: "No new game version (still vNNN)."
3. Commit `data/` and `sprites/` with the message `Update from game vNNN` (plus the lines it printed:
   new characters, new sprite versions) and push to `ccr-268c17b7-m1nixn`.
4. Run `python3 tools/make_artifact.py <scratchpad>/artifact $(cat tools/last_published.txt)`.
5. Update the Claude page https://claude.ai/artifact/35wFUTHhoDhxQLzthGEs7N:
   - first read it with the Artifact tool (`action: "read"`, that url);
   - then publish `<scratchpad>/artifact/fal125-story-archive.html` with that `url`, and as `files` the list in
     `files-1.json` (paths are relative to the repository root, so pass `root` = the repository folder).
     If there is a `files-2.json`, publish again with the same url and that list. Do not pass `capabilities`.
6. Write `git rev-parse HEAD` into `tools/last_published.txt`, commit "Published vNNN to the Claude archive", push.
7. Reply with a short plain-English summary for the author: the new game version, new characters,
   characters with a new sprite version, and the link above.

Never change the author's own data in the page's database (drawings, notes, lore, reviews).
If a step fails, stop and report which step and the error, in plain words.
