### FILE plan.md
# Plan: Quran app (Android + iOS) with printed mushaf, word highlight, tap-for-meaning

Assumption: **Hafs** riwayah, KFGQPC Madani mushaf (604 pages). This matters because the word-level blocks are Hafs-only. If you need another riwayah, see "Open questions".

## Building blocks

| Need | Use | Why |
|---|---|---|
| Real printed pages, drawn natively | **quran-engine** (`QvpKit` on iOS via SwiftPM, `ws.quran:qvp-android` on Android) | SVG this dense performs poorly on phones. The engine draws the pages natively and provides word hit-testing and highlighting. |
| Page data | `cdn.quran.ws/qvp/<version>/NNN.qvp` plus `NNN.words.json` | The packages do not bundle pages. Pin an exact `vX.Y.Z` folder; these are immutable. |
| Word identity, text, numbering | **quran-text** (`quran-text-swift`, Kotlin library from the repo) | Uses the same `surah:ayah:word` key as the engine. Also gives verified text for accessibility labels, search and copy. |
| Audio and word timings | Third party, since no block covers audio. Quran Foundation Audio API (segments `[word, start_ms, end_ms]`) or QUL segmented audio sets (downloadable, so good offline) | Word-level timestamps are needed for the moving highlight. |
| Word meanings | Third party: Quran Foundation API (word-by-word translation, transliteration, morphology) or QUL downloads (morphology, translations) | No block ships meanings. QUL works offline; the API stays current. |
| Optional later | `quran-tajweed` (Hafs), `quran-assets` (ornaments, check licences per asset) | Not needed for v1. |

**Not chosen:**
- `quran-svg` and `quran-svg-elements` are web-oriented. Use them only if you add a web client. Elements uses the same word keys, so nothing is lost.
- MushafImad and mushaf-imad-android are complete readers, but they are line images with ayah-level timing. They do not give word-level hit-testing on the real pages.
- Flutter or React Native: the engine has wrappers for both, but the RN wrapper is Android only. Native Swift and Kotlin is the simplest fit.

## How they fit together

```
                 ┌────────────── shared key: surah:ayah:word ──────────────┐
                 │                                                          │
 quran-engine ── page render, hitTest(x,y) → word key       highlight(key) ◄┤
 (QVP pages)                    │                                           │
                                ▼ tap                                       │
                 word key ──► meaning lookup (local DB) ──► bottom sheet    │
                                                                            │
 audio player ── currentTime ──► binary search in timing array ─────────────┘
 (reciter + segments)            (word key active now)
```

1. **Render.** Fetch the page's `.qvp` and `.words.json` for the current page from the pinned CDN version, and cache them on disk. Draw with the engine on a canvas at device pixel ratio (never extra supersampling). Page through 604 pages RTL.
2. **Tap → meaning.** On tap, convert to page coordinates (subtract layout offset, divide by scale) and call the engine's hit-test to get the word key. Look up that key in a local word-meaning table (translation, transliteration, root and morphology). Show it in a bottom sheet. Optionally offer word audio, the ayah's translation, and tafsir.
3. **Playback → highlight.** Load the timing segments for the selected recitation, sorted, once per surah. On each player position tick (about 30-60 ms), binary-search the active word key. If it changed, call the engine `highlight` on it. If it is on the next page, auto-turn the page. Keep the ayah highlight as a fallback for reciters that have no word segments.
4. **Join on keys only, never on strings.** Word keys are 1-based within the ayah. quran-svg-elements has 77,432 words and quran-text 77,434, so a few word boundaries differ. Spot-check the join away from page 1 and write a test that compares the counts per ayah across the three sources (engine, text, timings).

## Data model (minimal)

- `Recitation { id, reciter, rawi: hafs, style, audioUrlPattern, hasWordSegments }`. Keep rawi, reciter and recitation separate.
- `WordTiming { recitationId, surah, ayah, word, startMs, endMs }`, indexed by (recitationId, surah, ayah).
- `WordMeaning { surah, ayah, word, translation, transliteration, root?, morphology? }` with language and source attached. Label these as translations.
- Every ayah reference carries `{surah, ayah, counting}` (Kufan for Hafs), so a later riwayah does not break bookmarks.

## Build order

