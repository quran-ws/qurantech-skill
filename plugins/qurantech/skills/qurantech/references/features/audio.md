# Audio Recitations

## Table of Contents
- [How Audio Joins the Blocks](#how-audio-joins-the-blocks)
- [Model Rawi, Reciter, and Recitation Separately](#model-rawi-reciter-and-recitation-separately)
- [Filling Per-Ayah Audio Gaps](#filling-per-ayah-audio-gaps)
- [Playback Modes](#playback-modes)
- [Word-Level Highlighting](#word-level-highlighting)
- [Offline Audio](#offline-audio)
- [Audio Alignment & Timestamp Tools](#audio-alignment--timestamp-tools)
- [Verse Recognition (Audio-to-Ayah Identification)](#verse-recognition-audio-to-ayah-identification)
- [ASR for Recitation Evaluation](#asr-for-recitation-evaluation)
- [Best Practices](#best-practices)

## How Audio Joins the Blocks

The Quran.ws blocks ([blocks.md](../blocks.md)) do not ship audio; take recordings and timings from the sources below. The blocks supply the keys and the display that audio attaches to:

- **Word keys for highlighting.** `quran-text` numbers every word (the same number in every riwayah) and exposes `m.word(surah, ayah, index)`. `quran-svg-elements` keys each word `surah:ayah:word` (1-based within the ayah), the same key as audio timing word numbers. Join timings to the page on that key, never on strings. Elements has 77,432 words and quran-text 77,434, so spot-check word boundaries. Elements is Hafs only.
- **Ayah keys across counting systems.** A riwayah's ayah keys may not match a recording set indexed by Hafs. Use `qiraat-ayah-map` to pair them, and treat split or merged ayahs as ranges. Store `{surah, ayah, counting}` with each recording.
- **Riwayah-specific pairing.** Play a recording only over the text (`quran-text`), font and page set (`quran-svg`) of the same riwayah. See [qiraat.md](../concepts/qiraat.md).
- **Native rendering.** For word highlighting on phones use `quran-engine` (`highlight`, `hitTest`, word keys) instead of SVG.

## Model Rawi, Reciter, and Recitation Separately

A common data-modeling conflation: **rawi** = the transmission (defines the *text*), **reciter** = the person, **recitation** = one recording set of a reciter in a specific rawi (murattal vs mujawwad, different bitrates). Audio files, timings, and availability belong to the *recitation*. See [data-models.md](../concepts/data-models.md).

## Filling Per-Ayah Audio Gaps

Many reciters exist only as full-surah recordings. To offer ayah-level playback for them, split with ffmpeg using published ayah timings where available, or a duration-based heuristic otherwise — and put a **human review step** (listen, approve, re-slice a boundary) before publishing. Never ship machine-split ayah audio unreviewed: a cut mid-word violates the adab of recitation.

## Playback Modes

Design for these common user needs:

### Verse-by-verse
- Play one ayah, pause, wait for user action (or auto-advance).
- Support repeat count per ayah (common for memorization: play 3x, then move to next).
- Show active ayah highlighted in text.

### Continuous
- Play through a range (page, surah, juz) without stopping.
- Use timestamp data to highlight the current ayah as audio progresses.
- Support background playback with lock-screen controls (mobile).

### Word-by-word
- Highlight each word as it's recited.
- Requires word-level timestamp data (Quran Foundation segments endpoint).
- Essential for learning pronunciation and tajweed.

### Repeat/Loop
- Repeat a single ayah N times.
- Repeat a range of ayahs (e.g., ayah 1-5, loop).
- Adjustable speed if the audio engine supports it.

## Word-Level Highlighting

**Data requirement:** Word-level timestamps mapping each word (by `surah:ayah:word` key) to its start/end time in the audio file.

**Sources for timestamps:**
- Quran Foundation Audio API segments (`[word_index, start_ms, end_ms]`), for reciters that provide them
- QuranPedia timing files ([quranpedia-api.md](../sources/quranpedia-api.md))
- Your own alignment (tools below)

**Implementation pattern:**
1. Load timestamp data for the selected reciter + surah.
2. During playback, track `currentTime` against timestamp ranges.
3. Apply a highlight to the word whose time range contains `currentTime`: a class on `g.word` (`quran-svg-elements`) or `highlight` in `quran-engine`.
4. Handle edge cases: pauses between words, tajweed elongations, idgham (merging).

**Performance:** Pre-process timestamps into a sorted array for binary search lookup rather than linear scanning on every time update.

## Offline Audio

- **Download strategy:** Let users download by surah, juz, or full mushaf.
- **Storage estimates:** measure per reciter and bitrate from the file sizes you ship; do not quote a fixed figure.
- **Show download progress** and allow partial downloads (resume-capable).
- **Store metadata** about what's downloaded so the app knows when to stream vs. play locally.
- **Cache management:** Provide a way to delete downloaded audio per reciter/surah.

## Audio Alignment & Timestamp Tools

For generating timestamps from audio recordings:

| Tool | Method | Level |
|------|--------|-------|
| **quran-align** | Forced alignment | Word-level (last pushed 2017). `github.com/cpfair/quran-align` |
| **whisper-timestamped** | Whisper + confidence | Word-level. `github.com/linto-ai/whisper-timestamped` |
| **WhisperX** | Whisper + wav2vec 2.0 | Word-level (precise). `github.com/m-bain/whisperX` |
| **Aeneas** | Text-audio sync | Segment-level. Python/C. AGPL v3. `github.com/readbeyond/aeneas` |
| **quran_timing_files** | Pre-computed | Ready-to-use. `github.com/anassaiyed/quran_timing_files` |

**Note:** 16 kHz mono WAV is the typical ASR input, not universal; check the model's requirements. Use `pydub` + `ffmpeg` for conversion.

## Verse Recognition (Audio-to-Ayah Identification)

For identifying which surah/ayah is being recited from audio (not just transcription), see **[verse-recognition.md](verse-recognition.md)**. It covers Tilawa (formerly offline-tarteel) with its current engines, sizes and licences (the default Zipformer model is non-commercial, NPL-1.2).

## ASR for Recitation Evaluation

| Model | Notes |
|-------|-------|
| **tarteel-ai/whisper-base-ar-quran** | Whisper fine-tuned on Quran recitation |
| **wav2vec2-base-word-by-word-quran-asr** | Word-by-word Quran ASR |

**Warning:** low WER on clean benchmarks (the tarteel-ai model card reports 5.75 WER) does not mean tajweed competence. Standard ASR treats Arabic like any language — it misses the difference between "correct pronunciation" and "tajweed-compliant recitation," and errors concentrate exactly where tajweed matters (idgham, ghunnah, madd). A Quran-specific evaluation metric accounting for tajweed rules is still needed; never present ASR output as a tajweed judgment.

**Evaluation tools:**
- **check-telawa** (`github.com/engsaleh/check-telawa`) — Flask + Whisper + jiwer for WER calculation
- **WER (Word Error Rate)** — standard but insufficient for Quran
- **PER (Phoneme Error Rate)** — better for tajweed analysis at makhraj level

## Best Practices

- **Reciter attribution is mandatory.** Always show the reciter name when playing audio.
- **Never auto-play** without explicit user action.
- **Pre-buffer the next ayah** during playback for gapless transitions.
- **Handle missing audio gracefully.** Not all reciters have complete recordings. Show which surahs/ayahs are available.
- **Support multiple reciters.** Users have strong preferences — offer a reciter selection UI.
- **Audio should start at ayah boundaries**, never mid-ayah.
- **Background audio** must work on mobile (lock screen, notification controls).
- **Respect the user's qira'a selection.** A Warsh reciter should not be offered when the user is reading the Hafs mushaf (unless explicitly browsing reciters).
- **Noisy recordings cause poor alignment.** Alignment tools work best on clean, studio-quality audio.
- **Separate reading and listening architectures.** Community experience shows audio streaming apps differ fundamentally from page-based mushaf display — consider separate modules or even separate apps.
