### FILE plan.md
# Plan: adding Warsh (riwayat Warsh an Nafiʿ) to the Flutter Quran app

Current state: Hafs only. SQLite has `ayahs(surah, ayah_number, text, page)` and `bookmarks(surah, ayah_number, created_at)`.

Guiding fact: **the same `surah:ayah` can be a different piece of text in Warsh.** Hafs uses the Kufan count (`kufi`, 6,236 ayahs). Warsh uses the Last Madinan count (`madani-last`, 6,214 in the current data). Some Hafs ayahs are merged, split or shifted in Warsh. Almost everything below follows from that. A Warsh table that only swaps the `text` column will look right in testing and be wrong for many users.

Sources used for this plan: the Quran.ws `qurantech`, `qiraat-ayah-map` and related reference files. Items I could not verify are marked **(unverified)** and turned into checks in the phases at the end.

---

## 1. Data model changes

### 1.1 Principles
- Every reference carries **mushaf key + counting system**, never bare `surah:ayah`. Hafs = `hafs` / `kufi`. Warsh = `warsh` / `madani-last`.
- Do not store fixed totals (6,236 ayahs, 604 pages, per-surah ayah counts). Derive them from the loaded mushaf.
- Store Quranic text exactly as received. Never normalize, trim, or re-encode it. Keep a separate `text_search` column for search only.
- Use system ids exactly as they appear in `qiraat-ayah-map` (`kufi`, `madani-last`, …). Do not identify a system by its total.

### 1.2 New schema (DB version N → N+1)

```sql
CREATE TABLE mushafs (
  key             TEXT PRIMARY KEY,      -- 'hafs', 'warsh'
  riwayah         TEXT NOT NULL,
  counting_system TEXT NOT NULL,         -- 'kufi', 'madani-last'
  font_family     TEXT NOT NULL,         -- exact family from the source's font block
  font_file       TEXT NOT NULL,
  source_version  TEXT NOT NULL,         -- pinned data version
  source_sha256   TEXT NOT NULL          -- digest of the imported source file
);

CREATE TABLE ayahs (
  mushaf          TEXT NOT NULL REFERENCES mushafs(key),
  surah           INTEGER NOT NULL,
  ayah_number     INTEGER NOT NULL,      -- in that mushaf's counting system
  text            TEXT NOT NULL,         -- byte-exact from source
  text_search     TEXT,                  -- stripped form, search only
  page            INTEGER,               -- page in THIS mushaf's layout
  kufi_first      INTEGER,               -- nullable Hafs anchor range, see 1.4
  kufi_last       INTEGER,
  PRIMARY KEY (mushaf, surah, ayah_number)
);
CREATE INDEX ayahs_page ON ayahs(mushaf, page);

CREATE TABLE bookmarks (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  mushaf          TEXT NOT NULL,
  counting_system TEXT NOT NULL,
  surah           INTEGER NOT NULL,
  ayah_number     INTEGER NOT NULL,
  created_at      INTEGER NOT NULL,
  UNIQUE (mushaf, surah, ayah_number)
);
```

If you also want word-level features (word highlight, word audio), add a `words` table keyed on the **shared word number** from `quran-text`. That number is the same across riwayat. File-local positions are not.

### 1.3 Migration of existing data (Hafs)
Do this inside one `onUpgrade` transaction. Never drop the old tables until the copy is verified.
1. Rename `ayahs` → `ayahs_old`, `bookmarks` → `bookmarks_old`.
2. Create the new tables. Insert `mushafs('hafs', …)`.
3. Copy `ayahs_old` into `ayahs` with `mushaf='hafs'`, byte for byte.
4. Copy bookmarks with `mushaf='hafs'`, `counting_system='kufi'`. Every existing bookmark was made against Hafs, so this backfill is lossless.
5. Check `COUNT(*)` on both tables and compare a checksum of `text` against `ayahs_old`. Abort the transaction on any mismatch.
6. Drop `*_old` in a later app version, not the same one.