1. Engine spike on both platforms: render page 1 and page 2 from a pinned CDN version. Confirm `hitTest` returns word keys. Check the installed engine version for any API you rely on. `hitBoxes` and `hitTestViewEx` are in the repo but were not in the published 0.3.0 package.
2. Reader shell: 604-page RTL pager, page cache, jump to surah, juz or page. Use `quran-text` for the index and navigation data.
3. Word meanings: import one word-by-word dataset into SQLite (Room on Android, GRDB or SQLite on iOS) and add the tap → bottom-sheet flow. Check the licence of the dataset first.
4. Audio: streaming player with background playback and lock-screen controls, reciter picker with the reciter name always visible. No auto-play.
5. Word highlight: timing loader, binary search, engine `highlight`, page auto-turn. Add tap-a-word-to-start-from-here.
6. Offline: bundle core content (pages 1-604 as QVP if size allows, or download on first launch, plus the meaning DB). Audio downloads per surah with resume and delete.
7. QA and accessibility: Dynamic Type for non-Quran UI, VoiceOver and TalkBack labels using `quran-text` for the word at focus, and a CI check that text is byte-exact against the verified source.

## Risks and things to verify

- **Blocks are Beta.** quran-engine and quran-svg-elements are Beta. Pin versions and expect API changes.
- **Version drift.** The README pins (0.2.2) lag the published releases (0.3.x). Check each registry, and note that Flutter's `^0.2.2` does not resolve to 0.3.x.
- **Licences.** The page data carries KFGQPC terms, not MIT. Confirm redistribution rights before shipping pages inside the app binary. Also check each audio, translation and word-meaning source individually.
- **Timing quality.** Not every reciter has word segments. Check coverage before picking the launch reciters, and test idgham, elongation and pause edges by ear.
- **Ayah spanning pages.** An ayah can continue on the next page, so highlight and auto-turn logic must handle a word on page N+1 while the ayah started on page N.
- **Perf.** Cap canvas pixels to limit memory, and fetch pages one at a time.

## Adab checklist

- Never alter, truncate or strip diacritics from the text, and never hand-type Quranic text.
- Keep Quranic text out of logs and test fixtures; log `surah:ayah:word` keys instead.
- Never auto-play. Audio starts only after user action and at ayah boundaries. Always show the reciter's name.
- Show meanings as translations, labelled with the source. If tafsir is added later, use authoritative sources only, not AI-generated text.

## Open questions

- Other riwayat (e.g. Warsh)? The engine and elements are Hafs-only. The fallback is `quran-svg` (ayah-level only) plus `qiraat-ayah-map` and per-riwayah audio.
- Which languages for word meanings, and must it work fully offline?
- Preferred reciters (this decides whether word segments exist for them).
- Native Swift/Kotlin vs Flutter?


### FINAL MESSAGE
I wrote the plan to `/tmp/eval3-with_skill-30jnmysz/plan.md`. It assumes the Hafs riwayah, because the word-level blocks are Hafs-only.

**Building blocks**
- **Page rendering and tap detection:** `quran-engine`. It draws the printed KFGQPC pages natively and works out which word was tapped. It has a Swift package for iOS (`QvpKit`) and a Maven package for Android. The page files are separate and come from `cdn.quran.ws/qvp/<pinned version>/`.
- **Text and word numbering:** `quran-text`. It uses the same `surah:ayah:word` key as the engine, and gives you verified text for accessibility labels.
- **Audio and word timings:** a third-party source, since no block covers audio. Quran Foundation or QUL both provide per-word start and end times.
- **Word meanings:** also third-party. Quran Foundation (online) or QUL (downloadable, so it works offline) both have word-by-word data.
- **Not needed for v1:** `quran-svg` and `quran-svg-elements` are web-oriented, and SVG this dense is slow on phones. The MushafImad packages don't give word-level tapping on the real pages.

**How they fit**
- The `surah:ayah:word` key is what connects everything.
- **Tap:** the engine's hit-test returns the word key, you look it up in a local meanings table, and a bottom sheet shows it.
- **Playback:** the player's position is matched against the sorted word timings with a binary search. The engine then highlights the active word, and the page turns automatically when the word is on the next page.

**Things to check before you build**
- The engine and elements blocks are Beta, so pin versions.
- The page data carries KFGQPC terms, not MIT. Confirm you can bundle it in the app.
- Not every reciter has word-level timings. Check coverage for your chosen reciters first.
- `quran-svg-elements` and `quran-text` differ by two words (77,432 vs 77,434), so test the key join.

The plan also covers the minimal data model, a seven-step build order, the adab checklist, and open questions. The main open question is whether you need riwayat other than Hafs.