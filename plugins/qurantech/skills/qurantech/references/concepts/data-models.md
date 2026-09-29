# Quran Data Models & Taxonomy

## Table of Contents
- [Core Entities](#core-entities)
- [Structural Divisions](#structural-divisions)
- [Text Entities](#text-entities)
- [Audio Entities](#audio-entities)
- [User Entities](#user-entities)
- [Relationships](#relationships)
- [Schema Design Principles](#schema-design-principles)

## Core Entities

### Block-first: the shape to copy
Align with quran-text: **a mushaf is an ordered `words[]` array; everything else is a layer of positions into it** (`surah_starts`, `ayah_starts`, `page_starts`, `line_starts`, `juz_starts`, `marks`). Unit *k* of a layer is `words[starts[k] : starts[k+1]]`. Positions are file-local; only the **shared word number** (same word, same number in all seven riwayat) crosses mushafs. Counting comes from qiraat-ayah-map (ids `kufi`, `madani-first`, `madani-last`, `makki`, `basri`, `dimashqi`). See [blocks.md](../blocks.md) and skills `quran-text`, `qiraat-ayah-map`.

### Mushaf
A specific edition, tied to a riwayah and a counting system.

| Field | Type | Description |
|-------|------|-------------|
| key | string | Mushaf key, e.g. `hafs`, `warsh` (quran-text keys) |
| name | string | Display name |
| qiraah | string | The qari the mushaf follows |
| riwayah | string | Key such as `hafs`, `warsh`. `rawi` is the older name for the same concept; use `riwayah` |
| counting_system | string | A system **id** (`kufi`, `madani-last`, ...), never a school label or a total |
| counting_system_printed | string / null | What this printed edition measures onto |
| counting_system_associated_with_qari | string | What the qari is attributed. Store both, or a pointer to the qiraat-ayah-map / quran-text record; never derive one from the other |
| edition | object | Edition record (see below) |
| language | string | Primary script language |

Do not store `total_ayahs` or `total_pages` as fixed values: derive them from the loaded data (`words[]`, `ayah_starts`, `page_starts`). Page counts are edition-specific: 604 is the Madinah print's figure and this repo has no source that makes it universal.

**Edition record** (an idea, following the Quran.ws docs guidelines, whose status is "Proposed", not adopted): `edition`, `riwayah`, `counting_system`, `version`, and `source_hash` (SHA-256 of the source file). quran-text records SHA-256 digests for its sources and quran-tajweed's `edition.sha256` works the same way. This lets you prove which text a stored offset, span or timing was measured against.

### Surah (Chapter)
| Field | Type | Description |
|-------|------|-------------|
| number | integer | 1-114 |
| name_arabic | string | Arabic name |
| name_transliterated | string | Latin transliteration |
| name_translation | string | Translated name |
| revelation_type | enum | makki / madani (quran-text: `revelation`) |
| ayah_count | integer | Per mushaf/counting system; read it from the edition |
| revelation_order | integer | Order of revelation |
| has_basmalah | boolean | Whether the surah opens with one (false for Surah 9 only) |
| basmalah_counted | boolean | Whether the edition numbers it as an ayah. A separate fact: for al-Fatihah, Hafs, Shu'bah and Bazzi count it; the other four print it unnumbered (quran-text `counting.basmalah_counted`) |
| start_page | integer | Page in this mushaf |

### Ayah (Verse)
Keyed by **mushaf key + counting system + surah + ayah**, not bare `surah:ayah`.

| Field | Type | Description |
|-------|------|-------------|
| mushaf | string | Mushaf key |
| counting_system | string | System id of the numbering used |
| surah_number | integer | Parent surah |
| ayah_number | integer | Within the surah, in that counting system |
| word_range | [int, int] | Start/end positions into the mushaf's `words[]` (from `ayah_starts`) |
| text | string | Read from the mushaf's own `words[]`; store as received |
| text_search | string | Stripped form for search only, kept separate |
| page, juz, hizb, rub_al_hizb, manzil | integer | Division numbers; derive from the layers where the block supplies them (quran-text has page, line, juz; no others are confirmed) |
| ruku | integer | Scholar-dependent; unsourced here. Record which scheme you used |
| sajda | enum | none / recommended / obligatory. The classification is scholar-dependent and unsourced here; quran-text ships `sajdat` and states its source |
| kufi_anchor | reference | The corresponding Kufi (Hafs) ayah, for shared content. Earlier drafts call this `equals_hafs_ayah` |

`kufi_anchor` is one-directional: forward mapping (Kufi to target) can be `split` or `merged`, and the reverse is lossy at splits (Kufi 1:7 and its second half both map back to Kufi 7). For a split, store a range from qiraat-ayah-map rather than a single anchor. See [qiraat.md](qiraat.md).

## Structural Divisions

| Division | Count | Description | Use Case |
|----------|-------|-------------|----------|
| **Juz** (جزء) | 30 | Equal divisions for monthly reading | "Read one juz per day in Ramadan" |
| **Hizb** (حزب) | 60 | Half-juz divisions | Prayer portions |
| **Rub' al-Hizb** (ربع الحزب) | 240 | Quarter-hizb markers | Finer reading plans |
| **Manzil** (منزل) | 7 | Weekly reading divisions | "Complete Quran in one week" |
| **Ruku** (ركوع) | ~558 (scheme-dependent, unsourced) | Thematic passage units | Used in Hanafi prayer tradition |
| **Page** (صفحة) | 604 in the Madinah print; edition-specific | Mushaf pages | Mushaf display, page-by-page reading |

**All divisions map to specific ayah ranges.** Store the start/end ayah for each division.

## Text Entities

### Word (Kalimah)
| Field | Type | Description |
|-------|------|-------------|
| mushaf | string | Mushaf key |
| position | integer | Index into that mushaf's `words[]` (file-local) |
| word_number | integer / range | Shared word number, the cross-riwayah key. One word can cover a run (`written_joined`) and a mushaf may not read a number (`missing`) |
| text | string | The mushaf's own form, from `words[]` |
| transliteration | string | Latin transliteration |
| translation | string | Word meaning |
| root, lemma, morphology | string | Not covered by the Quran.ws blocks; take from `sources/data-sources.md` and record the source |

An `ayah:word-in-ayah` pair is a display convention (quran-svg-elements keys `surah:ayah:word`); persist the shared number when you must match across riwayat.

### Translation
| Field | Type | Description |
|-------|------|-------------|
| ayah_id | reference | Which ayah |
| language | string | ISO language code |
| author | string | Translator name |
| text | string | Translation text |
| source | string | Data source/API |

### Tafsir Entry
| Field | Type | Description |
|-------|------|-------------|
| ayah_range | range | Start–end ayah (tafsir often covers ranges) |
| tafsir_name | string | Which tafsir work |
| author | string | Scholar name |
| text | string | Tafsir content |

## Audio Entities

### Reciter, Recitation, Riwayah — three distinct entities

Model these separately (a common conflation bug):
- **Riwayah** = the transmission chain (defines the *text*: Hafs, Warsh...); `rawi` is the older name
- **Reciter** = the person/voice
- **Recitation** = one recording set of a reciter in a specific riwayah

One reciter can have multiple recitations (different riwayat, murattal vs mujawwad, different studios/bitrates). Audio, timings, and availability attach to the **recitation**, not the reciter.

### Reciter
| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique ID |
| name_arabic | string | Reciter name in Arabic |
| name_english | string | Reciter name transliterated |

### Recitation
| Field | Type | Description |
|-------|------|-------------|
| reciter_id | reference | The person |
| riwayah | string | Riwayah key this recording follows (not free text) |
| classification | enum | by_surah / by_verse |
| style | string | e.g., "murattal", "mujawwad" |
| servers | map | Base URLs per bitrate (128/64/32 kbps) |
| available_surahs | array | Not all recordings are complete |
| has_timings | boolean | Whether ayah/word timing data exists |

### Audio Segment
| Field | Type | Description |
|-------|------|-------------|
| recitation_id | reference | Which recitation (not just reciter) |
| mushaf | string | Mushaf key the timings were measured against |
| counting_system | string | System id of `ayah` |
| surah | integer | Surah number |
| ayah | integer | Ayah number in that system (null for full-surah files) |
| url | string | Audio file URL |
| duration_ms | integer | Duration in milliseconds |
| word_timestamps | array | [{word_number, start_ms, end_ms}]; use the shared word number |

## User Entities

### Bookmark
| Field | Type | Description |
|-------|------|-------------|
| mushaf | string | Mushaf key |
| counting_system | string | System id of the reference |
| surah | integer | Bookmarked surah |
| ayah | integer | Bookmarked ayah (in that system) |
| word_number | integer | Optional, for word-level bookmarks |
| label | string | User-defined label |
| created_at | datetime | When created |

### Reading Progress
| Field | Type | Description |
|-------|------|-------------|
| mushaf | string | Mushaf key |
| counting_system | string | System id of the reference |
| last_page | integer | Last viewed page (page N differs per mushaf) |
| last_surah | integer | Last surah |
| last_ayah | integer | Last ayah |
| updated_at | datetime | When last read |

### Memorization Progress
| Field | Type | Description |
|-------|------|-------------|
| mushaf | string | Mushaf key |
| counting_system | string | System id of the range |
| surah | integer | Which surah |
| ayah_from | integer | Range start |
| ayah_to | integer | Range end |
| status | enum | not_started / in_progress / memorized / review |
| last_reviewed | datetime | Last review date |
| confidence | float | Self-assessed confidence (0–1) |

## Relationships

```
Mushaf ─── has ──→ words[] (layers of positions)
Mushaf ─── has many ──→ Surah
Surah  ─── has many ──→ Ayah
Ayah   ─── has many ──→ Word
Ayah   ─── has many ──→ Translation
Ayah   ─── belongs to ──→ Juz, Hizb, Rub, Manzil, Ruku, Page
Reciter ─── has many ──→ Audio Segment
Audio Segment ─── linked to ──→ Ayah
```

## Schema Design Principles

- **Carry mushaf key and counting system in every reference.** `(surah:2, ayah:5)` is ambiguous; `(mushaf: warsh, counting: madani-last, surah:2, ayah:5)` is not.
- **Derive totals** (ayahs, pages, words) from the loaded mushaf; never store fixed examples.
- **Address words by shared number** when data crosses riwayat; positions are file-local.
- **Layers over unchanged text.** Tajweed spans, highlights and timings are positions or numbers measured against one edition; store the edition record beside them.
- **Normalize sparingly for Quranic text.** Quranic text should be stored exactly as received from the source — never transform or normalize the Uthmani text itself.
- **Store simplified text separately** for search purposes (stripped diacritics, normalized alef/hamza).
- **Translations and tafsir reference ayah ranges**, not just single ayahs — a tafsir entry often covers multiple consecutive ayahs.
- **Ranges are the norm for scholarly attachments generally.** In production datasets, most topic-to-ayah links are ranges, not single verses. Use `(ayah_from, ayah_to)` on the attachment pivot rather than one-row-per-ayah. See [content-types.md](../features/content-types.md).
- **People attach with roles.** Author, muhaqqiq (editor), mufti, reviewer, translator, narrator — one polymorphic people-attachment with a role type beats separate columns per role.
- **Audio segments should reference the recitation** — the same ayah has different audio per recitation (reciter x riwayah x style).
- **User data (bookmarks, progress) must reference the mushaf** — a bookmark at "page 300" means different things in different mushafs.