Also migrate anything else that stores `surah:ayah` (settings like "last read", reading progress, hifz ranges, notification schedules, shared prefs, widgets). It gets the same `mushaf` + `counting_system` treatment. Grep the codebase for `ayah_number`, `'$surah:$ayah'` and similar.

### 1.4 Cross-riwayah mapping
- Add `@quran.ws/qiraat-ayah-map` data as a bundled asset (pin the version). Read `kufi-to-madani-last.json` and `madani-last-to-kufi.json`.
- Kufan is the hub. Never convert Warsh → another non-Kufan system directly.
- Forward (Hafs → Warsh): `{target_ayah, status}` with status `mapped | merged | split`.
  - `split` carries `splits_into: [a, b]`. Show a range.
  - Test `merges_with_next` as its own field. Do not infer merging from `status === 'merged'`.
- Reverse (Warsh → Hafs): `mapped | covers_multiple`. For `covers_multiple` use the full `hafs_ayahs` array.
- Every helper returns a **list**. Callers render or join over the whole list. Add a `AyahRef` / `AyahRange` type so single-int returns are impossible.
- Reverse is lossy at splits. Example: Hafs 1:7 splits into Warsh 1:6 and 1:7, and both map back to Hafs 7. So never "normalize" by round trip.
- Precompute the two directions into `kufi_first` / `kufi_last` on Warsh rows at import time. Use them for joins to Hafs-indexed content (tafsir, translations). Keep the mapping files as the source of truth and regenerate on version bump.
- `quran-text` also ships `data/ayah-map.json` (Hafs → each of its 7 editions, text-aligned). If you ship quran-text's Warsh edition, cross-check your generated anchors against it. Two independent sources agreeing is a strong test.

### 1.5 Bookmarks across a riwayah switch
Recommended: **keep the original key and convert only for display.**
- A Hafs bookmark stays `(hafs, kufi, 2, 255)`. When the user is in Warsh mode, resolve it forward and show it as a range (Hafs 2:255 is Warsh 253–254 per the quran-text example, so verify in the data).
- A Warsh bookmark on a split half shows in Hafs mode as the Hafs ayah(s) it overlaps.
- Do not rewrite stored keys when the user switches. Rewriting via reverse mapping loses information at splits.
- The bookmarks list UI must handle results that are ranges and show which mushaf each came from.
- The "jump to bookmark" action opens the ayah in the **active** mushaf if a mapping exists, otherwise offers to switch.

### 1.6 Active-riwayah setting
- New setting `active_mushaf`, defaulting to `hafs`. Show the active riwayah visibly in the UI.
- All queries take the mushaf as a parameter. There is no global implicit Hafs.

---

## 2. Where to get the Warsh text

**Primary: Quran.ws `quran-text`.**
- Source-verified text for 7 printed riwayat including Warsh. Built from King Fahd Quran Complex (KFGQPC) packages with recorded SHA-256 digests.
- Same word number across riwayat. Ships page/line layout, juz, sajdat, waqf marks and the font each riwayah needs.
- It has JSON and SQLite data plus a Dart library in the main repo (`lib/`). It is Beta, so pin the version and the source hash.
- Licence: CC BY 4.0 plus KFGQPC terms for the text. Attribution is waived inside a product, but read `NOTICE.md` before shipping.
- Import at build time (a script), not at app runtime. Write the digest into `mushafs.source_sha256`.

**Do not:**
- Convert the Hafs text into Warsh by string edits. Warsh differs from Hafs in 277 words in `quran-text`, and also in orthography, marks and ayah boundaries. The result is Quranic text that looks plausible and is wrong.
- Take Tanzil for Warsh. It is Hafs only.
- Hand-type or copy-paste text from a website.

