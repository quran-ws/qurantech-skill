# Conversion detail (qiraat-ayah-map)

Sources: repo README, CONTRIBUTING.md, docs/consuming-the-mappings.md; quran.ws reference, method, source-files, map-ayah-references pages.

## Files (generated into dist/, not in git)
- `mappings/by-counting-system/kufi-to-<system>.json`, `<system>-to-kufi.json` (five systems, ten files)
- `mappings/by-rawi/hafs-to-<rawi>.json`, `<rawi>-to-hafs.json` (same tables by transmitter)
- `surah-counts/<system>.json`: `_counting_system`, `_total_ayahs`, `surahs`
- `rawis/<rawi>.json`: keys `_rawi`, `_qiraa`, `_counting_system_associated_with_qari`, `_counting_system_printed`, `_mapping_file_associated_with_qari`, `_mapping_file_printed`; deprecated `_counting_system`, `_mapping_file` (listed under `_deprecated`)
- Top-level keys of a mapping file: `_version`, `_description`, `_source`, `_target`, `surahs`.
- Committed and fetchable: `data/*.json`, `dist/site-data.json`, `dist/mushaf/surah-NNN.json`.

## Real entries (kufi-to-madani-last)
```json
"1":  { "target_ayah": 1, "status": "merged", "merges_with_next": true }
"2":  { "target_ayah": 1, "status": "mapped" }
"7":  { "target_ayah": 6, "status": "split", "splits_into": [6, 7] }
"11:82": { "target_ayah": 81, "status": "split", "splits_into": [81, 82], "merges_with_next": true }
```
Reverse: `{ "hafs_ayah": 1, "hafs_ayahs": [1, 2], "status": "covers_multiple" }` and `{ "hafs_ayah": 7, "status": "mapped" }`.
Kufan 7:206 is `target_ayah: 205` in basri, 206 in madani-last.

## Handling in the caller
- Forward result: `status === "split" ? splits_into : [target_ayah]`.
- If merging matters, test `merges_with_next` (398 forward entries carry it; 16 of them are splits, per the repo doc).
- Reverse result: `covers_multiple ? hafs_ayahs : [hafs_ayah]`.
- Render a multi-number result as a range; joining tafsir over an array means showing every entry.
- Reverse is lossy at splits and does not say so; reverse then forward is not identity.
- Forward and reverse use different field names (`target_ayah` vs `hafs_ayah`) and status unions.

## Two count fields
`data/printed-editions.json` fields: `rawi`, `qiraa`, `counting_system_printed`, `distance_to_printed_system`, `distance_to_system_associated_with_qari`, `differs_from_association`, `ayah_count`, `source_package`, `release_year`. A printed value belongs to one release; a new release is a new measurement. quran-text uses the same words under `counting.system_associated_with_qari`, `counting.system_printed`, `differs_from_association`.

## Boundary source layer
`data/book-boundary-primitives.json`: surah, Kufan ayah, then `end` (object) or `internal` (array); each has `word` and `counted_by`. Only disputes are recorded. `end` counted by fewer systems means those not listed merge that ayah into the next; `internal` counted by a system means it splits that ayah. Evidence statuses: `uncited`, `secondary_only`, `primary_cited`, `primary_cited_and_reviewed`, `disputed`, `unresolved`.

## Unverified or open
- The docs example calls `map({ from, to, ref })` from the package; the package is unpublished, so treat that call as unavailable.
- Which printed/attributed field to prefer per use case is my inference.
- Doc page says the count files are gitignored "at the commit read"; re-check the tree before relying on it.
- Ayah numbers for the Warsh worked example (1:1 to Hafs 1 and 2) come from the site's documented `toKufan(reverse, 1, 1)`; other entries were not re-read from generated files.
