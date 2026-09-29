# Quran API Comparison

The Quran.ws building blocks ([../blocks.md](../blocks.md)) are packages and datasets with no hosted API. They cover text, mushaf pages, tajweed spans and ayah mapping. The APIs below cover what the blocks do not: hosted access, translations, tafsir, audio, search, i'rab.

## Table of Contents
- [API Overview](#api-overview)
- [Feature Matrix](#feature-matrix)
- [Detailed Comparison](#detailed-comparison)
- [Choosing the Right API](#choosing-the-right-api)

## API Overview

| API (checked 2026-09) | URL | Auth | Rate Limits | Status |
|-----|-----|------|-------------|--------|
| **Quran.ws building blocks (packages, no hosted API)** | [github.com/quran-ws](https://github.com/quran-ws), [cdn.quran.ws](https://cdn.quran.ws), [text.quran.ws](https://text.quran.ws) | None | N/A (static files, npm/PyPI/etc.) | Active; maturity varies per block |
| **Quran Foundation (v4)** | [api-docs.quran.foundation](https://api-docs.quran.foundation) | OAuth2 client credentials (client_id + token) required for Content APIs | See docs | Active, well-maintained |
| **Al Quran Cloud** | [alquran.cloud/api](https://alquran.cloud/api) | None | Open | Active, no auth required |
| **Tanzil.net** | [tanzil.net/download](https://tanzil.net/download/) | None | N/A (download) | Static files, verified |
| **QuranPedia API** | [api.quranpedia.net/v1](https://api.quranpedia.net/v1) | None | 120/min, 10,000/day per IP | Active, comprehensive |
| **QUL (Tarteel)** | [qul.tarteel.ai](https://qul.tarteel.ai) | None | N/A (downloads; no API) | Active; licence varies per resource |
| **QuranHub** | [api.quranhub.com](https://api.quranhub.com) | None (keyless calls returned 200) | Unverified | Active |
| **EveryAyah** | [everyayah.com](https://everyayah.com) | None | N/A (static) | Active, static files |
| **MP3Quran** | [mp3quran.net/ar/api](https://mp3quran.net/ar/api) | None | Unverified | Active |
| **Alfanous** | [alfanous.ai](https://alfanous.ai) | None | Unverified | Active (site returned 403 to a scripted request) |
| **QuranEnc** | [quranenc.com/en/home/api](https://quranenc.com/en/home/api) | Unverified | Unverified | Active |
| **Quran Tafseer API** | [api.quran-tafseer.com](http://api.quran-tafseer.com/tafseer/) | None | Unverified | Responded 200 in the latest check; earlier checks timed out, so treat availability as unverified |
| **Fawaz Ahmed** | [GitHub repo](https://github.com/fawazahmed0/quran-api) | None | N/A (static) | Community-maintained, 400+ translations (492 editions counted) |
| **Quran MCP** | [mcp.quran.ai](https://mcp.quran.ai) | MCP protocol | Unverified | Active (AI integration) |

## Feature Matrix

| Feature | Quran.ws blocks (packages) | Quran Foundation | QuranPedia | QUL | Tanzil | EveryAyah | MP3Quran |
|---------|-----|-----------------|------------|-----|--------|-----------|---------|
| Quran text (Uthmani) | ✅ (7 riwayat) | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Multiple mushafs | ✅ (SVG pages, 5 riwayat) | ✅ (`mushaf=` IDs: QCF V1/V2/V4, IndoPak 15/16-line) | ✅ | ✅ (20 approved, +8 in progress) | ❌ | ❌ | ❌ |
| Translations | ❌ | ✅ (60+ languages) | ✅ (~142 books) | ✅ (204) | ✅ (40+) | ❌ | ❌ |
| Tafsir | ❌ | ✅ | ✅ (127 for 1:1) | ✅ (115) | ❌ | ❌ | ❌ |
| Print-book comparison | ❌ | ❌ | ✅ (unique) | ❌ | ❌ | ❌ | ❌ |
| I'rab | ❌ | ❌ | ✅ (books + morphology + syntax tree) | ❌ | ❌ | ❌ | ❌ |
| Audio (ayah) | ❌ | ✅ | ✅ (+ timing ZIPs) | ✅ (~58 segmented) | ❌ | ✅ | Whole surahs (ayah timings at `/ayat_timing`) |
| Audio (word-level) | ❌ (word boxes only) | ✅ | ❌ (ayah-level timings; word audio for qira'at variants) | ✅ (timestamps) | ❌ | ❌ | ❌ |
| Word morphology | ❌ | Unverified (no morphology endpoint in docs; word payload has no POS) | ✅ (QAC segments + treebank) | ✅ (77K entries) | ❌ | ❌ | ❌ |
| Topics/themes | ❌ | ❌ | ✅ | ✅ (2.5K topics) | ❌ | ❌ | ❌ |
| Mutashabihat | ❌ | ❌ | ✅ (services) | ✅ (5.2K entries) | ❌ | ❌ | ❌ |
| Delta sync + bulk dumps | ❌ (versioned downloads) | ❌ | ✅ (unique) | ✅ (downloads) | ✅ (static) | ❌ | ❌ |
| Fonts | ✅ (per riwayah, via quran-text) | ✅ (per-page fonts) | ✅ (per mushaf) | ✅ (24 font resources) | ❌ | ❌ | ❌ |
| Tajweed spans | ✅ (Hafs) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Ayah mapping across counting systems | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Search | Library only (quran-engine, quran-text keys) | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Multiple qira'at | ✅ (7 riwayat text, 5 riwayat pages) | ❌ (Hafs) | ✅ | ❌ | ❌ | ❌ | ✅ |
| Fatwas | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| User accounts/sync | ❌ | ✅ (OAuth2) | ❌ | ❌ | ❌ | ❌ | ❌ |
| Auth required | No | Yes (OAuth2) | No | No | N/A | No | No |

**Quran.ws blocks** — no hosted endpoint; install packages or fetch versioned files from the CDN. Maturity differs per block (see [../blocks.md](../blocks.md)).
**Alfanous** — keyword and Boolean search (Buckwalter supported) only.
**Quran MCP** — semantic search for AI applications only.
**Al Quran Cloud** — free, no auth, CORS-friendly, good for prototypes.

## Detailed Comparison

### Quran.ws building blocks (packages, no hosted API)
**Best for:** Verifiable text in 7 riwayat, printed mushaf pages, tajweed spans, and ayah mapping across counting systems.
- Blocks: `quran-text`, `quran-svg`, `quran-svg-elements`, `quran-engine`, `quran-tajweed`, `qiraat-ayah-map`, `quran-assets`, `quran-png`. Details in [../blocks.md](../blocks.md) and [data-sources.md](data-sources.md).
- No rate limits or accounts; you bundle the data or fetch pinned files from `cdn.quran.ws`.
- Text and pages carry KFGQPC terms; Quran.ws material is CC BY 4.0 (attribution waived inside a product).
- **Does not cover:** audio, translations, tafsir, i'rab, morphology, hosted search. Use the APIs below for these.


### Quran Foundation API (v4)
**Best for:** Full-featured Quran apps needing text + translations + audio.
- Broad single API. Content APIs need OAuth2 client credentials (client_id + token from a Developer Console app).
- Multiple mushafs selectable with `mushaf=` (QCF V1/V2/V4, IndoPak 15/16-line) and per-page font rendering; text is Hafs only.
- Word morphology: unverified (no morphology endpoint in the docs, word payload has no POS).
- OAuth2 for user features (bookmarks, last-read sync across quran.com and integrated apps).
- Word-level timestamps for audio synchronization.
- Active development, documentation at [api-docs.quran.foundation](https://api-docs.quran.foundation).
- **Limitation:** Hafs only. No multi-qira'a text support.

### QuranPedia API
**Best for:** A broad Quran API — large tafsir/translation library, 12 mushaf editions (8 riwayat), i'rab, fatwas, and unique print-book image comparison. **Full endpoint reference and use cases: [quranpedia-api.md](quranpedia-api.md).**
- Free, no authentication required. [`api.quranpedia.net/v1`](https://api.quranpedia.net/v1). Rate limit 120/min, 10,000/day per IP.
- **Tafsirs and translations:** 127 tafsirs for 1:1 (QUL lists 115) and about 142 translation books (QUL lists 204, Fawaz 492 editions). Counts as checked 2026-09; the "largest of any API" claim is unsourced.
- **12 mushaf editions (8 riwayat)** with downloadable SVG page-pack ZIPs (not every edition; `images_png` is currently null) and per-mushaf font files (`/v1/mushafs`).
- **Unique: print-book image comparison** — compare digital text against scanned images of the original printed books for verification.
- **I'rab three ways:** classical i'rab books + computed word morphology (Quranic Arabic Corpus) + dependency-treebank syntax — the only public API with all three.
- 16 per-ayah services (also `sayings`, `attachments`): tafsir, e3rab, morphology, syntax, asbab, nasekh, meanings, mutshabeh, similar, topics, fatwa, notes, qiraat (word-level variants with per-rawi audio), translations.
- Reciters with downloadable timing ZIPs; whole-book JSON downloads for translations and books.
- **Unique: delta sync** — `/v1/changes?since=` + bulk `/dumps` (gzipped, SHA-256 manifest, exact API schema) for offline-first apps.
- **Caution:** response shapes vary per endpoint (no envelope, object-vs-array polymorphism); Arabic-first fields; verify CORS before browser-side fetch. Details in [quranpedia-api.md](quranpedia-api.md).
- Also provides an **embeddable widget + oEmbed provider** — see [quranpedia-embed.md](quranpedia-embed.md).

### QUL (Quranic Universal Library by Tarteel)
**Best for:** Feature-rich apps needing a wide downloadable content library — translations, tafsirs, fonts, morphology, and audio with word-level timestamps.
- Downloads only: QUL has no API (its FAQ says so). Licences vary per resource, so check each before use. Source on GitHub. [qul.tarteel.ai](https://qul.tarteel.ai).
- 204 translations, ~22 word-by-word translation sets.
- 115 tafsirs (35 mukhtasar, 80 detailed).
- ~58 segmented audio sets with word-level timestamps.
- 20 approved mushaf layouts (+8 in progress).
- 24 font resources (homepage count).
- ~77,400 morphological entries (grammar, roots, lemmas, stems).
- 2,512 topics with semantic relations, 5,277 mutashabihat entries, 4,001 similar ayahs.
- Community contribution tools for proofreading and annotation.
- Backed by Tarteel.ai (known for Quran AI/speech recognition).
- **Strength:** Wide single resource collection for Quran app data. The "toolkit for Muslim developers."

### Al Quran Cloud API
**Best for:** Prototypes, simple apps, or projects needing zero authentication.
- Free, no API key needed.
- Text in multiple scripts + translations + audio.
- Supports CORS (unlike some other APIs).
- **Limitation:** Less feature-rich than Quran Foundation. No word-level data.

### Tanzil.net
**Best for:** Offline apps needing verified, static Quran text.
- Gold standard for verified Quranic text accuracy.
- Download once — no API dependency.
- Formats: text, text with aya numbers, XML, SQL.
- **Limitation:** Static download only, no API. No audio/tafsir. Requires attribution.

### EveryAyah
**Best for:** Simple ayah-by-ayah audio with predictable URL patterns.
- Dead-simple file structure: `everyayah.com/data/{reciter_folder}/001001.mp3` (3-digit surah + 3-digit ayah, `/data/` prefix, e.g. `Alafasy_128kbps`).
- Also provides mushaf page images (PNG/JPG).
- **Limitation:** Audio only (and images). No text API, no translations.

### MP3Quran
**Best for:** Large reciter library across multiple qira'at.
- Extensive collection of reciters.
- Supports multiple qira'at (not just Hafs).
- API lists reciters and their recordings as whole-surah files (`surah_list` per moshaf); ayah timings are separate at `/ayat_timing`.
- **Limitation:** Audio only. No text or translation data.

### Alfanous
**Best for:** Keyword and Boolean Quran search.
- The README describes keyword and Boolean search with Buckwalter support; no semantic search claim is supported.
- **Limitation:** Search-only service. Not a general Quran data API.

## Choosing the Right API

**Choosing between blocks and an API**
- Need verifiable text, tajweed spans, a native or printed-mushaf display, or ayah mapping → the **Quran.ws blocks**.
- Need a hosted API, translations, tafsir or audio → **Quran Foundation, QUL, QuranPedia or MP3Quran**.
- Most apps combine both: blocks for text and pages, an API for content. Join through ayah keys; convert with `qiraat-ayah-map` when the riwayah is not Hafs.

**Starting a new app?**
→ Text and pages from the blocks (`quran-text`, `quran-svg`). Add **QUL** for data resources (wide content library) and **Quran Foundation API** for live features (OAuth, search). Supplement with **MP3Quran** for more reciters.

**Need multiple mushafs and qira'at?**
→ `quran-svg` (5 riwayat pages, ayah polygons) and `quran-text` (7 riwayat) with `qiraat-ayah-map` for ayah keys. **QuranPedia API** adds mushaf editions the blocks do not ship (12 mushafs, 8 riwayat) with fonts and SVG packs.

**Need i'rab (grammatical analysis)?**
→ **QuranPedia API** is the only API with i'rab data — classical books, computed morphology, and syntax trees. See [quranpedia-api.md](quranpedia-api.md).

**Need to keep an offline app's data fresh?**
→ **QuranPedia** dumps + `/v1/changes` delta sync is the only ready-made mechanism. Seed from dumps, poll changes. Block data is versioned; pin and update by version.

**Embedding Quran content in a website with no backend?**
→ **QuranPedia embed widget / oEmbed** — see [quranpedia-embed.md](quranpedia-embed.md).

**Need many translations and tafsirs?**
→ **QUL** (204 translations, 115 tafsirs, downloads), **QuranPedia** (~142 translation books, 127 tafsirs for 1:1, plus print-book image comparison) and **Fawaz Ahmed** (492 translation editions). Counts checked 2026-09. No block ships these.

**Need word-level features?**
→ Word identity and page boxes: `quran-text` and `quran-svg-elements`. Word-level audio timestamps: **Quran Foundation API** and **QUL**. Morphology: **QUL** (and QuranPedia); Quran Foundation is unverified.

**Need verified offline text?**
→ `quran-text` (source-verified against KFGQPC, 7 riwayat, bundled with your app). **Tanzil.net** is the alternative for Hafs with several scripts; it requires attribution.

**Need tajweed colouring?**
→ `quran-tajweed` (Hafs spans kept apart from the text). No API in this comparison provides it.

**Building an AI/LLM integration?**
→ Use **Quran MCP** ([mcp.quran.ai](https://mcp.quran.ai)) for semantic retrieval in Claude/ChatGPT apps.

**Need multi-qira'a audio?**
→ **MP3Quran** has the widest reciter/qira'a coverage.

**Combine sources strategically.** No single source covers everything. A typical full-featured app uses 2-3 beside the blocks:
- Text, pages, tajweed, ayah mapping → Quran.ws blocks (`quran-text`, `quran-svg`, `quran-tajweed`, `qiraat-ayah-map`)
- Content library (translations, tafsirs, morphology) → QUL
- Live API (search, user sync, OAuth) → Quran Foundation
- Extra riwayat mushaf editions, i'rab, fatwas → QuranPedia API
- Additional reciters → MP3Quran / EveryAyah
- Keyword/Boolean search → Alfanous; semantic retrieval → Quran MCP
