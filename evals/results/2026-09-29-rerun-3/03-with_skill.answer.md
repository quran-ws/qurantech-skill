### FILE plan.md
# Quran app plan: printed mushaf, word highlight during recitation, tap-for-meaning

Target: Android and iOS. Riwayah: Hafs (see "Constraints").

## Recommended stack

| Need | Block | Why |
|------|-------|-----|
| Printed mushaf pages, word-addressable | `quran-svg-elements` data, drawn by `quran-engine` (`QvpKit` on iOS, `ws.quran:qvp-android` on Android) | Elements splits the KFGQPC 1441H print into words keyed `surah:ayah:word`. Its SVG is too dense for phones, so the native engine renders the same words from compact QVP pages. It also gives `hitTest` and `highlight`. |
| Text for search, copy and accessibility | `quran-text` | The page files hold no text. Join on the word key, never on strings. |
| Recitation audio and word timings | Quran Foundation Audio API (segments `[word_index, start_ms, end_ms]`). QuranPedia timing files or your own alignment are fallbacks. | No Quran.ws block ships audio. |
| Word meanings | Quran Foundation API word-by-word translation set, or QuranPedia `meanings` (gharib meanings) | No block covers meanings. Both key on surah:ayah:word. |
| Optional: ornaments | `quran-assets` | Only after checking each asset's `license.status`. Scan-derived ornaments are provisional and non-commercial. |

Not needed for v1: `quran-svg` (ayah-level only), `quran-tajweed`, `qiraat-ayah-map` (Hafs only).

## How they fit together

The word key `surah:ayah:word` (1-based within the ayah) is the join key everywhere.

```
QVP page (cdn.quran.ws/qvp/<pinned>/NNN.qvp + NNN.words.json)
   |  draws words natively; hitTest(x,y) -> wordKey ; highlight(wordKey)
   v
Reader screen  <-- audio player position (ms) --> timing table [wordKey, start, end]
   |
   +-- tap  -> wordKey -> meanings store -> bottom sheet (meaning + reciter-agnostic)
   +-- play -> binary-search timings at currentTime -> highlight(wordKey)
```

1. **Render.** Load one page at a time from a pinned CDN folder (never "latest"). Cache pages on disk. Draw with the engine at `max(2, devicePixelRatio)` backing scale. Store the mushaf key with every page number.
2. **Highlight.** On each player position tick, binary-search a sorted `[start_ms, end_ms, wordKey]` array for the reciter and surah. Call `highlight(wordKey)`, and turn the page when the word is on another page. An ayah can continue onto the next page, so check `ayahWordCount(s,a).complete`.
3. **Tap.** `hitTest(x, y, {maxDistance})` returns the word. Convert view coordinates to page units first: subtract the layout offset, divide by scale. Use the key to look up the meaning in the local store and show a bottom sheet. Optionally play that word's audio segment.
4. **Meanings.** Download the word-by-word set at first run or per surah, into SQLite keyed by `(dataset_id, wordKey)`. Label the dataset and its author in the sheet, as a translation and not as Quran text.
5. **Audio.** Model rawi, reciter and recitation separately, with timings attached to the recitation. Show the reciter name and never auto-play. Support background playback and lock-screen controls. Pre-buffer the next ayah and start at ayah boundaries. Allow downloads per surah.
6. **Search and copy.** Use `quran-text`, joined by ayah or word key.

## Constraints and risks

- **Hafs only.** Elements and the engine split only the Hafs KFGQPC print. Other riwayat would need `quran-svg` (ayah-level, so no word highlight) plus `qiraat-ayah-map`.
- **Beta blocks.** Elements and the engine are Beta. Pin exact versions and verify the registry versions: the README pins say 0.2.2, while releases are at 0.3.x. Verify `hitTestViewEx` and `hitBoxes()` exist in your installed version before using them.
- **Word-count mismatch.** Elements has 77,432 words and quran-text 77,434, and the cause is unknown. Spot-check word boundaries across the surahs and add a CI test on the join.
- **Timing alignment.** Confirm that the timing set's word numbering matches Elements' keys for a sample of ayahs, including surah openings. Timings can be missing for some reciters, so degrade to ayah-level highlight and say so.
- **Licences.** Page data and artwork carry KFGQPC terms, not MIT. The Elements bundle LICENSE was a placeholder at last report, so confirm before distributing in a store app. Check the audio API and meaning-set terms too.
- **Adab.** Never truncate or alter text. Keep Quranic text out of logs (log `surah:ayah:word`). Label meanings as translations or explanations.
- **Accessibility.** The canvas exposes nothing to screen readers. Provide a text view or an accessible overlay built from `quran-text`.
- **Dark mode.** Set ink and paper colours explicitly. Do not invert.
- **Navigation.** The mushaf is right-to-left, so swiping left goes to the next page. Read page and juz divisions from data, and do not hard-code them.

## Milestones

1. Spike: draw one page on both platforms from pinned QVP data. Verify `hitTest` returns the correct word keys.
2. Page reader: navigation, zoom, last-read position stored with the mushaf key, offline page cache.
3. Tap-for-meaning: meanings store, bottom sheet, dataset attribution.
4. Audio: player, timings, word highlight, page-turn following, background playback.
5. Offline downloads for audio, meanings and pages.
6. Hardening: join tests against `quran-text`, accessibility text view, licence review, pinned-version upgrade process.

## Open questions

- Which reciters must ship at launch? This depends on which have word segments.
- Which languages are needed for meanings?
- Is Hafs alone acceptable for launch?
- Will you use React Native (Android only) or Flutter (`qvp_flutter`, which resolves only to 0.2.x), or fully native? This plan assumes native.


### FINAL MESSAGE
I wrote the plan to `/tmp/eval3-with_skill-w1c5e5m_/plan.md`. It comes from the Quran.ws skill docs, and I haven't built or run anything yet.

**Building blocks**
- **Pages:** use `quran-svg-elements` data, drawn on the phone by `quran-engine`. The engine ships as `QvpKit` on iOS and `ws.quran:qvp-android` on Android. Elements splits the printed Hafs mushaf into words keyed `surah:ayah:word`. Its SVG is too heavy for phones, so the engine draws the same words from compact page files and gives you `hitTest` and `highlight`.
- **Text:** use `quran-text` for search, copy and screen readers. The page files contain no text.
- **Audio and word timings:** use the Quran Foundation Audio API, which has per-word start and end times for some reciters. No Quran.ws block ships audio.
- **Word meanings:** use the Quran Foundation word-by-word translations or QuranPedia's `meanings`. Neither is a Quran.ws block.

**How they fit together**
- The word key `surah:ayah:word` joins everything.
- **Playing:** on each player tick, binary-search the timing list for the current word and call `highlight(wordKey)`.
- **Tapping:** `hitTest` gives the word key, and you look up the meaning in a local database and show it in a bottom sheet.

**Risks**
- **Hafs only:** the word-level blocks cover only Hafs. Other riwayat would only get ayah-level tapping, with no word highlight.
- **Beta status:** both Elements and the engine are Beta. Pin exact versions.
- **Word-count mismatch:** Elements has 77,432 words and `quran-text` has 77,434, and the cause is unknown. The plan includes a test on that join.
- **Licences:** page data and artwork carry King Fahd Complex terms, and the Elements license file was a placeholder at last report. Confirm before you ship.
- **Screen readers:** the canvas is invisible to them, so you need a text view alongside it.

The plan also has milestones and a few open questions. The main one is which reciters must ship at launch, since that depends on who has word-level timings.