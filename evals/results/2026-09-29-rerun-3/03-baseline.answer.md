### FILE plan.md
# Quran App Plan: Printed Mushaf Pages, Word Highlight, Tap-for-Meaning

## Recommendation in one paragraph

Use **Flutter** (one codebase for Android and iOS). Render each mushaf page as **real text using the per-page King Fahd Complex (QCF) glyph fonts**, laid out line by line from a **mushaf layout dataset**. Do not use scanned page images. Drive audio with **just_audio + audio_service**, and sync the highlight from **word-level timing segments**. Store everything in a local **SQLite** database. Get the data from **Quran Foundation / quran.com API v4** and **QUL (Quran Universal Library)**.

Why glyph fonts and not page images: images only give you a picture. To highlight or tap a word you need a bounding box for every word on every page, and those datasets are scarce. Public ayah-level coordinate sets exist, but not reliable word-level ones. With the QCF fonts, every word is its own glyph code, so each word is a real widget or span that you can colour and tap. The page still looks like the printed Madani mushaf (15 lines, 604 pages).

## Building blocks

| Concern | Choice | Notes |
|---|---|---|
| App framework | Flutter (Dart) | Full control of text rendering; good custom-paint and gesture support. React Native is workable but font/RTL layout control is harder. |
| Page text and glyphs | QCF per-page fonts (v1, or v2/v4 if you want tajweed colours) | 604 small font files, one per page. Download on demand and cache. Register each with `FontLoader`. |
| Page layout | QUL mushaf layout data (page → lines → words) | Tells you which words go on which of the 15 lines, plus line type (text, surah header, bismillah). This is what makes it match the printed page. |
| Word and verse data | quran.com API v4 (`/verses/by_page/{n}?words=true`) | Gives per-word glyph code, position, translation, transliteration, verse key. Fetch once, then ship or cache in SQLite. |
| Audio playback | `just_audio` + `audio_service` | Background and lock-screen controls, gapless playback, precise position stream. |
| Word timings | quran.com recitation endpoints with `segments=true` (chapter or verse audio) | Each segment is `[word_index, start_ms, end_ms]`. Only some reciters have segments; pick launch reciters from that set. |
| Local storage | SQLite via `drift` | Tables: `pages`, `lines`, `words`, `translations`, `timings`, `downloads`. |
| State management | Riverpod | Fine-grained providers so only the highlighted word's line rebuilds. |
| Word meaning UI | Bottom sheet | Translation, transliteration, root/morphology, verse translation, tafsir link. |
| Morphology (optional) | Quranic Arabic Corpus data or QUL morphology | Check the licence before shipping. |

## How the pieces fit

```
 QUL layout + quran.com words ──► import script ──► SQLite (bundled seed DB)
                                                        │
 QCF font files (cached per page) ──► FontLoader        │
                                                        ▼
  PageView (604, RTL) ──► MushafPage(page n)
                            └─ 15 × LineWidget (fitted to page width)
                                 └─ WordSpan × N  (glyph in page font)
                                       ▲ tap ──► WordDetailSheet
                                       │ highlight
  Audio: just_audio ──► positionStream ──► TimingIndex (binary search)
                                       └─► currentWordProvider (verse_key, word_idx)
```

### 1. Page rendering
- `PageView.builder` with `reverse: true` for RTL swiping; 604 items, lazy.
- For page *n*, load the page font, then build 15 line widgets from the `lines` table.
- Justify each line to the page width. Measure the line's natural width with `TextPainter`, then either scale the font (`FittedBox`) or distribute the remainder as word spacing. Centre surah headers and bismillah lines. Draw the surah banner with a custom asset or painter.
- Keep line height and page margins fixed so the page matches the printed proportions on any screen. Scale from the page width.
- Preload fonts for pages n±2. Ship pages 1–2 and any small subset in the app bundle so first launch works offline.

### 2. Word highlight during playback
- Data: for each reciter and surah, a list of `(verse_key, word_index, start_ms, end_ms)` sorted by start.
- Playback: use one audio file per surah where the reciter offers it (gapless, one continuous position). Otherwise use per-verse files in a `ConcatenatingAudioSource`, and add the verse's offset to the segment times.
- Sync: listen to `positionStream` (about 30–60 ms updates is enough). Binary-search the timing list, and only emit when the word index changes.
- UI: `currentWordProvider` holds `(verseKey, wordIdx)`. Each `WordSpan` watches it through `select`, so only the old and new words repaint. Also auto-turn the page when the current word is on another page, but pause the auto-turn if the user has swiped manually.
- Also support verse-level highlight and "play from this word or verse" from long-press.