**Alternatives if `quran-text` doesn't fit (all need a licence and accuracy check first):**
- KFGQPC's own downloads (the official authority; `kfgqpc-resources` mirrors the files with checksums). Formats vary per riwayah, so verify what is published.
- QUL (Tarteel) has a `qpc-warsh` script. Per-resource licence.
- `fawazahmed0/quran-api` has Warsh text split by ayah. It is community-maintained, so verify accuracy against KFGQPC before trusting it.

**Text integrity gate (CI):** compare the imported `ayahs.text` for `warsh` byte for byte against the pinned source file. Fail the build on any difference. Compare in NFC only in a throwaway copy. Never store the normalized form.

---

## 3. Fonts

- Warsh needs its own font: **`KFGQPC Warsh Uthmanic Script`**, file `UthmanicWarsh-v-3.0.ttf`. Take the exact family and file from the mushaf's `font` block in `quran-text`.
- The Hafs font will not render Warsh correctly. Warsh text uses **Arabic Extended-B codepoints** that general and Hafs fonts lack. The symptom is a blank or boxed glyph, not an error, so it is easy to miss.
- Flutter: declare the font in `pubspec.yaml` and store `font_family` on the `mushafs` row. Choosing a mushaf then chooses its font. Do not hardcode `fontFamily` in widgets.
- Rules:
  1. Load the font the active mushaf names.
  2. **No fallback** to another Quranic font or the system font. Show the reference plus an error if loading fails.
  3. Build-time test: every codepoint in the Warsh text exists in the font's `cmap`.
- Waqf marks are combining characters. Inspect Unicode scalars, not grapheme clusters, when you truncate, measure or highlight.
- Licence: the fonts are under KFGQPC's terms. That allows use in software. It says nothing on modification, so **do not convert to woff2 or edit the file** without the Complex's permission. Ship the TTF unmodified.
- Text shaping on real devices: test on physical Android and iOS at the OS versions you support **(unverified which versions break which passages)**. If shaping is a problem, the alternative is glyph-outline pages (`quran-svg` has a Warsh page set) which need no font.
- Page mode: if the app shows mushaf pages, Warsh has its own layout. Use `quran-svg` (Warsh edition, with ayah polygons) or `quran-engine`, or the Warsh `page`/`line` layers from `quran-text`. Never reuse Hafs page numbers.
- Ornaments (ayah-end markers, surah banners): check licences in `quran-assets`. Its scan-derived ornaments are provisional and non-commercial.

---

## 4. Audio recitation

The app's audio layer needs Warsh recordings, and each one must be joined to Warsh ayahs correctly.

**Sources (check licence and terms of each before shipping):**
- **EveryAyah**: per-ayah MP3 (`everyayah.com/data/{reciter_folder}/001001.mp3`), includes Warsh reciters. Its XML metadata is at `everyayah.com/data/XML/`.
- **MP3Quran** (`mp3quran.net/ar/api`): whole-surah files, multiple qira'at, with `/ayat_timing`.
- **QuranPedia** `/v1/reciters`: reciters across riwayat with ayah-timing ZIPs.
- **QUL**: segmented audio with word timestamps. Check for Warsh sets.
- There's no Quran.ws audio block. The blocks give you keys, not recordings.

**Model:** `Reciter` (person) → `Recitation` (reciter × riwayah × style × bitrate) → `AudioSegment`. Put `riwayah`, `counting_system` and the source's `mushaf` on the **recitation**, not the reciter. One reciter can have both Hafs and Warsh sets.

**Rules:**
- Only offer Warsh reciters when the active mushaf is Warsh, and Hafs reciters when it is Hafs. A Hafs recording played over Warsh text is a data bug.
- **Verify which numbering each audio source uses for Warsh files (unverified).** A per-ayah file `001001.mp3` may follow Warsh numbering, Hafs numbering, or something in between. Do this per source by listening: sample the splits and merges (see §5.3) and compare with the timing file. Record the answer in `recitations.counting_system`.
- If a recording is indexed in a different system from the active text, map with `qiraat-ayah-map` and play the whole range. A split or merged ayah means one file may be two ayahs, or half of one.
- Word highlighting: key timings on the shared word number. Timing data measured against Hafs text is not valid for Warsh words that differ.
- Existing rules still apply: show the reciter's name, never auto-play, start at ayah boundaries, work in the background.
- Do not machine-split whole-surah Warsh audio into ayahs and ship it without human review.

