# quran-svg format detail

Sources: quran-ws/quran-svg docs/FORMAT.md, GETTING-THE-FILES.md, PROVENANCE.md; quran.ws/docs/reference/quran-svg and /docs/build/highlight-ayah.

## Layout
`mushafs/<riwayah>/<edition>/{svg,svg-br,json}/`. Editions today: `hafs`, `warsh`, `qalon`, `douri`, `shubah`, all `kfqc`. Per mushaf: 722 SVG files (604 pages plus 118 surah-specific variants) and 724 JSON files (adds `surah.json`, `markers.json`).
Sizes (Hafs): page 1 is 196,304 bytes as SVG, 32,707 as `.svg.br`; per-page JSON runs 132 to 6,039 bytes. Whole Hafs mushaf: 414 MB `svg/`, 72 MB `svg-br/`, 3.7 MB `json/`. Releases also carry `<riwayah>-kfqc-svg.zip` and `-svg-br.zip`.

## Per-page JSON entry
`{"surahNumber":2,"ayahNumber":6,"x":265.17,"y":64.13,"polygon":"..."}`. The polygon shares the SVG's unflipped root user space with no rescaling.

## Two polygon shapes
Path data on pages 3+ (one rectangular subpath per printed line the ayah touches); bare point list on pages 1-2. In the SVG, `d` is always path data.
```js
function polygonToPath(p) {
  if (p.trimStart().startsWith('M')) return p;
  const n = p.match(/-?\d+(?:\.\d+)?/g).map(Number), pts = [];
  for (let i = 0; i < n.length; i += 2) pts.push(`${n[i]} ${n[i+1]}`);
  return `M ${pts.join(' L ')} Z`;
}
```
Extracting all numbers in pairs is safe for a bounding box, not for an outline (it welds subpaths).

## Stacking order and structure
Root children: page content inside `<g transform="matrix(1.3333 0 0 -1.3333 ...)">` (y flipped, contains `#ayah_markers` and `#content`) and the polygons as unflipped siblings. Hafs: polygons after glyphs (on top). Warsh, Qalon, Douri, Shubah: before glyphs (beneath). Consistent on every page within a mushaf. To crop an ayah, put `clip-path` on a new untransformed wrapper `<g>`, not on the transformed group.

## viewBox
Pages 3-604: `0 0 345 550` (Warsh and Qalon: `-6 0 345 550`). Pages 1-2: 345 x 550 with a per-mushaf origin (Hafs `-53.3109 -198.4777 345 550`). Surah variants are height-cropped (`106-surah4.svg` is `0 0 345 188.58`). Always read it from the file.

## Numbering
`surah` + `ayah` attributes are the mushaf's own counting. `number` is SSSAAA. `id="verse-N"` is global over all five mushafs (page 1 is verse-1 in Hafs, verse-18709 in Warsh); do not parse it. `markers.json` is a flat list in reading order whose `ayah` is a running index 1..N; convert a reference with cumulative `ayahCount` from the same mushaf's `surah.json`. Use `quran-ws` `qiraat-ayah-map` to translate references between counts.

## Locating a page
`surah.json` (114 entries, includes `pageNumber`, `ayahCount`) bounds the search; binary-search `json/NNN.json` for the surah:ayah pair (documented as at most six requests over all Hafs references).

## Provenance
Traced from the KFQC "Digital Mushaf" Illustrator bundles (604 `.ai` pages each). Shipped SVGs drop the frame, running header and page number, re-crop to the text block, and redraw ayah markers. Only al-Duri was visually checked against the source; the other four were checked for structure only. Al-Duri `markers.json` has 6218 entries versus 6217 in quran-text (open issue #21).

## Unverified
`manifest.json` and `latest.json` are described in the repo README under `cdn.quran.ws/svg/pages/`, but both returned 404 when fetched at the paths given. Confirm before depending on them.
