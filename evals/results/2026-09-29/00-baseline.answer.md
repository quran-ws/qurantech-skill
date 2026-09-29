### FILE plan.md
# Plan: Add Warsh (riwayat Warsh 'an Nafi') alongside Hafs

Note: the working directory was empty, so this plan is based on the schema you described, not the code. Facts I could not verify offline are marked **VERIFY**. Do those checks before writing code.

## 0. The core problem

Warsh is not "Hafs with different text". The verse numbering differs. Hafs uses the Kufan count (6236 verses). Warsh mushafs (e.g. the King Fahd Complex Warsh mushaf) follow the Madani count, which has fewer verses (about 6214–6217 depending on the Madani sub-count, **VERIFY which one the chosen source uses**). Examples:

- Al-Fatiha: Hafs counts the basmalah as verse 1. Madani does not, so the verse boundaries inside 1:6–7 shift.
- Many surahs differ in how they count the disconnected letters (Ta-Ha, Ya-Sin, Ha-Mim, etc.). Some verses are also split or merged.

So `(surah, ayah_number)` **is not a riwaya-independent identifier**. Everything that stores or transmits that pair (bookmarks, audio URLs, translations, deep links, last-read) becomes ambiguous the moment a second riwaya exists. This is the main thing that breaks silently. The rest of this plan works around it.

## 1. Data model

### 1.1 Schema (DB version N → N+1)

```sql
-- ayahs: composite key including riwaya
CREATE TABLE ayahs_new (
  riwaya       TEXT    NOT NULL,          -- 'hafs' | 'warsh'
  surah        INTEGER NOT NULL,
  ayah_number  INTEGER NOT NULL,          -- number in THAT riwaya's count
  text         TEXT    NOT NULL,          -- rendered text (riwaya's orthography)
  text_search  TEXT    NOT NULL,          -- normalized for search (see §6)
  page         INTEGER NOT NULL,          -- page in THAT riwaya's mushaf
  PRIMARY KEY (riwaya, surah, ayah_number)
);
INSERT INTO ayahs_new SELECT 'hafs', surah, ayah_number, text, text, page FROM ayahs;
DROP TABLE ayahs; ALTER TABLE ayahs_new RENAME TO ayahs;
CREATE INDEX idx_ayahs_page ON ayahs(riwaya, page);

-- bookmarks: SQLite cannot alter a PK, so rebuild
CREATE TABLE bookmarks_new (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  riwaya       TEXT    NOT NULL,          -- riwaya the user was reading when saving
  surah        INTEGER NOT NULL,
  ayah_number  INTEGER NOT NULL,
  created_at   INTEGER NOT NULL,
  UNIQUE (riwaya, surah, ayah_number)
);
INSERT INTO bookmarks_new (riwaya, surah, ayah_number, created_at)
  SELECT 'hafs', surah, ayah_number, created_at FROM bookmarks;
DROP TABLE bookmarks; ALTER TABLE bookmarks_new RENAME TO bookmarks;
```

Run each step inside one transaction in `onUpgrade`. Keep the old DB file as a backup copy until the first successful launch after migration. Also write a migration test that starts from a real v(N) DB file.

### 1.2 Verse mapping table (Hafs ↔ Warsh)

```sql
CREATE TABLE verse_map (
  hafs_surah INTEGER, hafs_ayah INTEGER,
  warsh_surah INTEGER, warsh_ayah INTEGER,
  kind TEXT   -- 'exact' | 'split' | 'merged' | 'basmalah'
);
```

- Build it offline with a script, not by hand. Align both texts word by word after stripping diacritics and orthographic variants, then emit overlaps. Check the output by hand for every surah where the counts differ.
- Mapping is many-to-many. Warsh 1:6 may cover part of two Hafs verses. Resolve to "the verse containing the start of the range" and store this rule in one place.
- Ship `verse_map` as a static asset table. It is only used for cross-riwaya features (switching riwaya while keeping your place, showing bookmarks from the other riwaya).

### 1.3 Other structures to make riwaya-aware

Audit every place that keys on `(surah, ayah)`:

- Last-read position / reading progress
- Translations and tafsir tables. These are usually Hafs-numbered, so for Warsh either map through `verse_map` or hide them (see §7).
- Juz/hizb/rub' boundaries and sajdah verses. Store these per riwaya, since the boundaries are defined by mushaf and count.
- Notification, widget and deep-link payloads.

### 1.4 App state

- Riwaya is a persisted setting (`hafs` default), exposed via a provider/bloc at the top of the tree. Do not use a global constant.
- Every repository method that reads ayahs/bookmarks takes `riwaya` explicitly. Do not read it from ambient state inside the data layer. That is how the wrong riwaya gets queried after a switch.

## 2. Where to get the Warsh text

Candidates, in order of preference. **VERIFY the license and current availability of each.**

