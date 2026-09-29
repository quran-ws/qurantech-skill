# Quranic Scholarly Content Types (Beyond Tafsir)

## Table of Contents
- [Anchor Keys from the Blocks](#anchor-keys-from-the-blocks)
- [The Full Taxonomy](#the-full-taxonomy)
- [Modeling Content Attachments](#modeling-content-attachments)
- [Genre-Specific Notes](#genre-specific-notes)
- [Best Practices](#best-practices)

## Anchor Keys from the Blocks

The blocks ([blocks.md](../blocks.md)) carry no scholarly content, but they give it stable keys:

- **Ayah items** (asbab, munasabat, fada'il, fatwas, notes): anchor to the Hafs (Kufi) ayah key and convert per riwayah with `qiraat-ayah-map`, so one item attaches across riwayat. Ranges are normal on splits and merges. See [qiraat.md](../concepts/qiraat.md).
- **Word items** (gharib glossaries, word meanings): key on `quran-text` word numbers, the same in every riwayah; show the edition's own spelling. For a printed page use `quran-svg-elements` (`surah:ayah:word`, Hafs only).

## The Full Taxonomy

Most Quran apps stop at text + translation + tafsir. The scholarly tradition produced many more genres, each mapping to an app feature. Data availability varies ([data-sources.md](../sources/data-sources.md), [quranpedia-api.md](../sources/quranpedia-api.md)). In api.quranpedia.net, munasabat, amthal and fada'il exist only as book categories, with no ayah-level service. The mutashabih service returned empty on all 13 sampled ayahs; its `similar` service had data. Verify per genre against the live API.

Genre names in the table (Mutashabihat, Sayings/ma'thur) are working labels: scholar review.

| Genre | Arabic | What it is | App feature |
|-------|--------|-----------|-------------|
| **Tafsir** | تفسير | Verse commentary | Tap-ayah explanation |
| **Translations** | ترجمات معاني | Meaning translations | Multi-language display ([translations-tafsir.md](translations-tafsir.md)) |
| **I'rab** | إعراب | Grammatical analysis | Grammar views ([irab.md](irab.md)) |
| **Asbab al-nuzul** | أسباب النزول | Occasions of revelation | Context panel per ayah |
| **Nasikh/Mansukh** | الناسخ والمنسوخ | Abrogation relationships | Cross-reference links |
| **Gharib** | غريب القرآن | Rare-word glossaries (word → meaning) | Word-tap definitions |
| **Amthal** | أمثال القرآن | Parables and similitudes | Thematic study |
| **Munasabat** | المناسبات | Coherence between adjacent ayahs/surahs | "Why does this follow that?" |
| **Fada'il** | فضائل | Virtues of surahs/ayahs | Surah-info sections |
| **Mutashabihat** | متشابهات | Similar verses | Hifz aids ([memorization.md](memorization.md)) |
| **Sayings / ma'thur** | التفسير بالمأثور | Narrated exegesis with isnad chains | Scholarly deep-dive |
| **Fatwas** | فتاوى | Rulings citing ayahs; question-and-answer material belongs here | Q&A linked from verses |
| **Notes / tadabbur** | تدبر | Reflective notes with media | Reflection feed |
| **Surah info** | التعريف بالسور | Structured per-surah facts | Surah landing pages |

## Modeling Content Attachments

One relational pattern covers nearly all genres:

- **Polymorphic ayah attachment with range support**: `(content_type, content_id, ayah_from, ayah_to)`. Ranges are the norm — tafsir passages, topics, and sayings usually cover several consecutive ayahs. Don't model one-row-per-ayah.
- **In this model, key everything to Hafs anchor IDs**; other riwayat resolve through `qiraat-ayah-map` ([qiraat.md](../concepts/qiraat.md)).
- **Surah-level content gets its own pivot** — don't fake it as ayah range 1–N.
- **People attach with roles** (author, muhaqqiq, mufti, translator, narrator…) via one people-pivot with a role type.
- **Media attachments** (images, PDFs, videos, links) as one polymorphic table shared by notes, fatwas, and books.
- **Categories define services**: classify books by category and define each genre as a set of category IDs — adding a new tafsir book then needs zero code.

## Genre-Specific Notes

- **Tafsir has two natural granularities**: a curated per-ayah table (precise lookups) and book-page contents `(book, part, page)` joined to ayah ranges (preserves the printed structure, enables in-book reading). Production systems need both, with an explicit lookup priority — don't merge them.
- **Print alignment**: keep `(part, page)` on every digitized content row from day one. It enables citing the printed edition and showing scanned pages next to digital text for verification («مطابق للمطبوع») — retrofitting is far harder.
- **Sayings/isnad**: model narrators as entities with roles and generations (tabaqa), resolve "same chain as previous" print conventions at import, expand honorific ligatures (ﷺ is U+FDFA; U+FD40–FD4F are other honorific ligatures) to plain text if your fonts lack them, and deduplicate with a `merged_into` pointer rather than deleting.
- **Topics**: self-referencing hierarchy; when building A–Z indexes, derive the letter after stripping the ال prefix. Grade entry quality explicitly (has description / has children / enough ayahs / thin) and use the grade to decide what to display and index.
- **Further genres** in the QuranPedia category tree: ahkam, balagha, mubhamat, qasas, waqf/ibtida, rasm, 'add al-ay, i'jaz, tawjih al-qira'at. Adding them to this taxonomy is pending scholar review.
- **Surah info**: model as structured sections (revelation, virtues, purposes, naming, counts, order) rather than one text blob — each section can be its own screen or link target.

## Best Practices

- **Authenticity matters** for fada'il and asbab: grading varies by report, so use vetted collections and show sources.
- **Attribute everything**: author + book + (part, page) where known.
- **Plan an OCR-correction pipeline** for digitized books ([testing-qa.md](../concepts/testing-qa.md)) and per-book text-cleaning profiles in config, not code.
- **Show only available services per ayah** — a card grid computed from actual data beats fixed sections that render empty.
- **Verify licensing per work** — these genres are copyrighted scholarship ([translations-tafsir.md](translations-tafsir.md)).
