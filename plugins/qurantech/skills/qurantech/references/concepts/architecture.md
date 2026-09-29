# Architecture Patterns for Quran Apps

## Table of Contents
- [Block-First Stack](#block-first-stack)
- [Common Architectures](#common-architectures)
- [Offline-First Pattern](#offline-first-pattern)
- [Data Layer Design](#data-layer-design)
- [Multi-Qira'a Architecture](#multi-qiraa-architecture)
- [Anti-Patterns](#anti-patterns)
- [Pre-built Packages](#pre-built-packages)
- [Real-World Architecture Examples](#real-world-architecture-examples)
- [Accessibility](#accessibility)
- [Licensing Guidance](#licensing-guidance)

## Block-First Stack

Build on the Quran.ws blocks ([blocks.md](../blocks.md)) and take third-party sources only for what they do not cover (audio, translations, tafsir, search, i'rab; see [data-sources.md](../sources/data-sources.md)).

| Layer | Block | Delivery |
|---|---|---|
| Text | `quran-text` | Bundle per riwayah; the Hafs text is bundled in its libraries (`Mushaf.hafs()`). Hafs text is about 3 MB as JSON (the `quran.json` asset in [verse-recognition.md](../features/verse-recognition.md); measure `data/mushaf/hafs.json` for your build). |
| Page data | `quran-svg`, `quran-svg-elements`, `quran-engine` | Versioned, immutable CDN folders (`cdn.quran.ws/svg/pages/<version>/...`, `.../svg/elements/<version>/...`, `.../qvp/<version>/`), or bundled. The whole mushaf is about 26 MB as one QVP bundle. |
| Cross-riwayah keys | `qiraat-ayah-map` | Bundle the mapping data; convert on display, store `{surah, ayah, counting}`. |
| Layers | `quran-tajweed`, `quran-assets` | Spans apply only to the text edition they were measured on; check each asset's licence. |

Rules: pin every package and CDN version (never `latest.json` at runtime), verify recorded SHA-256 digests (`manifest.json`, `SHA256SUMS`, tajweed `edition.sha256`) after download, fetch page files one at a time, and cache them locally for offline use. Only Hafs is split in `quran-svg-elements` and `quran-engine`; other riwayat use `quran-svg` pages.

## Common Architectures

### Reading-focused app
```
UI Layer (Mushaf/Text view, Navigation)
    ↓
Feature Layer (Bookmarks, Search, Audio, Tajweed)
    ↓
Data Layer (Local DB + API sync)
    ↓
Sources (Quran text DB, Audio files, Translation API)
```

### API-first backend
```
Client apps (Web, iOS, Android)
    ↓
API Gateway (REST/GraphQL)
    ↓
Services (Text, Audio, Search, User data)
    ↓
Data stores (Quran DB, Audio CDN, Search index, User DB)
```

### Mushaf viewer
```
Rendering engine (SVG/Image viewer)
    ↓
Interaction layer (Ayah selection, Audio sync, Tajweed toggle)
    ↓
Data provider (Page data, Ayah metadata, Audio timestamps)
    ↓
Asset manager (SVG/Image cache, Font loader)
```

## Offline-First Pattern

Quran apps are expected to work offline. Users recite in mosques, during travel, and in areas without connectivity.

### Strategy

1. **Bundle essential data at install time:**
   - Full Quran text for the default riwayah (`quran-text`; Hafs text ≈ 3 MB JSON)
   - Mushaf metadata (surah info, juz/hizb mappings, page mappings)
   - At least one translation in the user's language
   - Quranic font files

2. **Download on demand:**
   - Audio files (large — let users choose what to download)
   - Additional translations and tafsirs
   - Additional mushaf SVGs/images for other qira'at

3. **Sync when online:**
   - User data (bookmarks, reading progress, memorization state)
   - Translation/tafsir updates (corrections happen over time)
   - New content (additional reciters, translations)

### Local storage options

| Platform | Storage | Best For |
|----------|---------|----------|
| Web | IndexedDB + Cache API | Text data + audio/font caching |
| iOS | Core Data / SQLite + FileManager | Structured data + audio files |
| Android | Room/SQLite + internal storage | Structured data + audio files |
| Flutter | sqflite / Hive + path_provider | Cross-platform local storage |

### Sync conflict resolution

- **Quran text never conflicts** — it's read-only from source.
- **User data (bookmarks, progress):** Last-write-wins is usually sufficient. More complex: merge bookmarks as a set (union), use latest timestamp for progress.
- **Downloaded content:** Check version/hash before re-downloading.

## Data Layer Design

### Separate Quran data from user data
- **Quran data** (text, metadata, translations) is read-only and shared.
- **User data** (bookmarks, progress, preferences) is mutable and personal.
- Keep them in separate databases/tables for clean backup, sync, and upgrade paths.

### Version your Quran data
- Include a version identifier with bundled Quran data.
- When an update is available (corrected text, new translations), apply it without losing user data.

### Index for search at build/install time
- Pre-build a search index with normalized text (stripped diacritics, normalized alef).
- Don't rebuild it at runtime.

### One data layer, many surfaces
If the same ayah content appears in multiple places (an in-app modal, an embeddable widget, a public API), render all of them from **one shared service layer** — parity is then guaranteed by construction instead of by testing. The same applies to data exports: generate bulk dumps from the same code paths that serve the API, so dump schemas never drift from API schemas.

### Data freshness: seed + delta sync
For content that receives corrections (translations, tafsir, scholarly notes), the robust offline pattern is: **seed from bulk dumps, then poll a changes feed** (`?since=<date>` returning changed record references) and refetch only what changed. This avoids both stale static bundles and full re-downloads. QuranPedia ships this ready-made ([quranpedia-api.md](../sources/quranpedia-api.md)); if you run your own backend, expose the same two surfaces.

### AI/LLM discoverability (GEO)
If your Quran content is web-facing, consider serving machine-readable twins: a markdown version of each content URL and an `llms.txt` index. Use plain Unicode Quranic text in these surfaces (never glyph-encoded text — it's garbage outside its font), so LLMs and agents quote the Quran correctly from your site.

## Multi-Qira'a Architecture

Supporting multiple qira'at requires careful separation:

```
Mushaf Selector (User picks qira'a)
    ↓
Mushaf Config (loads correct text, page data, font, ayah count)
    ↓
Feature Layer (all features use active mushaf config)
    ↓
Data Layer (each mushaf has its own text + page data)
```

**Key design decisions:**
- **One database per mushaf** or **one database with mushaf_id partitioning.** Partitioning is simpler; separate DBs are cleaner for download/delete.
- **Ayah references must always include the mushaf context.** See [data-models.md](data-models.md). Use `qiraat-ayah-map` to convert keys between counting systems.
- **User data (bookmarks) should store mushaf_id.** A bookmark in Hafs page 300 ≠ Warsh page 300.
- **Audio is tied to qira'a.** A Hafs reciter's audio should not play over Warsh text.

## Anti-Patterns

### Hardcoded ayah counts
**Wrong:** `if (ayah > 6236) throw error` (6,236 is the Kufi/Hafs count only)
**Right:** Derive max from the active mushaf's metadata.

### Universal surah:ayah references
**Wrong:** Storing `2:5` without mushaf context.
**Right:** Always pair with a mushaf or counting system identifier.

### Building Arabic search from scratch
**Wrong:** Writing custom diacritics-stripping, hamza-normalization, and fuzzy matching.
**Right:** Use a production-ready Arabic search service (Kalimat.dev, Quran Foundation API); see [search.md](../features/search.md).

### Static translation bundles
**Wrong:** Shipping translations as static JSON files that never update.
**Right:** Use API-driven sources or implement an update mechanism for static bundles.

### Mixing Quran text with user-generated content in the same table
**Wrong:** Storing Quran text and user notes in the same table/collection.
**Right:** Quran text is sacred, read-only data — isolate it architecturally.

### Ignoring font loading
**Wrong:** Rendering Quranic text immediately with a system font, then swapping.
**Right:** Block rendering of Quranic text until the proper font is loaded (`font-display: block`).

### Single-reciter assumption
**Wrong:** Building audio playback tied to one reciter's file structure.
**Right:** Abstract the audio source so reciters are interchangeable.

## Pre-built Packages

Check the blocks first, then these community packages:

| Package | Platform | What It Provides |
|---------|----------|-----------------|
| **MushafImad** (individual's repo, `ibo2001`) | Swift/iOS | Mushaf display, audio players, core Quran features |
| **mushaf-imad-android** (`YahiaRagae/mushaf-imad-android`) | Kotlin/Android | Android equivalent: mushaf rendering, bookmarks, audio |
| **mushaf-imad-flutter** | Flutter | Display, bookmarks, search, offline storage; needs about 9,000 PNGs downloaded separately |
| **Quran MCP** | AI integration | Semantic search and retrieval for Claude/ChatGPT apps via mcp.quran.ai |

See [data-sources.md](../sources/data-sources.md) for the full list of tools and libraries.

## Real-World Architecture Examples

Stacks below are limited to what each project's README confirms.

- **OpenMushaf:** Expo / React Native app, also a PWA, with offline caching.
- **OpenTarteel:** Next.js with Gun and Jotai state.
- **BAHETH** (`engsaleh/Baheth-Quran`): Flask + Elasticsearch kNN search. See [search.md](../features/search.md).
- **SyncQuran:** an experimental proof of concept for shared reading sessions; treat it as an idea, not a reference design.

### PWA as Multi-Platform Strategy
Build a web app, convert to a PWA, and wrap it with **PWABuilder** (`pwabuilder.com`) for Android and iOS packages. Updating the website then updates the app.

## Accessibility

- **Test with real screen readers** (VoiceOver, TalkBack), not only automated tools.
- **Keep the interface minimal** for blind users; every extra element is an obstacle.
- **Use semantic HTML** on the web: `<article>`, `<nav>`, ARIA labels for ayah elements.
- **Support text scaling:** Dynamic Type (iOS) and user font scaling (Android/web).
- **SVG and Canvas pages expose no text.** Provide the ayah text from `quran-text` as the accessible layer.

## Licensing Guidance

- **Quran text and artwork inherit KFGQPC terms** (`quran-text`, `quran-svg`, `quran-svg-elements`, QVP page data); block metadata is CC BY 4.0 and tools are MIT. Some assets are non-commercial: the scan-derived ornaments in `quran-assets` are CC BY-NC-SA 4.0 and provisional. Read [blocks.md](../blocks.md) and each asset's licence before shipping.
- **MIT/Apache 2.0:** best for maximum adoption of Quran libraries.
- **Copyleft (GPL/AGPL):** using a GPL library may require open-sourcing your entire app.
- **Open-core:** open-source the core, offer premium features commercially.
- **Audio and visual content** often lacks open licenses. Verify permissions before using recitation recordings.
