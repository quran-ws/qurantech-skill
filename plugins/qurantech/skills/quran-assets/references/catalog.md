# Quran Assets catalogue detail

Sources: quran-ws/quran-assets README and catalog.json (generated 2026-09-11, schema `quran-assets/catalog@1`, count 71); quran.ws/docs/reference/quran-assets, /docs/build/assets, /docs/reference/licensing.

## Counts (from catalog.json)
| type | lineage | license.id | status | n |
|---|---|---|---|---|
| ayah-markers | font | OFL-1.1 | confirmed | 40 |
| ayah-markers | font | unverified | pending | 7 |
| ayah-markers | scan | CC-BY-NC-SA-4.0 | provisional | 8 |
| page-frames | scan | CC-BY-NC-SA-4.0 | provisional | 8 |
| surah-headers | scan | CC-BY-NC-SA-4.0 | provisional | 8 |

## Entry fields
`id`, `type`, `style`, `lineage`, `units` (normalized-100), `riwayah` (null for fonts), `viewBox`, `aspect`, `variants`, `source_crop`, `palette` (name, hex; the `line` entry has `stroke: true`), `stroke_widths_px`, `slots`, `symmetry`, `sources`, `license`, `pipeline_commit`. Font entries add `font` (upem, advance, upem_scale, codepoint, glyph). Frames with tiling add `slices` (files, corner, repeat, corner_mode, reconstruction_iou).
`license` has `id`, `status`, `attribution`, `note`. Font `sources[]` carry the family and its own `license` (copyright, reserved_font_names, url).

## Files per asset (assets/<type>/<style>/)
`color.svg`, `mono.svg` (currentColor), `line.svg` (scan only), `meta.json`, scan crops (`source.*`, `clean.*`), font `source.svg`, frame `slices/` (`corner.svg`, `edge-h.svg`, `edge-v.svg`). Variants are separate drawings, not filters.
The 47 font markers also ship as one PUA font, `dist/fonts/AyahMarkers.otf`/`.ttf`, U+E000-U+E02E, with `dist/fonts/font-map.json`. Useful for text runs.

## Root attributes
`data-style`, `data-lineage`, `data-asset`, `data-variant`, `data-symmetry`, `data-slot`; scans add `data-mushaf` and `data-source-*`; fonts add `data-source-font`, `data-source-glyph`. Symmetry: 4 = quadrant mirrored (all headers), 2 = scan markers, 1 = font markers.
Scan `color.svg`: `slot`, `c1..cN`, `line`. Font `color.svg`: `c1..cN` only (no slot group, no line). Colours are presentation attributes, so CSS beats them.

## Slots
Roles seen: `surah-name`, `ayah-number`, `text-area`. Font marker slots add `r`. Slot is sized for 1-3 digits in markers.

## Frame tiling
Seven of eight frames have `slices`; compose corner (mirrored) plus repeating `edge-h`/`edge-v` in frame units; leave the `text-area` margin.

## Licence notes
Scan note (catalogue): "Released non-commercially while written permission is sought." Not legal advice. `status: pending` keeps the npm package private and `qa dist --exclude-unconfirmed` omits those markers. Licensing page: MIT toolchain, CC BY 4.0 for catalogue and docs; ornaments carry their own terms per asset.

## Unverified
- Whether any package is now published (README and site say not yet).
- Whether scan permissions have been cleared since 2026-09-11; re-read catalog.json.
- Site's `assets-index.json` (demo copy) filenames differ from repo paths; the repo `variants` paths were used here.