---

## 5. What could silently break if we do it naively

None of these crashes. They all show wrong content.

### 5.1 Ayah numbering
1. **`(surah, ayah_number)` used as a global key.** Warsh 2:253 does not mean Hafs 2:253. Any join between the new Warsh table and Hafs-indexed content (translations, tafsir, tajweed spans, audio timings, hifz data) returns the wrong ayah with no error.
2. **Split and merged ayahs.** Some ayahs exist in one system as one and in the other as two. A single-integer mapping shows only one of them. The tafsir for the missing half is never shown.
3. **Fatiha and the basmalah.** Hafs numbers the basmalah as 1:1. Warsh (per the mapping, `1:1` covers Hafs 1 and 2) does not. Code that assumes "surah 1 has 7 ayahs, ayah 1 is the basmalah", or that skips the basmalah when it is ayah 1, is wrong for Warsh. Treat "has a basmalah" and "basmalah is numbered" as two separate fields.
4. **Hardcoded counts.** 6236, 114-surah ayah arrays, "604 pages", progress percentages, "juz 30 has N ayahs", khatm counters. Warsh total is 6,214 in the current data, and per-surah counts cannot be derived from totals. Read `surah-counts/<system>.json`.
5. **Next / previous ayah, and range end.** `ayah + 1` and `ayah <= surah_ayah_count` (from a Hafs table) walk off the end or skip an ayah.
6. **Round-trip normalization.** Converting a Warsh bookmark to Hafs and back changes it at splits.
7. **The mapping disagrees with the printed edition.** `qiraat-ayah-map` records both the count *attributed* to Warsh and the count a measured KFGQPC printed edition carries. Check `printed-editions.json` for Warsh. If it differs from `madani-last`, decide which one the text you import follows, and test against that text.

### 5.2 Page, juz, layout
8. **`page` column reuse.** Page N holds different ayahs in Warsh. Any feature that navigates by page (jump to page, reading progress, page-based audio, "pages read today") is wrong.
9. **Juz, hizb, rub', sajda and ruku tables keyed to Hafs ayahs.** Starting points can shift with the numbering. Sajdat and their ayah numbers differ in the data. Recompute per mushaf, or map via the anchor range.
10. **Surah metadata** (`ayah_count`, `start_page`) shared across mushafs.

### 5.3 Text and rendering
11. **Wrong font, no error.** See §3. A blank line, or a Hafs-shaped glyph substitute, means a wrong font, not missing data.
12. **Font fallback.** Flutter silently falls back to a system font for missing codepoints. That is worse than a visible failure for Quranic text.
13. **Text normalization** in code that was written for Hafs: NFC/NFD, stripping "unusual" marks, `trim()`, regexes over Arabic ranges that don't include Arabic Extended-B. This can delete Warsh marks. Also check any `substring` and `.length` calls (code points ≠ letters).
14. **Search.** Search that strips diacritics using a Hafs-tuned mark list may not strip Warsh marks, so queries fail to match. Build `text_search` per riwayah, and make search results use the active mushaf.
15. **Copy and share.** Copy/share code that assumes Hafs text, or embeds the Hafs ayah number in the text or a deep link.
16. **Tajweed colouring.** Rules keyed to Hafs text offsets (regex or spans) do not apply to Warsh. Warsh has its own rules (for example, different madd lengths and other riwayah-specific rules). Hide tajweed for Warsh until it is validated for it. Check `quran-tajweed` coverage first **(unverified)**.

