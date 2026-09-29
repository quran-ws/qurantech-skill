### FILE answer.md
# Data sources for a 50-language reading app with word-highlighted recitation

Assumptions: the app reads **Hafs**, the most common case, and ships on mobile and/or web. If you need another riwayah, see "If you need another riwayah" below. Counts come from the QuranTech skill catalog (checked 2026-09-29). Re-check them against the live catalogs before you commit.

## Recommendation

| Need | Use | Why |
|---|---|---|
| Arabic text and word IDs | **quran-text** (`@quran.ws/text`, or the SQLite/JSON files) | Source-verified against KFGQPC. It numbers every word, and that number is the join key for audio timings. It works offline and needs no API key. |
| Translations, about 50 languages | **Quran Foundation API v4** as the live source, plus **QUL** downloads as the offline and fallback copy | Quran Foundation covers 60+ languages (126 translations in 69 languages when checked) and receives corrections. QUL has 204 translations as downloads with no API dependency. Seed the app from QUL and refresh from the API. |
| Recitation audio with word timestamps | **Quran Foundation Audio API** (`[word_index, start_ms, end_ms]` segments) and **QUL** (about 58 segmented audio sets) | These are the only sources in the catalog with word-level timing. Use the same `surah:ayah:word` key for both. |
| Word highlighting on the page | **Web:** `quran-svg-elements` (Hafs only, beta) or plain text spans. **Native:** `quran-engine` (beta) | Both address words by `surah:ayah:word`, so a timing row maps straight to a highlight call. |
| More reciters, no highlighting | **MP3Quran** (whole surahs, ayah timings at `/ayat_timing`) and **EveryAyah** (per-ayah files) | Wide reciter coverage. Ayah-level highlighting only. |

The Quran.ws blocks ship no translations or audio. They give you the keys that attach translations and audio to the text.

## Translations

**Language coverage**
- Quran Foundation: 126 translations in 69 languages.
- QuranEnc: 56 languages (75 translations), listed at `quranenc.com/api/v1/translations/list`.
- Tanzil: 43 language codes.
- QUL: 204 translations.
- Fawaz Ahmed: 90+ languages, 440+ translations.

Pick your 50 languages first, then check the catalogs. Quran Foundation and QUL will cover most of them. Use QuranEnc to fill gaps, because its translations are reviewed.

**Trade-offs**
- **Quran Foundation API:** current, and one integration covers most languages. It needs a Developer Console app (OAuth2 client credentials). Don't ship the secret in a client app: proxy through your backend, or cache server-side. You also depend on its terms and uptime.
- **QUL downloads:** works offline, and you control the versions. There is no API, so updates are manual. **Licences differ per resource**, so audit each translation you bundle.
- **Tanzil:** verified, but **non-commercial use only**, and it requires a backlink if you use more than three translations. Skip it for a commercial app.
- **Fawaz Ahmed:** the widest coverage. The Unlicense covers the repo, not each translation's copyright. Treat it as a discovery source, not a clean-licence source.

**Rules to build in**
- Keep a per-translation licence and attribution table. Some translations need publisher permission.
- Label them "translation of meanings" and never show one without the Arabic. Let users choose among several translations per language.
- Set text direction per translation, since Urdu, Persian and others are RTL.
- Default to the device language.
- Key stored translations to `surah:ayah` plus the counting system.

## Audio with word highlighting

1. **Choose reciters that have word segments.** Word-level timing exists only for some reciters and riwayat. Build the reciter list from what the timing data covers, and don't promise highlighting for every reciter.
2. **Join on the word key.** Word keys in `quran-svg-elements` use `surah:ayah:word` (1-based within the ayah), the same shape as the audio segments. Never join on strings. `quran-svg-elements` has 77,432 words and `quran-text` has 77,434, so **spot-check word boundaries**.
3. **Highlight in the player.** Preprocess segments into a sorted array and binary-search on `currentTime`. Handle pauses between words and elongations.
4. **Model the recitation separately from the reciter.** A recitation is one recording set of a reciter in a specific riwayah. Timings and availability belong to the recitation.
5. **Adab:** always show the reciter's name. Never auto-play without user action. Start audio only at ayah boundaries. Never ship machine-split ayah audio without human review.
6. **Offline:** let users download by surah or juz, with resume and per-reciter deletion. Size the downloads from the files you ship.

