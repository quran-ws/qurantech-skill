# Qira'at (Recitation Styles) Support

## Table of Contents
- [Overview](#overview)
- [Block-first: what to use](#block-first-what-to-use)
- [Counting systems](#counting-systems)
- [Converting a reference](#converting-a-reference)
- [Data model](#data-model)
- [Background: qira'at and ruwat](#background-qiraat-and-ruwat)
- [Fallback: your own anchor design](#fallback-your-own-anchor-design)
- [Per-riwayah fonts](#per-riwayah-fonts)
- [Best Practices](#best-practices)

## Overview

The same `surah:ayah` can point to different text depending on the counting system. Two Quran.ws blocks cover this; see [blocks.md](../blocks.md) for the catalog.

## Block-first: what to use

| Need | Block | Notes |
|---|---|---|
| Text of a riwayah (7 printed riwayat), word-level alignment | **quran-text** | One word numbering shared by all seven riwayat, so a word matches across them. `data/differences.json` lists the 277 differing words. |
| Ayah reference in another riwayah, when you ship the quran-text editions | **quran-text** `data/ayah-map.json` | Kufi (Hafs) reference to each edition: `relation` is `same`, `merged`, `split`, `shifted` or `unnumbered`, plus `ayah_last`. Example from the skill: Hafs 2:255 is Warsh 253 to 254, `split`. |
| Any of the six counting systems in the dataset, all ten qira'at, boundary evidence | **qiraat-ayah-map** | Skill `qiraat-ayah-map` has the recipe; the repo's `docs/consuming-the-mappings.md` lists what code gets wrong. |

Use `data/counting.json` in quran-text to see which system an edition follows.

## Counting systems

qiraat-ayah-map ids, exactly as in the data: `kufi` (the hub; Hafs), `madani-first`, `madani-last` (Warsh, Qalun), `makki`, `basri`, `dimashqi`. Six is the dataset's scope (al-Bayan works with six). Nafa'is al-Bayan lists a seventh, a Himsi count of 6,232, which the dataset excludes and records in a scope note. Never identify a system by its total. Totals in the dataset: `kufi` 6,236, `makki` 6,219, `dimashqi` 6,226, `basri` 6,204, `madani-last` 6,214. `madani-first` is **disputed, pending PR #7**: today's data generates 6,214; PR #7 (open) corrects it to al-Dani's 6,217 (al-Bayan p. 79, via al-Shatibi), on the grounds that 6,214 is the Basran route through Warsh and that Last Madinan is independently 6,214. The two Madinan counts differ by 57 places in al-Dani's enumeration. Neither figure is final here; read `data/counting-systems.json` and the PR before quoting one.

Two count fields, never joined together:
- `counting_system_associated_with_qari` (`data/qiraat.json`): the count *attributed* to a qari.
- `counting_system_printed` (`data/printed-editions.json`): what a measured printed mushaf carries. `null` means unmeasured, not agreeing.

They differ. Abu Amr is attributed `basri`, yet both King Fahd mushafs of his ruwat measure onto `madani-first`: Duri (v2.0, 2022 package) at distance 0 with 6,217 ayahs, Susi (v3.0) at distance 1 with 6,218 ayahs, so Susi is not an exact match. The Duri figure comes from the 2022 package only, and printings of it disagree about 67:9, so a later release can differ. Bazzi (6,220) is distance 1 from `makki` (6,219). `printed-editions.json` covers only seven KFGQPC packages: Hafs, Shuba, Warsh, Qalun, Duri, Susi, Bazzi. quran-text reports the same pair (`system_printed`, `system_associated_with_qari`, `differs_from_association`) and names the release each count was measured from (`counting.measured_from`). A printed count describes one release, not the mushaf in general.

Read `data/counting-systems.json` and `surah-counts/<system>.json` from the released package, and never copy a total from a table.

To number what a specific printed mushaf shows, prefer the printed count when non-null; otherwise use the attributed one and flag it unverified.

## Converting a reference

Kufi is the hub: there is no `basri-to-makki`; go through `kufi` in two steps (full recipe in skill `qiraat-ayah-map`).
- Forward `kufi-to-<system>.json`: `{target_ayah, status}` with status `mapped | merged | split`. A `split` carries `splits_into`: show a range. `merges_with_next` is independent of `status`: test the field.
- Reverse `<system>-to-kufi.json`: `mapped | covers_multiple`; `covers_multiple` adds `hafs_ayahs`: use the full array.
- Helpers return arrays; render or join over all of it.

The dataset stores only *disputed* boundaries: the word each contested boundary falls on and which madhhabs count it as an ayah end. Walking a surah's boundary points in text order reproduces every madhhab's numbering, with citations. Consider modelling your counting data the same way rather than storing six parallel numberings.

## Data model

- Persist `{surah, ayah, counting}` (or a mushaf key), never bare `surah:ayah`.
- Store content once against the Kufi ayah and translate to the reader's system on display, as the qiraat-ayah-map docs recommend.
- The reverse direction is lossy at splits: Kufi 1:7 splits in `madani-last` into 1:6 and 1:7, and both map back to Kufi 7. Never normalize bookmarks by round trip; keep the original key.
- Word-level features: key on quran-text's shared word number, not on ayah position.

## Background: qira'at and ruwat

There are 10 canonical qira'at, each through 2 ruwat (20 chains). Hafs an Asim is the most widely used. The table shows the count *attributed* to each qari. Names and attributions are as in `data/qiraat.json`; verify against it before relying on them.

| Qari | Rawi 1 | Rawi 2 | Attributed count (per the dataset) |
|---|---|---|---|
| Nafi' al-Madani | Qalun | Warsh | `madani-last` |
| Ibn Kathir al-Makki | Al-Buzzi | Qunbul | `makki` |
| Abu Amr al-Basri | Al-Duri | Al-Susi | `basri` (printed: `madani-first`) |
| Ibn Amir al-Shami | Hisham | Ibn Dhakwan | `dimashqi` |
| Asim al-Kufi | Shu'bah | Hafs | `kufi` |
| Hamzah al-Kufi | Khalaf | Khallad | `kufi` |
| Al-Kisa'i | Abu al-Harith | Al-Duri | `kufi` |
| Abu Ja'far al-Madani | Ibn Wardan | Ibn Jammaz | `madani-first` (PR #7: al-Dani treats him as his own authority, 6,210) |
| Ya'qub al-Basri | Ruways | Rawh | `basri` |
| Khalaf al-Ashir | Ishaq | Idris | `kufi` |

Two different reciters are called Khalaf: Hamza's rawi (slug `khalaf` under `hamza`) and the tenth qari, Khalaf al-Ashir (`khalaf` qari entry, name_en "Khalaf al-Ashir"). Do not join them on the bare name. Abu Amr's assignment is contested upstream. Boundary placement differs between systems; that is a numbering difference, not a text difference.

## Fallback: your own anchor design

Use this only for what the blocks do not cover (for example a database that already keys tafsir and translations to one system). The anchor is the Kufi (Hafs) ayah:
- One database; every ayah row carries `mushaf_id`; each non-Kufi ayah row carries an anchor to a Kufi ayah (the first of the range when it merges two).
- All shared content is keyed to the anchor; fetch content by resolving to the anchor first.
- To show another mushaf's ayah, take the greatest anchor at or below the source anchor, so a merged ayah still resolves:

```sql
SELECT * FROM ayahs
WHERE mushaf_id = :target_mushaf AND surah_id = :surah AND equals_ayah_id <= :hafs_ayah_id
ORDER BY equals_ayah_id DESC LIMIT 1
```

A single-anchor column cannot represent a split faithfully (one Kufi ayah becomes two target ayahs); prefer the block's range output. A separate database per riwayah, joined by an API layer, is an untested alternative for when riwayat are downloaded or deleted independently; the anchor pattern above is a design suggestion, not a measured production result.

## Per-riwayah fonts

quran-text ships the font each riwayah needs; a Hafs font misrenders other riwayat, and Warsh, Qalun and Susi use Arabic Extended-B codepoints that many fonts lack. Coverage is the seven printed riwayat only. Store the font reference on the mushaf record so choosing a mushaf chooses its font. Originals: King Fahd Complex; `kfgqpc-resources` mirrors them with checksums.

## Best Practices

- Never hardcode ayah counts; derive them from the data for the active mushaf or system.
- Show the active riwayah in the UI. Default to Hafs unless the user chose otherwise, and keep it configurable.
- Use mapping data for every cross-riwayah feature; never assume the same number works across systems.
- Test boundary cases from the mapping data: `split` and `merged` entries, `covers_multiple`, and entries with `merges_with_next` (see [testing-qa.md](testing-qa.md)).
- Audio metadata must name the riwayah; a Hafs recording over Warsh text is a data bug.
- Pin the qiraat-ayah-map version and treat data as versioned input.