1. **King Fahd Glorious Quran Printing Complex (KFGQPC)** publishes Warsh Uthmani text and the matching Warsh font. It is authoritative and consistent with a printed Warsh mushaf (including its page layout). Check the license terms for app redistribution.
2. **Quran.com / Quran Foundation API (v4)**: check whether it exposes a Warsh script and Warsh verse numbering. If it does, it is useful for cross-checking.
3. **Tanzil** covers Hafs only as far as I know (**VERIFY**), so it can't be the primary source. It is still a good baseline for the mapping alignment.
4. Community datasets (GitHub Warsh JSON/SQL). Treat them as untrusted. They often have typos or mixed Hafs and Warsh orthography. Use them only as a cross-check.

Data acceptance checks (automated, run in CI on the import script):

- Verse counts per surah match the published count for the chosen Warsh mushaf.
- The text has no Hafs-only marks and no mixed orthography (see §3).
- A second, independent source agrees after normalization, or discrepancies are reviewed by a person who reads Warsh. Have a qualified reader review the final text. Quran text errors are not acceptable.
- Store the source, version and license in the repo (`assets/data/README`).

## 3. Fonts

- Warsh uses the Maghribi conventions. Fa has one dot below, qaf has one dot above, and the sukun, madd and small-mark forms differ. The Hafs font will render these wrongly or fall back to another font.
- Bundle a Warsh-capable font. KFGQPC provides one, so **VERIFY the license**. Declare it in `pubspec.yaml` as a separate family and choose it by riwaya.
- Any per-page glyph font approach (QCF-style fonts, one font per mushaf page) is Hafs-specific and cannot be reused. Warsh needs its own pagination and font, or you fall back to plain text layout.
- Test on real devices, both Android and iOS. Check every combining mark in the Warsh text. Missing glyphs show as boxes or silently drop marks, and that changes the reading.
- Do not apply `TextStyle` letter spacing or a font fallback stack that can substitute glyphs from another font.
- Check rendering with a script that renders all distinct code points in the Warsh text and diffs against the font's cmap.

## 4. Audio recitation

- Recitation must be Warsh. Hafs audio under Warsh text is a correctness bug, not a cosmetic one.
- Sources to evaluate (**VERIFY availability, reciter names and licenses**): EveryAyah and Quran.com host some Warsh reciters (e.g. Ibrahim Al-Dosari, Yassin Al-Jazairi), and there are others. Prefer sources that provide per-ayah files under Warsh numbering.
- Data model: an `audio_reciters` table with `riwaya`, `reciter_id`, `base_url`, `granularity` (`ayah` | `surah`). Each reciter is tied to a riwaya. The reciter picker only lists reciters for the active riwaya.
- Per-ayah file URLs must use the **Warsh** numbering. If a source has only full-surah files, you need timing data (ayah start/end offsets) and must produce it yourself for Warsh. Don't reuse Hafs timings.
- Cache keys must include riwaya and reciter (`warsh/<reciter>/<surah>_<ayah>.mp3`). Otherwise a cache hit returns the Hafs file for the same `(surah, ayah)`.
- Gapless playback, highlight-current-ayah and "repeat ayah" all depend on the numbering. Test them on the surahs where the counts differ.

## 5. Page layout

- The `page` column is per riwaya. The Warsh mushaf has its own pagination (**VERIFY the page count and line layout for your chosen edition**). Never assume 604 pages. Search the code for `604` and for page-clamp logic.
- If you render as a page-by-page mushaf, build the Warsh page index from the source's page data. Don't derive it from Hafs.
- If the source has no page data, drop the "page" view for Warsh and use a scrolling surah view. Do not invent page numbers.

## 6. Search

- Store a normalized `text_search` column. Normalize by stripping tashkeel and small marks, and unifying alef/hamza/ya/ta marbuta variants. Also apply Maghribi orthography variants (dotting of fa/qaf) so a user typing standard Arabic finds Warsh text.
- Use the same normalization function for the query and the stored text. Put it in one shared function with tests.
- Search results are scoped to the active riwaya.

## 7. What could silently break if we do this naively

