### FILE answer.md
# Data sources for a Quran reading app: ~50 languages + recitation audio with word highlighting

I'm assuming "reading app" with "recitation" means the Quran. If it isn't, most of this doesn't apply.

I wrote this from memory and did not check live docs. Before you commit, confirm current API auth, rate limits, and licence terms for each source. Quran Foundation has been changing its API access model.

## Recommendation

Use **Quran Foundation's Quran.com API (v4)** for the text, translations, and audio timing. Use **Quranic Universal Library (QUL)** for bulk data. Don't build on a live API alone.

| Need | Primary source | Fallback |
|---|---|---|
| Arabic text (Uthmani, IndoPak, word-by-word) | Quran.com API v4 / QUL | Tanzil.net (text only, no API) |
| Translations, ~50 languages | Quran.com API v4 translations, plus QUL bulk downloads | Tanzil, AlQuran.cloud |
| Recitation audio with word timings | Quran.com API v4 (`/recitations`, `/chapter_recitations`, `segments`) | QUL audio and segment downloads |
| Verse-level audio only | EveryAyah.com, or Quran.com CDN | AlQuran.cloud audio |
| Fonts and page layout (Mushaf-accurate) | QCF / KFGQPC fonts via QUL | Uthmani Hafs font |

## Why this stack

**1. Quran.com API v4 is the only source I know of with word-level timing.**
- Verse audio endpoints can return `segments`. These are `[word_position, start_ms, end_ms]` arrays.
- Word highlighting then needs only an `<audio>` element, its `timeupdate` event, and a lookup into that array.
- Most other audio sources give you verse-level MP3s only. You would have to force-align the words yourself.

**2. QUL (from Tarteel and the Quran Foundation ecosystem) is better for bulk data.**
- It offers downloadable SQLite and JSON for text, translations, tafsir, word-by-word data, and audio segments.
- You get versioned snapshots, so you don't depend on API uptime or rate limits.
- Translation and word-by-word data are catalogued per language and per resource, which helps a lot with 50 languages.

**3. Import everything into your own database and serve it yourself.**
- Load the text, translations, and segments into your own DB or bundle them as SQLite in the app.
- This gives you offline reading, predictable latency, and no per-request dependency.
- Only stream the audio files from a CDN.
- Keep the upstream API for refreshing data.

## Language coverage (~50 languages)

- The Quran.com translation catalogue covers roughly 40 to 50 languages and often several translators per language. Hitting exactly your 50 is plausible but not guaranteed. Get the full list from the translations endpoint and diff it against your target languages **before** you commit.
- Tanzil and AlQuran.cloud are useful for filling gaps, but check each translation's licence.
- Pick **one default translator per language** and make the rest optional. Translator choice matters more to users than language count.
- Right-to-left languages other than Arabic (Urdu, Persian, Hebrew, and others) need real RTL testing.
- Some languages have thin or dated translations. Show the translator name and year in the UI.

## Trade-offs

**Live API vs. bundled data**
- Live API: fastest to start, always current. You depend on availability and rate limits, and auth requirements may change. It also breaks offline.
- Bundled or self-hosted: more setup work, and you own updates. It is faster, works offline, and is much more robust. **This is my recommendation for production.**

**Quran.com audio vs. EveryAyah**
- Quran.com has word timings and a smaller reciter set.
- EveryAyah has many reciters at verse level and is simple and reliable, but has no word timing.
- Option: offer word highlighting for reciters that have segments, and verse-level highlighting for the rest.

**Timing accuracy**
- Segment data is usually good but not perfect, especially where reciters elongate or repeat.
- Test on a few surahs with slow *tartīl* and fast *ḥadr* recitation.
- Consider a tolerance or lookahead of about 50 to 100 ms so highlights don't lag.

**Licences**
- Text, translations, audio, and fonts each have their own licence. Many translations are free for non-commercial use only, and some require attribution.
- Audio reciters' rights vary.
- Get this right early, especially if the app is monetised or ad-supported.
- Quran Foundation's terms are the first thing to read.

**Text integrity**
- Use an established, verified text (Uthmani Hafs from King Fahd Complex lineage) and never edit it.
- Scholars and users will notice errors, so version and checksum the text you ship.

## Suggested architecture

1. Download the QUL/Quran.com snapshot: text, word-by-word, the translations you selected, and audio segments for the reciters you chose.
2. Normalise into your schema: `verses`, `words`, `translations(verse_id, lang, translator_id, text)`, `reciters`, `audio_segments(reciter_id, verse_id, word_pos, start_ms, end_ms)`.
3. Serve audio from the Quran.com/QDC CDN at first. Move to your own CDN if you need reliability or offline downloads.
4. On the client, drive highlighting from `audio.currentTime` and binary-search the segments for the current verse.
5. Run a scheduled job (monthly) to check upstream for corrections.

## What to do first

1. Fetch the Quran.com translations list and map it against your 50 target languages.
2. Prototype word highlighting for one reciter and one surah to validate the segment quality.
3. Read the licences for text, translations, and audio.
4. Then decide between live API and bundled data. I'd bundle.


### FINAL MESSAGE
I wrote the recommendation to `/tmp/eval7-baseline-zqjoqrtf/answer.md`. I assumed the app is for the Quran, since you mention recitation and word highlighting. I wrote it from memory and didn't check live docs, so confirm API auth, rate limits, and licences before you commit.

- **Main source:** Quran Foundation's Quran.com API v4 for the Arabic text, translations, and audio. It's the only source I know of that returns word-level timing (`segments`, as `[word, start_ms, end_ms]`).
- **Bulk data:** Quranic Universal Library (QUL) for downloadable text, translation, word-by-word, and timing datasets. I'd import these into your own database or a bundled SQLite file instead of depending on the live API.
- **Fallbacks:** EveryAyah gives verse-level audio for many more reciters, but it has no word timing. Tanzil and AlQuran.cloud can fill translation gaps.
- **Trade-offs:**
  - **Language coverage:** the Quran.com catalogue is roughly 40 to 50 languages, so hitting all 50 isn't guaranteed. Compare its translations list to your target languages first.
  - **Timing accuracy:** segment timing can be imperfect on elongated or repeated recitation.
  - **Licences:** text, translations, audio, and fonts are licensed separately, and many translations are non-commercial only.
  - **Highlighting:** word highlighting would work only for reciters that have timing data. The others would fall back to verse-level highlighting.

The file ends with a suggested schema and four first steps. The first is to diff the translations list against your 50 languages, and the second is to prototype word highlighting for one reciter and one surah.