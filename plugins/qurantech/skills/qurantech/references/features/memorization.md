# Memorization (Hifz) Tools

## Table of Contents
- [Overview](#overview)
- [Composing a Hifz App from Blocks](#composing-a-hifz-app-from-blocks)
- [The Traditional Hifz Method](#the-traditional-hifz-method)
- [Core Features](#core-features)
- [Spaced Repetition](#spaced-repetition)
- [Mutashabihat (Similar Verses)](#mutashabihat-similar-verses)
- [Recitation Checking](#recitation-checking)
- [Data Model](#data-model)
- [Best Practices](#best-practices)

## Overview

Memorization (hifz) is one of the most-requested Quran app categories. Effective hifz apps digitize a method that has worked for 14 centuries rather than inventing new pedagogy. Understand the traditional method first, then map features onto it.

## Composing a Hifz App from Blocks

Build the hifz surface from the Quran.ws blocks ([blocks.md](../blocks.md)); third-party sources below are complements.

| Hifz need | Block |
|---|---|
| Ayah text, page and line layers | `quran-text`: `page_starts` and `line_starts` give pages and lines in the active riwayah's own layout |
| Word-level hide/reveal and tap-to-check | `quran-svg-elements` (word keys `surah:ayah:word`, Hafs only) with `quran-engine` (`mask`, `highlight`, `hitTest`, word keys; native rendering) |
| Annotated review (tajweed colouring on the review text) | `quran-tajweed`, applied only to the edition it was measured on; a study aid, not a judgment |
| Page-based progress | `quran-svg`: the printed page per riwayah, with tappable ayah polygons to mark ranges |
| Per-riwayah progress | `qiraat-ayah-map`: store `{surah, ayah, counting}` so progress survives a riwayah switch |

Hide words with masks or overlays on the page, never by editing the text. Store mistakes by word key.

## The Traditional Hifz Method

A three-tier daily routine is common in South Asian-style hifz programmes ([thehifzproject.com/articles/sabaq-sabqi-manzil](https://thehifzproject.com/articles/sabaq-sabqi-manzil)). *Sabaq* and *sabqi* are Urdu/Persian loanwords. Windows and amounts vary by school and student; the table is illustrative, so let a teacher review the defaults:

| Tier | Arabic | What It Is | Typical Daily Amount |
|------|--------|-----------|---------------------|
| **New lesson** | سبق (sabaq) | Verses being memorized today | ¼–1 page |
| **Recent revision** | سبقي (sabqi) | Recently memorized material, still fragile (window varies) | Last few pages |
| **Old revision** | منزل (manzil / muraja'ah) | Consolidated portions, reviewed on rotation | ½–1 juz |

**Key implications:**
- The **page** (of the 604-page Madinah mushaf) is the standard unit of memorization progress, not the ayah. Most huffaz think in pages and juz.
- New memorization without structured revision fails. An app that only tracks "memorized surahs" without a revision queue misses the hard part.
- Recently memorized material needs far more frequent review than old material, which a tiered schedule already encodes.

## Core Features

### Hide/reveal modes
- **Full mask:** Hide the ayah entirely; user recites from memory, then taps to reveal.
- **Progressive reveal:** Reveal word by word as the user recites (pairs well with verse recognition — see below).
- **First-word hint:** Show only the first word of each ayah as a prompt.
- **Mistake marking:** Let the user (or teacher) tap a word to mark a mistake; store it word-level for later drilling.

### Repeat loops (audio)
- Repeat a single ayah N times, then auto-advance (classic memorization drill: 3–10× per ayah).
- Loop a range (ayah 1–5 of a page) with configurable repetitions per ayah and per range.
- Adjustable playback speed. Gapless transitions matter — a pause between repeats breaks the drill rhythm.
- See [audio.md](audio.md) for ayah-level audio sources and playback patterns.

### Testing modes
- **Continue from here:** Show/play an ayah, user continues reciting the next ones.
- **Random spot check:** Random ayah from the user's memorized range — the standard oral exam format.
- **Page connections:** Prompt with the last ayah of a page, user recites the first ayah of the next page. Page transitions are a notorious weak point.
- **Where is this from?** Show an ayah, user identifies surah/juz — useful for advanced review.

### Progress & motivation
- Track by page and juz (primary), with surah view as secondary.
- Distinguish statuses: not started / in progress / memorized / needs review (see [data-models.md](../concepts/data-models.md)).
- Streaks and daily goals work, but keep them humble in tone — this is worship, not a game. Avoid leaderboards ranking users by "Quran memorized."

## Spaced Repetition

One approach, with tunable defaults (none of these numbers is sourced). The traditional tiers are already a fixed-rotation schedule; add SM-2/FSRS-style scheduling only if you need adaptivity:

- **The item is a page or ayah-range, not a flashcard.** Reviewing a page takes minutes, so the daily queue must respect a time budget (e.g., cap the queue at a set number of minutes of reciting), not just card counts.
- **Seed intervals from the sabaq/sabqi/manzil structure:** new material reviews daily for a week or more before intervals stretch; consolidated material can go weeks.
- **Grade by mistake count** from the review session (0 mistakes = easy, 1–2 = good, 3+ = again) instead of asking users to self-rate.
- **Never let intervals grow unbounded.** Even solid huffaz revise the whole Quran on a fixed rotation (e.g., a juz per day). Cap the maximum interval at a value you tune.
- Word-level mistake history should raise the review frequency of the specific pages containing chronic mistake words.

## Mutashabihat (Similar Verses)

Nearly-identical verses in different surahs are a common source of memorization errors (e.g., similar endings like غفور رحيم vs عزيز حكيم; a refrain repeated within one surah, such as the آلاء refrain in Surah Ar-Rahman, is a different case: it confuses position within the surah).

- **QUL** provides ~5,277 mutashabihat entries and ~4,001 similar ayahs (records are per ayah); scholar review of the curation is unverified: use this data rather than computing similarity yourself.
- Show a "similar verses" warning on ayahs with known confusions, with a side-by-side diff highlighting the differing words.
- Build a dedicated drill mode: present the shared stem, user picks/recites the correct continuation for the current surah.
- When a recitation-checking feature detects the user drifting into the *other* similar verse, name the other passage explicitly (surah and ayah of the similar verse it drifted into); that is more useful than "wrong word."

## Recitation Checking

Two levels of automated checking:

1. **Verse identification** — confirm the user recited the intended ayah(s). Use Tilawa, formerly offline-tarteel (see [verse-recognition.md](verse-recognition.md)); it returns `{surah, ayah, ayah_end, score}` fully offline.
2. **Word-level following** — track position word by word for progressive reveal and mistake detection. Requires ASR (tarteel-ai/whisper-base-ar-quran) plus alignment; see [audio.md](audio.md). Expect errors on tajweed-heavy passages — surface low-confidence results as "check this word" rather than asserting a mistake.

**Do not claim tajweed evaluation** unless you genuinely implement it — current open ASR models cannot reliably judge tajweed correctness (see the warning in [audio.md](audio.md)). A false "your recitation is correct" is worse than no feedback. For serious hifz, position the app as a supplement to a teacher, not a replacement.

## Data Model

See [data-models.md](../concepts/data-models.md) for the `Memorization Progress` entity. Extend it with:

| Field | Type | Description |
|-------|------|-------------|
| unit | enum | page / ayah_range / surah |
| ease / stability | float | Spaced-repetition scheduling state |
| next_review | datetime | When this unit is due |
| mistake_words | array | [{surah, ayah, word_position, count, last_at}] |
| tier | enum | sabaq / sabqi / manzil |

As always, include `mushaf_id` — page numbers and ayah boundaries are mushaf-specific.

## Best Practices

- **Default to the 604-page Madinah layout** for page-based tracking, but derive page boundaries from the active mushaf's metadata (Warsh mushafs paginate differently).
- **Review queue over library.** The home screen of a hifz app should answer "what do I review right now?", not show a surah list.
- **Offline is non-negotiable.** Memorization sessions happen in mosques and classrooms without connectivity. All drill modes and queues must work offline.
- **Support teacher/student workflows.** Many users memorize under a teacher: shared progress visibility, teacher-marked mistakes, and assignment of the next sabaq are high-value features.
- **Respect the adab rules** ([adab.md](../concepts/adab.md)): masked/hidden text must never be rendered truncated mid-ayah when revealed, and test prompts must show complete ayahs.
- **Khatma tracking** (completing the full Quran in recitation) is a related but distinct feature — reading progress, not memorization state. Keep the two separate in the data model.