### 3. Tap a word for its meaning
- Each word is a `GestureDetector` or `TextSpan` with a tap recogniser. Store `word_id` on it.
- Tap opens `WordDetailSheet`, which reads `words` and `translations` from SQLite: Arabic word, transliteration, translation, root and morphology (if licensed), then verse translation and a link to tafsir.
- Keep the sheet non-blocking. It should not stop playback, and it should keep the word highlighted while open.
- Language: ship English word-by-word first, and make the translation source a setting.

### 4. Offline and downloads
- Seed DB in the app bundle: layout + Arabic words + one word-by-word translation.
- On-demand downloads: page fonts (or all at once, as a "download mushaf" option), audio per surah, timing files per reciter. Track them in a `downloads` table.

## Milestones

1. **Data pipeline (script, not app).** Pull layout + words for all 604 pages; build the seed SQLite DB; verify 604 pages × 15 lines and word counts per surah.
2. **Static mushaf reader.** Font loading, line fitting, RTL paging, surah headers. Compare against a printed Madani mushaf page by page for a sample of pages.
3. **Tap for meaning.** Word taps and the detail sheet.
4. **Audio.** Playback, background controls, one reciter with segments; word highlight and page auto-turn.
5. **Offline and polish.** Downloads, more reciters, dark/sepia themes, accessibility (font scaling within the page-fit rules), bookmarks and last-read.
6. **Device testing.** Small phones, tablets, foldables, and both platforms' font rendering. Check that lines stay within bounds and that highlight timing looks right on real devices.

## Risks and things to verify before committing

- **Licensing.** Check terms for each of these separately: QCF fonts (King Fahd Complex), the layout dataset, each reciter's audio and timings, translations, and morphology data. Some require attribution or forbid modification. Get this settled early because it can change the reciter list.
- **API access.** quran.com's API has moved to Quran Foundation's hosted APIs, which may require client credentials. Confirm current endpoints, auth, and rate limits, and plan to bundle the data rather than call it live from the app.
- **Timing coverage.** Word-level segments do not exist for every reciter. If a reciter has none, fall back to verse-level highlight.
- **Font versions.** v1 fonts have some known glyph-mapping quirks on some renderers, and v2/v4 differ in size and tajweed colouring. Prototype one page in each and pick before building the pipeline around it.
- **Line fitting.** Justification is the hardest visual part. Prototype it in milestone 2 with the widest and narrowest lines (for example, pages 1, 2, and dense pages near the end of the mushaf).
- **Text correctness.** This is scripture: validate imported text against a second source and never edit glyphs by hand.


### FINAL MESSAGE
I wrote the plan to `plan.md`. I wrote it from what I know and didn't check any of the APIs, licences or datasets live, so the data sources and licensing need verifying before you commit to them (more below).

**Recommendation**
- **Framework:** Flutter, for one codebase on Android and iOS.
- **Pages:** render them as real text using the King Fahd Complex per-page glyph fonts (QCF), one font per page across the 604 pages. Lay them out with a mushaf layout dataset such as QUL's, which says which words go on which of the 15 lines. This still looks like the printed Madani mushaf.
- **Why not page images:** they only give you a picture. Word-level tap and highlight would need a bounding box for every word, and I don't know of reliable public word-level datasets. With glyph fonts, each word is its own tappable, colourable span.
- **Data:** quran.com / Quran Foundation API v4 and QUL supply the words, per-word translations and reciter timings. An import script builds a SQLite database (via `drift`) that ships with the app.
- **Audio and highlight:** `just_audio` + `audio_service` play the recitation. The position stream is matched against word timing segments (`[word, start_ms, end_ms]`), and a Riverpod provider holds the current word. Only the old and new words repaint, and the page turns automatically when the current word is on the next page.
- **Tap for meaning:** tapping a word opens a bottom sheet. It shows the translation, transliteration and root, then the verse translation and a tafsir link. Playback keeps going while it's open.

**Things to settle early** (all in the plan)
- **Licensing:** the fonts, layout data, each reciter's audio, translations and morphology data each have their own terms. This can change which reciters you can ship.
- **API access:** the API may now require credentials, so bundle the data rather than calling it live.
- **Timing coverage:** only some reciters have word-level timings. Reciters without them fall back to verse-level highlight.
- **Font version:** prototype v1, v2 and v4 on one page before choosing.
- **Line justification:** fitting each line to the page width is the hardest visual part, so prototype it in the static reader milestone.

The plan also has a milestone order, from the data pipeline through to device testing.