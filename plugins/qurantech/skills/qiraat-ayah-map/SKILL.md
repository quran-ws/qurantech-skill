---
name: qiraat-ayah-map
description: Use when an app supports a riwayah other than Hafs, converts an ayah reference between counting systems (madhhab of ʿadd al-āy), handles split or merged ayahs, joins Warsh or other non-Kufan ayahs to Hafs-indexed tafsir, translation or recitation data, or stores bookmarks that must survive a riwayah switch. Covers Quran.ws qiraat-ayah-map.
---

# qiraat-ayah-map

Follow the `qurantech` skill's adab rules (never alter or truncate Quranic text). This block carries numbering only, no Quranic text; text comes from `quran-text`.

## The six counting systems (ids exactly as in data)
`kufi` (Kufan, hub, 6,236; Hafs), `madani-first` (6,214 in the current data; qiraat-ayah-map PR #7 proposes 6,217), `madani-last` (6,214; Warsh, Qalun), `makki` (6,219), `basri` (6,204), `dimashqi` (6,226). Never identify a system by its total: the First Madinan total is disputed pending PR #7 (6,214 vs 6,217), so the two Madinan totals must not be assumed to tie or differ.

## Get the data
`npm i @quran.ws/qiraat-ayah-map` (0.1.0 on the registry; the tarball ships `data/` and the generated `dist/mappings`, `dist/rawis`). The README still says "not published", so confirm with `npm view`. From the repo, `dist/mappings` is gitignored: run `npm run generate`, or use the committed `data/*.json`. Pin the package version.

## Convert a reference
Kufan is the hub; there is no `basri-to-makki`. Route through Kufan in two steps.
1. Find the system: `dist/rawis/<rawi>.json`, field `_counting_system_associated_with_qari` or `_counting_system_printed`. A null `_mapping_file_*` means Kufan: no conversion.
2. Forward `mappings/by-counting-system/kufi-to-<system>.json`: `surahs[s].ayahs[a]` gives `{target_ayah, status}`, status `mapped | merged | split`.
   - `split` carries `splits_into: [n, m]`: show a range, never only `target_ayah`.
   - `merges_with_next: true` is independent of status; test the field, not `status === "merged"`.
3. Reverse `<system>-to-kufi.json`: `{hafs_ayah, status}`, status `mapped | covers_multiple`; `covers_multiple` adds `hafs_ayahs`, use the full array.
4. Every helper returns an array; the caller renders or joins over all of it. Keys are strings.

## Two count fields
`counting_system_associated_with_qari` (`data/qiraat.json`): the madhhab a qāriʾ is attributed. `counting_system_printed` (`data/printed-editions.json`): what a measured printed muṣḥaf carries. Abū ʿAmr is attributed `basri`, yet both King Fahd muṣḥafs measure `madani-first`. Never derive one from the other; `null` printed means unmeasured, not agreeing. To number what a specific muṣḥaf shows, prefer printed when non-null; otherwise use the attributed system and flag it unverified (my reading; the docs say only that the two never share a field). Unsettled upstream.

## Store and join
Persist `{surah, ayah, counting}`, never bare `surah:ayah`. Docs recommend storing Kufan and translating only on display. Do not normalise by round trip: reverse of a split loses which half (1:7 and its second half both return Kufan 7).

## Example: Warsh ayah to Hafs-indexed tafsir
```js
const rev = await load("dist/mappings/by-counting-system/madani-last-to-kufi.json"); // Warsh
const e = rev.surahs["1"].ayahs["1"];
const hafs = e.status === "covers_multiple" ? e.hafs_ayahs : [e.hafs_ayah]; // [1, 2]
const tafsir = hafs.map(a => tafsirByHafs["1:" + a]); // show both, never only the first
```

## quran-text or this block
`quran-text` `data/ayah-map.json` gives Hafs reference to each of its seven bundled editions (relation `same|merged|split|shifted|unnumbered`, `ayah_last`), text-aligned. Use it when you already ship those editions. Use this block for any of the six systems, all ten qiraat, or the boundary evidence.

## Licence and maturity
CC BY 4.0 for `data/`, MIT for `scripts/`, `tests/`. Labelled Stable, version 0.1.0; 246 disputed positions. Abū ʿAmr's assignment is contested.

## Gotchas
No schema or types. Files mix `_` metadata with data. `word` in primitives is not a join key. Per-surah counts cannot be derived from totals: read `surah-counts/<system>.json`. `_counting_system` and `_mapping_file` are deprecated aliases.

Detail: `references/conversion.md`.