**Trade-offs**
- Quran Foundation segments depend on the API and its terms. QUL sets are downloadable, so you can host them yourself, but check each set's licence.
- Word highlighting on the printed mushaf (`quran-svg-elements`) is Hafs-only and beta. Pin the CDN version (`cdn.quran.ws/svg/elements/<version>/`).
- If you would rather not use SVG pages, render text words yourself. Use a KFGQPC-based Quranic font, not a generic Arabic font.
- Forced alignment (WhisperX, `quran-align`) can generate timings for reciters that lack them. It needs clean studio audio and human review. Treat it as a last resort.

## Architecture

- **Bundle** `quran-text` and one default translation. Download other translations and audio on demand.
- **Backend proxy** for Quran Foundation, with a cache and version pinning. If you need offline delta sync, **QuranPedia** offers `/v1/changes` and bulk dumps, but its translation library is smaller (about 142 books).
- **Data model:** every ayah reference is `{surah, ayah, counting}`. Never hardcode ayah counts (they range from 6,204 to 6,236 across counting systems).
- **CI:** check that the Arabic text matches the verified source byte for byte. Log `surah:ayah` references, never Quranic text.
- **Accessibility:** support screen readers and dynamic type. Most Quran apps skip this.

## If you need another riwayah

Translations, tafsir and most audio are indexed by the Hafs count. For Warsh and others, convert with `qiraat-ayah-map` (or `quran-text`'s `ayah-map.json`). A split or merged ayah becomes a range, so show every Hafs ayah in it. Play audio only over text of the same riwayah. `quran-svg-elements` word highlighting is Hafs-only, so use `quran-text` words with your own rendering instead.

## Open items to verify before you build

- Licence terms for every translation and audio set you ship. The catalog marks most as "verify".
- Whether Quran Foundation's terms permit your usage (caching, redistribution, commercial use).
- Which of your 50 languages have a translation with acceptable quality and licence.
- Which reciters have word-level segments in both Quran Foundation and QUL.
- Maturity: `quran-text`, `quran-svg-elements` and `quran-engine` are Beta, so pin versions.


### FINAL MESSAGE
I wrote the recommendation to `/tmp/eval7-with_skill-gg2pth_l/answer.md`. I assumed you're reading Hafs. All counts come from the QuranTech skill's catalog, checked 2026-09-29, and I didn't re-check them against the live services.

- **Arabic text and word IDs:** `quran-text`. It numbers every word, and that number is what ties audio timings to the text.
- **Translations (about 50 languages):**
  - Use the Quran Foundation API v4 as the live source. It covers 60+ languages and needs OAuth credentials, so call it through your backend.
  - Use QUL downloads (204 translations) as the offline copy and fallback. Their licences vary per resource.
  - Use QuranEnc to fill any gaps.
  - Avoid Tanzil for a commercial app, because it is non-commercial only.
- **Audio with word highlighting:** The Quran Foundation Audio API and QUL are the only sources in the catalog with word-level timestamps. Join them to the text on the `surah:ayah:word` key. Use MP3Quran and EveryAyah for extra reciters, but only with ayah-level highlighting.
- **Display:** On the web, use `quran-svg-elements`, which is Hafs-only and beta. On native, use `quran-engine`. Pin versions for both.

The file also covers the trade-offs, the adab rules and the offline design. It also says how to handle other riwayat and lists what to verify before you build. The main open items are per-translation licences, whether Quran Foundation's terms allow your usage, and which reciters have word segments in both sources.