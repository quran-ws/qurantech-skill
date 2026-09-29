---
name: quran-svg
description: Use when displaying printed Mushaf pages as SVG in a website or app, making ayahs on a page tappable or highlighted, fetching Quran.ws quran-svg files, cdn.quran.ws/svg pages, ayahPolygon hit-regions, per-page polygon JSON, or choosing between quran-svg and its sibling blocks. Keywords - mushaf page SVG, ayah polygon, hit-test, highlight ayah, KFQC, riwayah pages.
---

# quran-svg

Vector Mushaf pages (glyph outlines, no text) with one clickable polygon per ayah. Five riwayat ship: hafs, warsh, qalon, douri, shubah; each has 604 pages (KFQC edition, folder `kfqc`). Maturity: labelled Stable; the set of mushafs grows by contribution, not on a schedule.

Follow the `qurantech` skill's adab rules (never alter or truncate Quranic text).

## Pick the block
- Whole page plus tap-to-ayah: this block.
- Single word or mark: `quran-svg-elements`. Text of an ayah: `quran-text`. Fast native or phone rendering: `quran-engine`.
- Converting ayah numbers between counts: `qiraat-ayah-map`. Tajweed spans: `quran-tajweed`.

## Get the files
- One page: `https://raw.githubusercontent.com/quran-ws/quran-svg/main/mushafs/hafs/kfqc/svg/001.svg` (three-digit page; `json/001.json` holds polygons; `svg-br/` holds Brotli copies).
- CDN, immutable and version-pinned: `https://cdn.quran.ws/svg/pages/v1.1.1/hafs-kfqc/001.svg` and `.json` (editions `hafs-kfqc`, `warsh-kfqc`, `qalon-kfqc`, `shubah-kfqc`, `douri-kfqc`). Pin a version or commit, never `main`.
- One mushaf: `git clone --depth 1 --filter=blob:none --sparse ...` then `git sparse-checkout set mushafs/hafs/kfqc`. Take one mushaf this way; a plain clone is 5.29 GiB.
- Pages holding two surahs also have `106-surah4.svg` (surah part only).

## Facts to apply
- Inline the SVG (fetch, set innerHTML) so you can style and hit-test polygons. Pages declare `viewBox` only; read it from the file.
- Each ayah is `<path class="ayahPolygon" surah="2" ayah="6" number="002006" d="...">`. Read `surah` and `ayah`; ignore `id="verse-N"` (global across the five mushafs).
- Set `pointer-events: none` on glyph paths after mounting. Polygons sit above glyphs in Hafs and below them in the other four.
- Highlight by raising `fill-opacity` from 0. `fill: none` disables taps.
- JSON `polygon` is path data on pages 3+, a bare `x,y x,y` list on pages 1-2. Handle both (see references/format.md).
- Ayah numbers follow each mushaf's own counting (Hafs 6,236 polygons, Warsh and Qalon 6,214). Store the mushaf key beside every page number and ayah key; page N differs per mushaf.
- Pages 1-2: the drawn ink fills a fraction of the declared box; fit with `getBBox()`.
- No text in the files. Fetch words from `quran-text` by reference.

## Minimal example (TypeScript)
```ts
const RAW = "https://raw.githubusercontent.com/quran-ws/quran-svg/main/mushafs";
const res = await fetch(`${RAW}/hafs/kfqc/svg/042.svg`);
host.innerHTML = await res.text();
const svg = host.querySelector("svg")!;
svg.querySelectorAll("path:not(.ayahPolygon)").forEach(p => (p as SVGElement).style.pointerEvents = "none");
const poly = svg.querySelectorAll<SVGPathElement>(".ayahPolygon");
poly.forEach(p => {
  const hit = p.getAttribute("surah") === "2" && p.getAttribute("ayah") === "255";
  p.setAttribute("fill", "#15705D");
  p.setAttribute("fill-opacity", hit ? "0.35" : "0");
});
```
A multi-line ayah is one path with several subpaths; one element covers all its lines.

## Licence
Polygon layer, per-page JSON, `surah.json`, `markers.json`: CC BY 4.0, attribution waived inside a product; `tools/` MIT. Page artwork belongs to the King Fahd Glorious Qur'an Printing Complex (free digital use; only commercial physical printing is restricted). Read the repo's `NOTICE.md` before redistributing.

## Gotchas
- SVG pages are heavy on phones (hundreds of KB); use `svg-br` or `quran-engine`.
- Find a reference's page by binary search over `json/NNN.json`, or `markers.json` (its `ayah` is a running index, not an ayah number). Details in references/format.md.