| Risk | Symptom | Mitigation |
|---|---|---|
| Bookmarks keyed on `(surah, ayah)` only | After switching riwaya, a bookmark opens a different verse (or a non-existent verse, e.g. Hafs 1:7 beyond Warsh's count, or a Warsh count that has fewer verses) with no error | `riwaya` column, or map through `verse_map` (§1) |
| Hard-coded 6236 / 114 / 604 / per-surah counts | Progress %, khatmah tracker, "verse of the day", range validation off by a few | Compute from DB per riwaya |
| Migration rebuilds the PK wrongly or drops the created_at data | Lost bookmarks | Transactional migration, backup, upgrade test on a real v(N) DB |
| Basmalah handling (Fatiha 1:1 vs. unnumbered) | Fatiha displays 8 lines or the wrong verse numbers | Explicit per-riwaya rule and a Fatiha test |
| Hafs translations/tafsir shown on Warsh verses | The translation is attached to the wrong verse. Nobody notices without checking | Map via `verse_map`, or hide them for Warsh at first |
| Audio cache key without riwaya | Warsh mode plays cached Hafs audio | Include riwaya and reciter in cache path |
| Hafs audio timings reused | Highlight drifts, wrong ayah highlighted | Timings per riwaya/reciter |
| Missing font glyphs | Marks disappear and change the reading. This is hard to see in QA without an Arabic reader | Glyph coverage script, real-device test, Warsh font |
| Search normalization differences | Warsh verses not found by common queries | Normalize Maghribi variants, test with real queries |
| Unicode normalization (NFC/NFD) applied to text | Mark order changes, rendering differs | Store text exactly as sourced. Only normalize `text_search` |
| Import script pulls mixed sources | Hafs orthography inside Warsh text | Automated checks in §2 and reviewer sign-off |
| Share/copy text, deep links, widgets, notification payloads with `surah:ayah` | The link opens a different verse in the receiver's riwaya | Include riwaya in the payload and the link |
| Juz/hizb/sajdah markers reused from Hafs | Markers at the wrong verses | Per-riwaya tables |
| Riwaya read from a global at query time | A race after the setting changes, and the UI shows a mix of both | Pass riwaya explicitly (§1.4) |
| Default (fresh install / old data) | Existing users flipped to Warsh or crash | Default `hafs`; backfill `hafs` for all old rows |

## 8. Rollout steps

1. **Research (before code):** confirm the Warsh source, its verse count and its license. Confirm the audio sources and the font licenses. Decide the page-layout approach (§5). Deliver: a short decision note.
2. **Data pipeline:** an import script producing `warsh_ayahs` rows and `verse_map`, with the checks from §2. Keep the script in the repo so the data is reproducible.
3. **Schema migration:** §1.1 with tests (fresh install, upgrade from v(N), upgrade with many bookmarks).
4. **Repository layer:** add `riwaya` parameters everywhere and remove hard-coded constants (§7). Behavior for Hafs must stay identical. Add a regression test that compares Hafs output before and after.
5. **UI:** riwaya setting, font selection, reciter list filter, hide features that are not available for Warsh (translations, page view) rather than showing wrong data.
6. **Audio:** per-riwaya reciters, cache keys, timings.
7. **Review:** a Warsh-literate reviewer checks the text rendering and audio alignment on the surahs where numbering differs (Al-Fatiha, and a sample of others chosen from the `verse_map` non-exact rows).
8. **Release:** ship behind a setting, default Hafs, and stage the rollout. Keep the pre-migration DB backup for one release.

## 9. Open questions for you

- Which Warsh mushaf edition should be the reference (verse count, pagination)? This decides the source and the font.
- Should a bookmark follow the user across riwayat (mapped) or belong to the riwaya it was created in? The plan above defaults to per-riwaya. Mapping is an optional add-on.
- Is the app allowed to redistribute the KFGQPC data and fonts under its license?
- Are translations/tafsir in scope for Warsh in v1?


### FINAL MESSAGE
I wrote the plan to `/tmp/eval0-baseline-mio9sh4c/plan.md`. The directory was empty, so it is based on the schema you described, not your code. I had no web access here, so anything I couldn't confirm offline is marked **VERIFY**.

- **Verse numbering:** Warsh uses the Madani verse count, not Hafs's Kufan count. The Fatiha basmalah and the disconnected-letter verses are counted differently, and some verses are split or merged. So `(surah, ayah_number)` no longer identifies a verse on its own. This is the main thing that would silently break.
- **Data model:** the plan adds a `riwaya` column to `ayahs` and `bookmarks` and rebuilds both tables in one transaction. A `verse_map` table, generated offline by word alignment, handles moving between riwayat. Every repository method takes `riwaya` explicitly.
- **Warsh text:** KFGQPC is the preferred source. Tanzil, as far as I know, only has Hafs, so it is useful only as a cross-check. The plan includes automated verse-count and orthography checks and a review by someone who reads Warsh.
- **Fonts:** Warsh needs the Maghribi letter forms, such as the fa and qaf dots, so you need a separate Warsh font. Per-page glyph fonts are Hafs-specific. The plan includes a script to check glyph coverage.
- **Audio:** it must be Warsh recitation, with cache keys and timings kept per riwaya and reciter. Otherwise Warsh mode can play cached Hafs files.
- **Also covered:** page layout (don't assume 604 pages), search normalization, and a table of about 14 silent-breakage risks with mitigations. Examples are bookmarks opening the wrong verse, translations attached to the wrong verse, hard-coded 6236/604 constants, and shared links.
- **Open questions for you:** which Warsh mushaf edition is the reference, whether bookmarks should follow you across riwayat, whether the KFGQPC license allows redistribution, and whether translations are in scope for v1.

If you point me at the Flutter project, I can turn the plan's audit lists into a concrete list of files to change.