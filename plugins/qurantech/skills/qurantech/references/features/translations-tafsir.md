# Translations & Tafsir

## Table of Contents
- [Joining to a Riwayah](#joining-to-a-riwayah)
- [Translations](#translations)
- [Tafsir](#tafsir)
- [Copyright & Legal](#copyright--legal)
- [AI-Generated Translations & Tafsir](#ai-generated-translations--tafsir)
- [Best Practices](#best-practices)

## Joining to a Riwayah

The blocks carry no translation or tafsir text; they carry the keys to attach it correctly ([blocks.md](../blocks.md)).

- Most translation and tafsir sources are indexed in the Hafs (Kufi) count. If the reader uses Warsh or another riwayah, a conversion is required: an ayah number does not mean the same ayah across counts. Use `qiraat-ayah-map` (any of the six counting systems) or `quran-text` `data/ayah-map.json` (Hafs reference to each bundled edition) and follow its `relation` (`same`, `merged`, `split`, `shifted`, `unnumbered`).
- On a split or merge the result is a range: show every Hafs ayah in it (`hafs_ayahs`), never only the first.
- Key stored content to `quran-text` ayah keys plus the counting system, and convert on display (see [qiraat.md](../concepts/qiraat.md)). Do not normalise by round trip; the reverse direction is lossy at splits.
- **kfgqpc-resources** mirrors the King Fahd Complex's translation and tafsir books unmodified, with checksums (see the group listing in its README, `quran-ws.github.io/kfgqpc-resources/`). It is a mirror, not the official site: point users to the Complex as the authority. All rights remain with the Complex.

## Translations

### Sources

| Source | Languages | Model | Notes |
|--------|-----------|-------|-------|
| **Quran Foundation API** | 60+ languages (126 translations in 69 languages when checked 2026-09-29) | API (kept current by the provider) | Needs a Developer Console app (client credentials); check the live catalog for counts |
| **Tanzil.net** | 40+ (43 language codes, 114 files) | Static download | Verified, widely used. Non-commercial use only; a backlink is required if you use more than three translations |
| **QUL (Tarteel)** | Multiple | Download | Curated translations as downloadable data, not an API |
| **QuranEnc** | 56 languages (75 translations) | Download/API | Verified translations; list at `quranenc.com/api/v1/translations/list` |
| **Fawaz Ahmed quran-api** | 90+ languages, 440+ translations | GitHub repo | Open dataset. The Unlicense covers the repo, not each translation's copyright |

### Key Considerations

- **Translations are human-authored and may contain errors.** They are not the Quran — they are scholarly interpretations in other languages.
- **Prefer API-driven sources** for translations so users get corrections. Content APIs such as Quran Foundation need client credentials, so plan for key handling and an offline fallback.
- **Multiple translations per language are common.** Let users choose.
- **Translation quality varies significantly.** Some are literal, some are interpretive. Provide context about each translation's approach if possible.
- **Some translations are copyrighted.** Verify licensing before including any translation.

### Display Patterns

- **Side-by-side:** Arabic text on the right, translation on the left. Most common layout.
- **Inline:** Translation below each ayah. Good for reading flow.
- **Comparison:** Multiple translations shown together per ayah. Useful for study.
- **Always visually distinguish** translation text from Quranic Arabic text (different font, different color/style, labeled).

## Tafsir

### Sources

| Source | Content | Notes |
|--------|---------|-------|
| **Quran Foundation API** | 20 tafsirs (2026-09-29) | Client credentials required; check the live catalog for the current list |
| **QUL (Tarteel)** | Curated tafsirs | Download, not an API: `qul.tarteel.ai/resources/tafsir` |
| **Spa5k tafsir API** | 123 tafsirs | Open, MIT, active. `github.com/spa5k/tafsir_api` — self-hostable |
| **Quran Tafseer API** | Multiple editions | `api.quran-tafseer.com/en/docs/`. Works over http only; https failed when checked, so avoid it in browsers on https pages |

### Common Tafsirs

Popular tafsirs that users expect, with where each was found (2026-09-29; verify against the live catalog):
- **Tafsir Ibn Kathir** — classical, widely trusted (Quran Foundation, Spa5k)
- **Tafsir al-Tabari** — comprehensive classical tafsir (Quran Foundation, Spa5k)
- **Tafsir al-Sa'di** — accessible modern Arabic tafsir (Quran Foundation, Spa5k)
- **Al-Jalalayn** — concise, popular for quick reference (Spa5k; absent from Quran Foundation)
- **Fi Zilal al-Quran** (Sayyid Qutb) — literary/thematic approach (Quran Foundation, Urdu edition only; not found on Spa5k)

### Display Patterns

- **Expandable panel:** Tap an ayah to see its tafsir. Keeps the reading view clean.
- **Dedicated tafsir view:** Full-screen tafsir with the ayah shown at the top.
- **Multiple tafsirs:** Let users switch between tafsir sources.
- **Tafsir text is often very long.** Support scrolling, collapsible sections, or pagination within a tafsir entry.

## Copyright & Legal

- **Always verify copyright** before including any translation or tafsir.
- **Some translations are freely distributable**, others require written publisher permission.
- **Seek explicit approval** from the copyright holder or publisher, especially for tafsir works.
- **Attribute the author/translator** — this is both an ethical and legal requirement.
- **Digitized tafsirs may contain OCR errors.** Plan for corrections and periodic updates.

## AI-Generated Translations & Tafsir

**Never let AI generate tafsir freely.** Use RAG (Retrieval-Augmented Generation) with authoritative tafsir sources.

Without asbab al-nuzul and the surrounding ayahs, a model can misread an ayah. Hypothetical example: Al-Ma'un 107:4 ("woe to those who pray") is qualified by verse 5; a model given only verse 4 could get the meaning wrong. Retrieve the neighbouring ayahs and cite the tafsir.

**Guidelines:**
- Use RAG with verified tafsir databases as the knowledge source
- Always show the source tafsir the AI's answer is based on
- Human review is mandatory before publishing any AI-generated Islamic content
- Label AI-generated content clearly — never attribute it to a scholar
- Pre-process and cache AI results rather than generating on-the-fly

## Best Practices

- **Always label translations as "ترجمة معاني" (Translation of meanings)**, not as "Quran" or "translation of the Quran." This is an important Islamic scholarly distinction.
- **Never display a translation without the Arabic original** visible or easily accessible.
- **Translations should be synced to the correct ayah numbering system** for the active mushaf/qira'a.
- **Default translation** should match the user's device language if available.
- **Keep translations updated** via an API or a versioned download rather than bundling static files that go stale.
- **Tafsir and translation are different things.** Don't merge them in the UI — users expect them as separate features.
- **RTL considerations:** Some translations are in RTL languages (Urdu, Farsi) and some in LTR (English, French). Handle mixed directionality correctly.
