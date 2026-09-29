# quran-svg-elements format detail

Sources: quran.ws/docs/reference/quran-svg-elements, /docs/build/clickable-words, repo README, and files inspected at https://cdn.quran.ws/svg/elements/v1.1.2/ (page 001).

## CDN layout (manifest v1.1.2)
`manifest.json` keys: version, release, edition (`hafs-kfgqpc`), base, encoding (`identity`), files[name, bytes, sha256].
Files: `pages/NNN.svg` (604), `index/by-page/NNN.json` (604), `index/words.json`, `pages.json`, `surahs.json`, `divisions.json`. The release tarball also has `schema/FORMAT.md`, `schema/mark-taxonomy.json`, `schema/*.schema.json`, `VERSION.json`, `CHECKSUMS.txt`.
The reference page still says there is no per-file host; the README and CDN show one exists. Prefer the CDN.
Verify tarball: `shasum -a 256 --ignore-missing -c CHECKSUMS.txt` (flag required).

## Root `<svg>` attributes (page 1)
data-mushaf="hafs-kfqc", data-qiraah="asim", data-riwayah="hafs", data-edition="kfgqpc-1441", data-riwayah-name-ar/en, data-ayah-numbering="kufi", data-ayah-total="6236", data-decomposition="word", data-page="1". `viewBox="0 0 345 550"` on page 1.
Every JSON carries `schema` and `schema_version`; columnar ones carry `fields`.

## Element inventory
- `g.word`: data-word-key, data-rasm-uthmani.
- `g.ayah-fragment`: data-ayah-key, data-ayah-mark, data-fragment, data-ayah-fragments; sometimes data-juz-start, data-hizb-start, data-rubu-al-hizb-start.
- `g.line`: data-line (top to bottom). `g.ayah-mark#mk-S-A` (id `mk-1-1`) with data-ayah-key and `g.ayah-mark-ornament`. `g.surah-name`. `g.ayah_markers` wraps the medallions.
- Path `data-kind` values seen on page 1: `body`, `mark`, `ayah_mark_ornament`, `ayah_number`, `header_ink`.
- Mark paths: `data-mark` (e.g. kasrah, dot, hamzat_al_wasl), `data-mark-family` (e.g. diacritic, dots).
- Page 1 counts: 29 words, 10 ayah fragments for 7 ayat, 8 lines, 179 marks, 67 body paths.

## Sidecar `index/by-page/NNN.json`
Top: schema `quran-svg-elements/page-words`, page, count, edition, view_box, box_space, words[]. Word example (1:1:2): ayah_key "1:1", box [185.33, 219.36, 200.18, 239.21], line 2, rasm_uthmani, rasm, rasm_imlai, qpc, search.
`words.json` fields: word_key, page, line, rasm_uthmani, search. `pages.json` per page: ayahs, banners, divisions, first_ayah, last_ayah, lines, marks, page, surahs, view_box, words.

## Geometry
Boxes are in the page viewBox with transforms applied. The SVG body sits under a negative-y matrix; use `getBBox()` in a browser. Crop a word: set `viewBox` to `x0 y0 (x1-x0) (y1-y0)`; to isolate, set `svg.style.visibility="hidden"` and the one `g.word` to `visible`.

## Text forms
rasm_uthmani: display it. search: match on it (derived from modern spelling; nothing is folded, so fold alef/hamza/yeh/teh marbuta on your side). Never split values on whitespace or assert forms are equal. qpc and rasm_uthmani differ from quran-text in codepoint order and sukun code point, so string joins fail.

## Sizes
Page 1 about 219.6 KiB raw; a fifteen-line page about 760 KiB raw (about 120 KiB brotli); whole set about 449 MiB raw.

## Known limits
No letter split. Some marks are exceptions (FORMAT.md section 10 lists them). Data may change between versions: pin one.