### 5.4 Content joins
17. **Translations and tafsir.** These are almost always Hafs-indexed. Join through the anchor range and display all Hafs ayahs it covers. Label the content as Hafs-based when the reader is in Warsh.
18. **Tafsir ranges.** A tafsir entry covers a range. A Warsh ayah may straddle a range boundary.
19. **Word-by-word data.** Do not key it on position. Use the shared word number. Note some words differ between riwayat.

### 5.5 Audio
20. **Wrong recitation offered or played.** See §4.
21. **Timings measured on another mushaf.** Highlighting drifts, or lands on the wrong word.

### 5.6 User data
22. **Old bookmarks** without a `mushaf` column silently become Warsh bookmarks (if the default flips to Warsh), or vanish (if queries filter by mushaf).
23. **Sync / backup / export.** Old exports and cloud sync payloads have no mushaf. Import must treat a missing field as `hafs`/`kufi`, and new exports must always write it. Old app versions reading a new payload will misread Warsh bookmarks as Hafs.
24. **Reading progress and hifz ranges** (`ayah_from`..`ayah_to`) become invalid when the user switches mushaf. Store them with the mushaf and convert to ranges for display only.
25. **Notifications and widgets** ("ayah of the day") that pick a random Hafs number and look it up in Warsh.

### 5.7 Licensing and process
26. **Font conversion** without permission (§3).
27. **Unpinned data.** A silent update to the text or mapping package changes a stored offset or bookmark meaning. Pin versions and store the source digest.
28. **Adab.** No AI-generated or hand-typed Quranic text. Do not log Quranic text (log `mushaf:surah:ayah`). Label translations as translations.

---

## 6. Phases

**Phase 0 – Groundwork (no user-visible change)**
- Add the `mushafs` table and the new schemas. Write and test the Hafs-only migration (§1.3) on real copies of existing databases (including a large bookmark set, and a fresh install).
- Introduce `AyahRef {mushaf, counting, surah, ayah}` and `AyahRange`. Refactor every call site off bare `(surah, ayah)`. Remove hardcoded counts.
- Ship this on its own. If it regresses, Hafs users notice before Warsh exists.

**Phase 1 – Warsh data**
- Build-time importer from pinned `quran-text` Warsh data. Digest recorded. CI byte-comparison test.
- Bundle `qiraat-ayah-map` files. Build the anchor ranges. Cross-check against `quran-text` `ayah-map.json`.
- Decision to make: bundle Warsh in the APK/IPA or download on demand. Recommend on-demand download for size, with Hafs always bundled **(size is unverified; measure it)**.

**Phase 2 – Rendering**
- Font declaration per mushaf, cmap coverage test, no fallback.
- Warsh page layout (from `quran-text` layers or `quran-svg` Warsh).
- Riwayah selector in settings and visible in the reader UI.
- Device tests on real Android and iOS.

**Phase 3 – Bookmarks, progress, content joins**
- Bookmarks per §1.5. Translations/tafsir through anchor ranges. Sync/export format version bump.

**Phase 4 – Audio**
- Pick sources, verify numbering by listening at the split/merge points, add the `Recitation` model, filter reciters by active riwayah.

**Phase 5 – Ship**
- Feature-flag Warsh. Label which features are Hafs-only for now (tajweed, some translations) rather than showing them wrongly.
- Ask a Warsh reader or scholar to review the text display, the font, and the audio pairing before release. Automated tests cannot judge that.

---

## 7. Test list

- **Migration:** old DB → new DB has identical Hafs text (checksum), identical bookmarks with `hafs`/`kufi`, on both upgrade and fresh install.
- **Text integrity:** Warsh `text` equals the pinned source byte for byte.
- **Font:** every Warsh codepoint is in the font's `cmap`. Golden screenshot of a few Warsh ayahs on real devices.
- **Mapping boundary cases:** a `mapped`, a `split` (Hafs 1:7 → Warsh 1:6–7), a `merged`, a `covers_multiple` (Warsh 1:1), and an entry with `merges_with_next` that is also a `split` (for example `11:82`). Assert list results, not single ints.
- **Totals:** derived ayah count for Warsh equals the count in `surah-counts/madani-last.json`. No test may assert 6,236 for Warsh.
- **Navigation:** next/previous across every surah boundary in Warsh.
- **Bookmarks:** create in Hafs, view in Warsh, switch back. The stored row never changes.
- **Audio:** for each Warsh recitation, play the ayahs at split/merge positions and check they start and end at an ayah boundary.
- **Search:** Warsh queries find Warsh text (and use `text_search`, not `text`).

