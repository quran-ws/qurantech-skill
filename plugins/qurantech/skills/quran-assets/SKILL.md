---
name: quran-assets
description: Use when a Quran app or site needs Mushaf-style ornaments around text - surah header banners, ayah marker roundels, page frames or borders - as recolourable SVG, or when choosing which ornament may be shipped under its licence (OFL font markers vs provisional scan assets).
---

# Quran Assets

Follow the `qurantech` skill's adab rules (never alter or truncate Quranic text). These files hold no Quranic text; the text comes from Quran Text and sits in a slot.

## What it is
Beta library of 71 SVG assets in three types: `surah-headers`, `page-frames`, `ayah-markers`. Two lineages: `scan` (24 assets, 8 of each type, traced from eight printed mushafs) and `font` (47 ayah markers from the U+06DD glyph of Arabic fonts). Repo: `quran-ws/quran-assets`.

## Read catalog.json
`catalog.json` is the contract. Each entry in `assets[]` has `id` (`<type>/<style>`), `type`, `style`, `lineage`, `riwayah`, `viewBox`, `variants` (`color`, `mono`, and `line` for scans), `palette`, `slots` (`role`, x, y, w, h, cx, cy), `symmetry`, `sources`, `license` (`id`, `status`, `attribution`, `note`). Frames may add `slices`. Filter by `type` and `license.status`, never by lineage alone.

## Licence: check before shipping
- Font markers: 40 are `OFL-1.1`, `confirmed` - shippable; the OFL text and the family notice must travel with them (`dist/LICENSES.md`, `sources[].license`).
- 7 font markers (designs 014-020) are `unverified`, `pending` - assert no licence; exclude.
- All 24 scan assets are `CC-BY-NC-SA-4.0`, `provisional`: publisher ornaments, permission still being settled. Do not ship them in a commercial product until cleared; otherwise attribute the mushaf and archive item from `sources`.
- Read each asset's `license` field at build time and fail on anything not `confirmed` unless the project has cleared it.

## Not published yet
The README says `# not published yet — read from assets/ in the repository`. Vendor files from the repo; pin the commit.

## Use and recolour
Inline the SVG (an `<img>` blocks CSS). The root has a `viewBox` of height 100 and no width/height; size it with CSS. Each drawable group has matching `class` and `data-part`: `slot`, `c1`..`cN`, `line`. Set `fill` on `c*`, `stroke` on `line`, leave `slot` transparent; c1 is often paper, so do not map it dark. `data-slot` is `x y w h` in viewBox units: divide by the viewBox to get percentages and overlay your text there.

## Choose the right block
Complete printed pages, letters included: use Quran SVG. Quranic text: Quran Text.

## Cautions
- Ayah number: write the edition's own count (docs cite 255 in Hafs, 253 in Warsh); size it from slot height or `r`, not width.
- Scan assets key by printing (`mushaf-hafs-madinah-mumtaza`, `-kabir`, `-adi`, `mushaf-douri`, `-sousi`, `-qalon`); these spellings differ from quran-text keys (duri, susi, qalun).
- `mushaf-hafs-madinah-kabir` frame has no `slices`; scale its `color.svg`.
- Inline several assets only with a build after commit 5843b12 (unique `<use>` ids).

## Example
```js
const cat = await (await fetch("catalog.json")).json();
const marker = cat.assets.find(a => a.type === "ayah-markers" && a.license.status === "confirmed");
const host = document.querySelector("#roundel");
host.innerHTML = await (await fetch(marker.variants.color)).text();
const svg = host.querySelector("svg");
svg.style.width = "2rem";
const [, , W, H] = svg.getAttribute("viewBox").split(/\s+/).map(Number);
const [x, y, w, h] = svg.getAttribute("data-slot").split(/\s+/).map(Number);
svg.querySelector('[data-part="c3"]')?.setAttribute("fill", "#15705D");
// overlay the edition's ayah number at (x/W, y/H, w/W, h/H) as percentages
```

More: `references/catalog.md`.
