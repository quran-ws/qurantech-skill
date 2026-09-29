### FILE plan.md
# Quran App Plan: Mushaf Pages, Word Highlighting, Word Meanings

## Recommendation

Build with **Flutter** (one codebase for Android and iOS) unless your team is already strong in React Native. Everything below works in either. The three data problems (page layout, audio timing, word meaning) are solved by **three datasets keyed to the same word ID**. The UI is a thin layer on top.

## Building blocks

### 1. Page layout: the real printed mushaf
Two viable approaches:

| Option | What it is | Pros | Cons |
|---|---|---|---|
| **A. Per-page QCF fonts (King Fahd Complex / Quran.com "V1"/"V2" fonts)** | One font per page (604) where each word is a single glyph, rendered as text | Exact Madinah Mushaf layout, sharp at any size, text is selectable, per-word widgets are easy | ~604 font files (~a few tens of MB; download lazily), need glyph-to-word mapping |
| **B. Page images (e.g. Madinah mushaf PNG/SVG) + word bounding boxes** | Image per page plus coordinates per word | Simplest visual fidelity | Large assets, blurry when zoomed (unless SVG), needs coordinate data per word, no reflow or dark mode |

**Pick A** (QCF v2 fonts, or the newer Uthmani-based line-by-line layout). Word-level data (`page_number`, `line_number`, `position`, `code_v2`) is available from the Quran.com API. Render each line as a `Row`/`RichText` of word spans, each span a tappable, highlightable unit. Layout data (which words on which line of which page, 15 lines/page) comes from the same source, so you never compute line breaking yourself.

Check licensing: the KFGQPC fonts have their own terms, and Quran.com's are distributed for Quran use. Confirm before shipping commercially.

### 2. Data source
- **Quran.com API v4 / quran-com open data**: verses, words (with `page_number`, `line_number`, `code_v2`, `audio_url`, `translation`, `transliteration`), chapters, recitations.
- **Tanzil / QUL (Quran Universal Library, by Tarteel)**: downloadable datasets for text, mushaf layouts, word-by-word translations, and audio segments. QUL is good for **offline, bundled** data.
- Prefer downloading once and shipping in a local **SQLite** DB rather than calling the API at runtime.

### 3. Audio + word timing
- Use a reciter that has **word-level segment timestamps** (Quran.com recitations API `?segments=true`, or QUL audio segment data). Format per verse: `[word_position, start_ms, end_ms]`.
- Playback: `just_audio` + `audio_service` (Flutter) for background play, lock-screen controls, and gapless verse playlists. (RN equivalent: `react-native-track-player`.)
- Prefer per-verse audio files (or one file per surah with verse timestamps) so seeking to a verse is trivial. Support download for offline.

### 4. Word meaning on tap
- Word-by-word translation and transliteration come from the same word records (Quran.com `words` data / QUL word-by-word datasets).
- Optional depth: root, lemma, grammar from the **Quranic Arabic Corpus** (check its license) for a richer "word details" sheet; tafsir per verse from QUL/Quran.com.
- Show in a bottom sheet: Arabic word, transliteration, translation, root, then a "verse tafsir" link.

## How they fit together

```
            +------------------+
            |  SQLite (local)  |   words(id, verse_key, page, line, position,
            |                  |          code_v2, translation, transliteration, root)
            |                  |   segments(verse_key, word_pos, start_ms, end_ms, reciter)
            +--------+---------+
                     |
       +-------------+--------------+
       |                            |
 Mushaf renderer               Audio controller
 (page -> lines -> words)      (just_audio position stream)
       |                            |
       |   current word id  <-------+  binary-search segments by position
       v
 Highlight state (single source of truth: currentWordId)
       ^
       |  tap word
 Word meaning bottom sheet (reads words table)
```

Key idea: **`(verse_key, word_position)` is the shared key.** The renderer, the audio segments, and the meanings all reference it.

### Highlighting flow
1. Player emits position (~every 50 ms; use `positionStream` with a fast update interval).
2. Controller finds the active verse (playlist index) and binary-searches that verse's segments for the word whose `[start, end)` contains the position.
3. It publishes `currentWordId` through a state holder (Riverpod/Bloc `StateNotifier`).
4. Only the word widget whose id matches rebuilds (use `select`/per-word listeners). Do not rebuild the whole page at 20 Hz.
5. If the word is on another page, auto-turn the `PageView` to that page (with a "follow audio" toggle users can disable when they scroll manually).

### Tap flow
Word widget `onTap` -> set `selectedWordId` -> open bottom sheet with data from SQLite. Optionally offer "play from this word/verse", using the same segment data.

## Suggested stack (Flutter)
- UI: Flutter, `PageView` (RTL) with one page widget per mushaf page
- State: Riverpod
- DB: `drift` (SQLite) with a prebuilt DB shipped in assets
- Audio: `just_audio`, `audio_service`
- Fonts: `FontLoader` to lazily register per-page fonts; cache on disk
- Downloads: `dio` + local storage for audio/fonts

## Milestones
1. **Data pipeline (script, not app):** pull words, layout, segments for one reciter, build the SQLite DB. Validate that word counts per verse match across the three datasets.
2. **Page renderer:** render pages 1-604 from local data, RTL paging, per-page font loading, dark/sepia themes.
3. **Word tap + meaning sheet.**
4. **Audio playback:** verse/surah playback, background audio, download manager.
5. **Word sync:** segments, highlight, follow-audio page turning, seek-by-word.
6. **Polish:** multiple reciters, translations, bookmarks, last-read, accessibility, offline packs.

## Risks and open questions
- **Licensing:** fonts, audio, translations, and corpus data each have separate licenses. Get this settled before building on them.
- **Segment quality:** timing data varies by reciter, and some reciters have none. Limit the launch reciter list to ones with segments.
- **Word-count mismatches** between layout data (glyph-per-word) and segment data (esp. at verse-end markers and sajda signs). Handle the verse-end marker as a non-word glyph in the renderer.
- **Font size on device:** QCF is tuned for fixed page proportions. Scale the whole page to fit the width rather than reflowing.
- **Performance:** 604 fonts loaded lazily (current page +/- 2); keep memory bounded.
- Verify current API/dataset field names and licenses against the live docs, since they change over time. I haven't checked them in this session.


### FINAL MESSAGE
I wrote the plan to `plan.md`. I haven't checked the dataset field names, APIs or licenses against their live docs, so verify those before building on them.

- **Framework:** Flutter, so one codebase covers Android and iOS. React Native would work too.
- **Mushaf pages:** Use the per-page QCF fonts that Quran.com distributes, where each word is one glyph. This gives the exact Madinah layout and makes each word its own tappable widget. Page images would be simpler, but they are heavy and blurry when zoomed, and they need bounding boxes for every word.
- **Data:** One local SQLite database built from Quran.com and QUL data. It holds words with page, line and position, plus word-by-word translations, transliteration and audio segment timings.
- **Audio timing:** Pick reciters that have word-level start and end times. Playback uses `just_audio` and `audio_service`.
- **How they connect:** The shared key is `(verse_key, word_position)`, so layout, audio timings and meanings all point at the same word.
- **Highlighting:** The player position is matched to a word by binary search on that verse's timings. That word's id goes into one state holder, and only that word rebuilds. The page turns automatically to follow the audio, with a toggle to switch that off.
- **Word meanings:** Tapping a word opens a bottom sheet showing its translation, transliteration and root.

`plan.md` also has the milestone order and the risks. The main risks are licensing, reciters that have no word timings, and word-count mismatches at verse-end markers.