## 8. Open questions to resolve before Phase 1
1. Which counting system does the KFGQPC Warsh edition you import measure onto (attributed `madani-last` versus `printed-editions.json`)? Confirm in the data.
2. Which numbering do the chosen Warsh audio sets use? (unverified)
3. Is `quran-tajweed` valid for Warsh? (unverified)
4. Do Warsh pages in `quran-text` and `quran-svg` agree (page count, first ayah per page)? Don't assume 604.
5. Which state-management / DB layer does the app use (`sqflite`, `drift`)? The migration code in §1.3 depends on it.
6. Which tafsir and translation sets are shipped, and are they Hafs-indexed? (Likely yes.)


### FINAL MESSAGE
I've written the plan to `/tmp/eval0-with_skill-a8o210tf/plan.md`. It comes from the Quran.ws reference docs, not from checking any real Warsh data, so the numbering, audio and pagination details are still unchecked.

The main risk is that Warsh counts ayahs differently from Hafs. Warsh follows the Last Madinan count (`madani-last`, 6,214 ayahs in the current data), and Hafs follows the Kufan count (6,236). Some ayahs are merged or split between them. Warsh 1:1, for example, covers Hafs 1 and 2. So a table that only swaps the `text` column will look right and still be wrong in many places.

- **Data model:**
  - Every reference carries a mushaf key and a counting system, never a bare `surah:ayah`.
  - The `ayahs` and `bookmarks` tables gain those columns, and the existing rows are backfilled as `hafs` / `kufi` in one transaction with a checksum check.
  - Mapping between Hafs and Warsh uses `qiraat-ayah-map` and always returns a list, because splits and merges produce ranges.
  - Bookmarks keep their original key and are converted only for display, because converting a Warsh bookmark to Hafs and back can land on a different ayah.
- **Text:** use the Warsh edition of Quran.ws `quran-text`, pinned, with a CI check that it matches the source byte for byte. Don't derive Warsh from Hafs text. Tanzil is Hafs only.
- **Fonts:**
  - Warsh needs its own font, `KFGQPC Warsh Uthmanic Script`.
  - It uses Arabic Extended-B codepoints, so the wrong font shows blanks rather than errors.
  - The plan says no font fallback, a check that the font covers every codepoint, and no converting the font without the Complex's permission.
- **Audio:**
  - Model reciter, recitation and ayah audio separately, and tag each recitation with its riwayah and counting system.
  - Only offer Warsh reciters when the reader is on Warsh.
  - Word-highlight timings are only valid against the text they were measured on.
- **Silent breakage:** the plan lists 28 cases. They include hardcoded 6,236 or 604 counts, the basmalah handling in al-Fatihah, page, juz and sajda tables keyed to Hafs, tafsir and translation joins, tajweed rules tied to Hafs text, old sync or export payloads with no mushaf field, and search that strips marks Warsh doesn't use.
- **Phases and tests:** it also has phased delivery (Phase 0 refactors and migrates with no visible change) and a test list built around the split and merged ayahs.

**Unverified in the plan:**
- Which numbering each Warsh audio source uses (EveryAyah, MP3Quran, QuranPedia). You'll need to check this by listening at the split and merge points.
- Whether tajweed colouring is valid for Warsh.
- Whether Warsh pagination matches 604 pages.
- Whether the Warsh edition you import follows `madani-last` or something slightly different.

I also don't know whether the app uses `sqflite` or `drift`, so the migration code is written generically.