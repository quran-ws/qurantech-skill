---
name: quran-svg-elements
description: Use when a web app needs word-level or mark-level interaction on printed Mushaf pages, such as clickable words, recitation word highlighting, word-by-word meanings or audio, cropping one word, or styling marks by name, using the Quran.ws quran-svg-elements page SVGs and JSON indexes (Hafs KFGQPC only, beta).
---

# quran-svg-elements

Follow the `qurantech` skill's adab rules (never alter or truncate Quranic text).

Printed Mushaf pages as SVG with the ink taken apart: each word is a `g.word` keyed `surah:ayah:word`, each diacritic is its own named `path`. Beside each page is a JSON sidecar. Status: Beta. Split so far: only `hafs-kfgqpc` (KFGQPC V4 1441H print, Hafs). 604 pages; 77,432 words; 436,398 marks.

## Pick the block
- Ayah-level regions, or an edition Elements has not split: `quran-svg`.
- Mobile or native rendering (SVG this dense performs poorly): `quran-engine`.
- Text, word records, numbering: `quran-text`. Rule spans: `quran-tajweed`.

## Fetch
- Newest version: `https://cdn.quran.ws/svg/elements/latest.json` (`version`, `manifest`).
- Pin one version: `https://cdn.quran.ws/svg/elements/<version>/pages/001.svg` and `.../index/by-page/001.json`. Folders are immutable; `manifest.json` lists sha256 per file.
- GitHub releases of `quran-ws/quran-svg-elements` are canonical (tarball about 108 MB).
- Fetch one page at a time; do not bundle pages in an app.

## Model
- Inject the SVG text into the DOM. `<img>` renders pixels and exposes nothing.
- Hierarchy: `g.line[data-line]` > `g.ayah-fragment[data-ayah-key]` > `g.word[data-word-key][data-rasm-uthmani]` > `path[data-kind=body|mark]`. Marks carry `data-mark` (closed vocabulary in `schema/mark-taxonomy.json`) and `data-mark-family`, a token list: match with `~=`.
- An ayah is one `g.ayah-fragment` per printed line. Use `querySelectorAll`; check the count against `data-ayah-fragments`.
- Read `data-decomposition` on the root: `word` means addressable, `ayah` means not split.
- Colour is `fill` on paths; there is no `<text>`.
- Sidecar per word: `word_key`, `ayah_key`, `line`, `box` (viewBox units), `rasm_uthmani` (display), `rasm`, `rasm_imlai`, `qpc`, `search` (match user input here).
- Corpus indexes (`words.json`, `pages.json`, `surahs.json`, `divisions.json`): see references.

## Join to other blocks
Join on the key, never on strings: encodings differ and equal-looking words compare unequal. The key equals `quran-text`'s `m.word(surah, ayah, index)`, and audio timing word numbers (1-based within the ayah). Elements has 77,432 words and quran-text 77,434; the sources say word boundaries differ for a handful of words, so spot-check away from page 1. Cause of the two-word gap: unknown.

## Example: make words clickable (JavaScript)
```js
const host = document.querySelector("#page");
host.innerHTML = await (await fetch(`${BASE}/pages/001.svg`)).text();
const svg = host.querySelector("svg");
svg.removeAttribute("width"); svg.removeAttribute("height");
svg.style.cssText = "height:70vh;width:auto";
svg.addEventListener("click", (e) => {
  const w = e.target.closest("g.word");
  if (w) onWord(w.dataset.wordKey, w.closest("g.ayah-fragment").dataset.ayahKey);
});
```
For touch, give `g.word path` a transparent stroke and `pointer-events:all`.

## Licence
CC BY 4.0 covers the decomposition, indexes and docs; attribution is waived inside a product and asked on republishing data. Page artwork and Quranic text belong to the King Fahd Glorious Quran Printing Complex (KFGQPC) and are used under its terms, reproduced in the repo `LICENSE`. The bundle `LICENSE` was a placeholder at last report: ask before redistributing artwork.

## Gotchas
- Root `data-mushaf` is `hafs-kfqc` but indexes say `hafs-kfgqpc`. Key on `data-edition` or the file loaded.
- `data-ayah-total` (6236) is per edition, not a constant.
- Path order inside a word is not reading order.

Detail: `references/format.md`.
