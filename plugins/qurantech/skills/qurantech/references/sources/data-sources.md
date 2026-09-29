# Quran Data Sources & APIs

Quran.ws building blocks (packages and datasets, no hosted API) come first; third-party sources cover what the blocks do not: audio, translations, tafsir, search, morphology and i'rab, word audio, and hosted APIs. Block details live in [../blocks.md](../blocks.md).

## Table of Contents
- [Quran.ws Building Blocks](#quranws-building-blocks)
- [Quran Text & Script](#quran-text--script)
- [Mushaf Images & SVG](#mushaf-images--svg)
- [Qira'at & Ayah Mapping](#qiraat--ayah-mapping)
- [Fonts & Typography](#fonts--typography)
- [Audio Recitations](#audio-recitations)
- [Translations](#translations)
- [Tafsir](#tafsir)
- [Word-Level Data](#word-level-data)
- [Search Services](#search-services)
- [Pre-built Packages & Libraries](#pre-built-packages--libraries)
- [AI/ML Datasets & Models](#aiml-datasets--models)
- [Open-Source Quran Projects](#open-source-quran-projects)
- [CMS & Management Platforms](#cms--management-platforms)
- [Community Resources](#community-resources)

## Quran.ws Building Blocks

Packages and datasets from `github.com/quran-ws`; none is a hosted API (only `text.quran.ws`, `png.quran.ws` and `cdn.quran.ws` serve files). Maturity is from each README banner and may lag; confirm install status with the registry before writing install steps. Full notes: [../blocks.md](../blocks.md).

| Block | What it provides | Formats / riwayat | Install / CDN | Licence | Maturity |
|---|---|---|---|---|---|
| **quran-text** | Word-level text with one shared word numbering, pages, lines, juz, sajdat, waqf marks, riwayah differences | JSON, SQLite; 7 riwayat (Hafs, Shubah, Warsh, Qalun, Duri, Susi, Bazzi) | `@quran.ws/text` (npm), `quran-text` (PyPI), `quran-ws/quran-text` (Packagist), `quran-text-swift` (SwiftPM); Dart and Kotlin libraries in the repo; data at `text.quran.ws` | CC BY 4.0 (attribution waived inside a product) + KFGQPC terms for the text | Beta |
| **qiraat-ayah-map** | Ayah-number mappings across the 6 counting systems | JSON; ten qira'at | `@quran.ws/qiraat-ayah-map` (npm) | CC BY 4.0 (data), MIT (tooling) | Stable |
| **quran-svg** | Printed mushaf pages with ayah polygons | SVG + JSON; 5 riwayat (Hafs, Warsh, Qalun, Duri, Shubah) | GitHub release, `cdn.quran.ws/svg/pages/<version>/<edition>/` | CC BY 4.0 (polygons), MIT (tools) | Stable |
| **quran-svg-elements** | Same pages split into words and marks | SVG + JSON; Hafs only | GitHub release, `cdn.quran.ws/svg/elements/<version>/` | CC BY 4.0 + KFGQPC terms (artwork) | Beta |
| **quran-engine** | Native mushaf rendering, hit-testing, search over QVP pages | QVP page format; wrappers for Web, iOS/macOS, Android, Flutter, React Native | `@quran.ws/engine` (npm), SwiftPM `QvpKit`, `cdn.quran.ws/qvp/<version>/` | Check the repo | Beta |
| **quran-tajweed** | 182 authored rules, precomputed spans kept apart from the text | JSON spans; Hafs only | `@quran.ws/tajwid`, `-rules`, `-annotations`, `-react` (npm) | CC BY 4.0 (corpus), MIT (engine) | Stable |
| **quran-assets** | 71 recolourable SVGs: surah headers, page frames, ayah markers | SVG + `catalog.json` | Not published; read `assets/` from the repo | **Per asset** (OFL-1.1 markers; scan-derived ornaments CC BY-NC-SA 4.0, provisional) | Beta |
| **quran-png** | PNG/SVG/PDF image of an ayah range | Images from the KFGQPC mushaf | `png.quran.ws/api/v1/image/<surah>/<from>-<to>.png` | Check the terms at `png.quran.ws` | Beta |
| **kfgqpc-resources** | Byte-for-byte mirror of King Fahd Complex downloads with checksums; **not the official site** | Fonts, mushaf editions, books, audio | `cdn.quran.ws/KFGQPC/resources/<group>/<resource>/<file>` | All rights remain with the Complex | Archive |
| **docs** (guidelines) | Naming, text handling, versioning, repo conventions; terminology dictionary | Markdown | `github.com/quran-ws` docs repo | Check the repo | **Proposed** |

**Where the blocks do not apply:** audio, translations, tafsir, search, morphology and i'rab, word-level audio, hosted APIs, and non-Hafs tajweed or word-split pages. Use the sections below.

## Quran Text & Script

Blocks first: `quran-text` for text in 7 riwayat (and the font each needs), `kfgqpc-resources` for original KFGQPC files. Third-party rows below serve hosted APIs, metadata, or riwayat and scripts the blocks do not ship. Redistribution terms differ per source: Quran.ws material is CC BY 4.0 (attribution waived inside a product); KFGQPC text and artwork carry the Complex's terms; Tanzil requires attribution; verify the others before bundling.

| Source | Formats | Qira'at | Redistribution / licence | Notes |
|--------|---------|---------|--------------------------|-------|
| **quran-ws/quran-text** | JSON, SQLite, libraries in 6 languages | Hafs, Shubah, Warsh, Qalun, Duri, Susi, Bazzi | CC BY 4.0 + KFGQPC terms | Block (see above); same word number in every riwayah |
| **King Fahd Quran Complex** | Downloads (formats vary per riwayah, so verify what is published) | Hafs, Warsh, Duri, Qalun, Shubah, Susi (Bazzi per `quran-text`) | KFGQPC terms; rights remain with the Complex | Official authority. Fonts at `fonts.qurancomplex.gov.sa` (site did not respond when checked, 2026-09-29); `kfgqpc-resources` mirrors the files |
| **Tanzil.net** | Text (with aya numbers), XML, SQL | Hafs | Attribution required; do not alter the text | Verified text in several scripts (Simple, Simple Plain, Simple Minimal, Simple Clean, Uthmani, Uthmani Minimal) |
| **Quran Foundation API (v4)** | REST JSON | Hafs | Per API terms | `api-docs.quran.foundation`. Content APIs need a Developer Console app (client_id + OAuth2 client-credentials token sent as `x-auth-token` / `x-client-id`); search needs extra permission. Check the current quickstart. Use `fields=text_uthmani` and specific translation IDs to reduce payload |
| **Al Quran Cloud API** | REST JSON | Hafs | Verify | `alquran.cloud/api`. Free, no auth. Good for prototypes |
| **EveryAyah** | XML, PNG, JPG | Hafs text and images; audio includes Warsh reciters | Verify | Images + text; audio in the Audio section |
| **QUL (by Tarteel)** | Downloads (no API) + GitHub | Hafs, plus a `qpc-warsh` script | Per resource; check each | [qul.tarteel.ai](https://qul.tarteel.ai), the Toolkit for Muslim Developers. 204 translations, 115 tafsirs, ~58 segmented audio sets with word-level timestamps, 20 approved mushaf layouts, 24 font resources, ~77K morphological entries, 2.5K topics, mutashabihat, transliterations. Open-sourced on GitHub |
| **QuranPedia API** | REST JSON + dumps | 8 riwayat (12 mushafs) | See Licensing Obligations in [quranpedia-api.md](quranpedia-api.md) | `api.quranpedia.net/v1`. Free, no auth. Large tafsir/translation library (about 142 translation books; see [api-comparison.md](api-comparison.md)). 12 mushaf editions (8 riwayat) with SVG page packs (some editions) + fonts, i'rab (books + morphology + syntax), fatwas, notes, topics, reciters with timing ZIPs, search, print-book image verification, delta sync (`/v1/changes`) + bulk dumps. Reference: [quranpedia-api.md](quranpedia-api.md). Embed widget: [quranpedia-embed.md](quranpedia-embed.md) |
| **QuranHub** | REST JSON | Unverified | Verify | `api.quranhub.com`. Keyless calls returned 200 (checked 2026-09-29). Other feature claims unverified |
| **fawazahmed0/quran-api** | JSON (GitHub) | Hafs, Warsh | Per edition; verify | 400+ translations/tafsirs (492 translation editions counted). Includes Warsh text split by ayah. Community-maintained, verify accuracy |
| **KSU Electronic Mushaf** | Web | Hafs | Verify | `quran.ksu.edu.sa`. Text + tafsirs + audio |

## Mushaf Images & SVG

Blocks first. Use `quran-svg` for ayah-level interaction, `quran-svg-elements` for words and marks (Hafs only), `quran-engine` for fast native rendering, `quran-png` for a single ayah range as an image, and `quran-assets` for headers, frames and markers. Use a third-party source for editions the blocks do not ship (QuranPedia covers 12 mushafs) or for layouts from QUL.

| Source | Format | Mushafs | Features |
|--------|--------|---------|----------|
| **quran-ws/quran-svg** (block) | SVG + JSON | Hafs, Warsh, Qalun, Duri, Shubah | Clickable ayah polygons, KFGQPC editions, CDN and Brotli copies |
| **quran-ws/quran-svg-elements** (block) | SVG + JSON | Hafs (KFGQPC) | Addressable words and marks for recitation highlight, word audio, cropping |
| **quran-ws/quran-engine** (block) | QVP pages + native renderers | Hafs (KFGQPC) | Native drawing, hit-testing, masks, search; Wasm, Swift, Android, Flutter, React Native |
| **quran-ws/quran-png** (block) | PNG / SVG / PDF | KFGQPC mushaf | Ayah-range images at `png.quran.ws` |
| **QuranPedia API mushaf packages** | SVG ZIPs | 12 mushafs, 8 riwayat | `/v1/mushafs` lists per-mushaf `images` (SVG pack; present for about half the editions), `images_png` (currently null for all) and `font_file` URLs. Widest riwayah coverage. See [quranpedia-api.md](quranpedia-api.md) |
| **QUL layouts** | Layout data | 20 approved (+8 in progress) | Line and page layouts for non-KFGQPC print styles |
| **King Fahd Complex** | Images, PDFs | Multiple | Official mushaf pages; `kfgqpc-resources` mirrors the downloads |

## Qira'at & Ayah Mapping

Use `qiraat-ayah-map` (block) to convert an ayah key between the six counting systems: Kufan, Last Madinan, First Madinan, Makkan, Basran, Damascene. It covers the ten qira'at. It carries two count fields, attributed-to-qari and printed edition; see [../blocks.md](../blocks.md) and [../concepts/qiraat.md](../concepts/qiraat.md). `quran-text` also ships `ayah-map.json` for the riwayat it holds. Third-party data (QuranPedia `number_in_hafs`, tafsir and translation APIs) is Hafs-indexed: convert through Kufan when the app's riwayah is not Hafs.

**Critical:** Ayah counts belong to the edition (riwayah plus counting system), not to the riwayah alone. Never hardcode them; look them up through `qiraat-ayah-map`.

## Fonts & Typography

Blocks first: `quran-text` names the font each riwayah needs, and `kfgqpc-resources` mirrors the original KFGQPC font files with checksums. The rows below cover other scripts and hosted per-page fonts.

| Font | Source | Licence / terms | Notes |
|------|--------|-----------------|-------|
| **KFGQPC fonts** (Uthmanic Hafs, `Uthman TN`, `Uthman TS`, per-riwayah fonts) | `quran-text` (per riwayah), `kfgqpc-resources` (originals), `fonts.qurancomplex.gov.sa` (official) | KFGQPC terms | Uthmanic and Naskh styles; per-riwayah fonts for non-Hafs text |
| **Amiri / Amiri Quran** | Open source | OFL | Good browser/cross-platform support |
| **Me Quran** | `qul.tarteel.ai/resources/font/243` | Verify | Modern digital Quran typography |
| **PDMS Saleem Quran Font** | `pakdata.com/products/arabicfont` | Verify | Nastaleeq for Indo-Pak script |
| **Scheherazade** | SIL International | OFL | SIL Arabic font |
| **Quran Foundation per-page fonts** | CDN | Verify | Per-page woff2 for pixel-perfect rendering: `verses.quran.foundation/fonts/quran/hafs/v2/woff2/p{PAGE}.woff2` (V4 COLRv1 also available) |

## Audio Recitations

No block covers audio; `quran-text` and `qiraat-ayah-map` provide the ayah keys to join recordings to text.

| Source | Type | Terms | Features |
|--------|------|-------|----------|
| **MP3Quran** | Whole-surah files | Verify | [mp3quran.net/ar/api](https://mp3quran.net/ar/api): large reciter library, multiple qira'at; `surah_list` per moshaf. Ayah timings at `/ayat_timing` |
| **EveryAyah** | Ayah-by-ayah | Verify | MP3 per ayah: `everyayah.com/data/{reciter_folder}/001001.mp3` (3-digit padding, e.g. `Alafasy_128kbps`). Includes Warsh reciters. XML metadata at `everyayah.com/data/XML/` |
| **QuranicAudio** | Full & ayah-level | Verify | Streaming-friendly |
| **Quran Foundation Audio API** | Ayah + word-level timestamps | API terms | `api-docs.quran.foundation/docs/sdk/javascript/audio/`; suited to word-by-word highlighting |
| **Tahbeer Project** | Qira'at recordings | Verify | Professional recordings with iOS + Android apps. Claims about duration and authorship are unverified |
| **QuranPedia reciters** | Full surah + ayah-level, timings | See [quranpedia-api.md](quranpedia-api.md) | `/v1/reciters`: reciters across riwayat with ayah-timing ZIPs. |
| **Buraaq Word Audio Dataset** | Word-level | Verify | HuggingFace dataset for ML/speech apps |

## Translations

No block ships translations. Join through ayah keys; convert with `qiraat-ayah-map` when the app's riwayah is not Hafs.

| Source | Languages | Update Model |
|--------|-----------|-------------|
| **Tanzil.net** | 40+ languages | Static download |
| **QUL (Tarteel)** | 204 translations | Downloads |
| **Quran Foundation API** | 60+ languages | API — always current |
| **QuranEnc** | Multiple | Verified translations |
| **Fawaz Ahmed quran-api** | Multiple | GitHub repo |

**Important:** Translations are human-authored and may contain errors. Prefer API-driven sources for continuous updates. Always verify copyright before including a translation.

## Tafsir

No block ships tafsir; most tafsir sources are Hafs-indexed.

| Source | Content | Notes |
|--------|---------|-------|
| **Quran Foundation API** | Multiple tafsirs | API-driven, current |
| **QUL** | 115 tafsirs (35 mukhtasar, 80 detailed) | Downloads |
| **Spa5k tafsir API** | Multiple tafsirs | Open API |

**Legal:** Verify copyright status before including tafsir. Many tafsirs require publisher approval. Digitized versions may contain OCR errors.

## Word-Level Data

For word identity and position, `quran-text` (shared word numbering, `word-index.json`) and `quran-svg-elements` (word boxes on the page) are blocks. Morphology and word audio come from third parties.

| Source | Data |
|--------|------|
| **quran-ws/quran-text**, **quran-svg-elements** (blocks) | Word numbering, word records, per-word page boxes (no morphology, no audio) |
| **Quran Foundation API** | Word-by-word translation, transliteration, morphology |
| **QuranWBW** | Word-by-word breakdown (unverified; no URL confirmed) |
| **Buraaq Word Audio** | Word-level audio segments (HuggingFace) |

## Search Services

`quran-text` carries plain-spelling search keys and `quran-engine` has in-app search; hosted search comes from third parties.

| Source | Type | Notes |
|--------|------|-------|
| **Kalimat.dev** | Full-text Arabic search | Readiness unverified |
| **Alfanous.ai** | Keyword and Boolean search (Buckwalter supported) | Not semantic (site returned 403 to a scripted request, 2026-09-29) |
| **Quran Foundation API** | Text search | API-integrated search |

Prefer an existing search service over a custom implementation where its behaviour fits.

## Pre-built Packages & Libraries

Quran.ws blocks with native wrappers: `quran-engine` (iOS/macOS, Android, Flutter, React Native) and `quran-text` (Swift, Dart, Kotlin, PHP, Python, JS). Community packages below.

| Package | Platform | Features |
|---------|----------|----------|
| **MushafImad** (github.com/ibo2001/MushafImad) | Swift/iOS 17+, macOS 14+ | Full mushaf reader: 604 pages (line images loaded on demand), audio playback with verse sync (ayah timing JSON), reciter selection, RealmSwift offline DB, SwiftUI components (MushafView, QuranPlayer), RTL paging, theming, haptic feedback, AirPlay. MIT licensed. Individual maintainer (ibo2001), not an Itqan project. |
| **mushaf-imad-android** (`YahiaRagae/mushaf-imad-android`) | Kotlin/Android | Android equivalent — mushaf rendering, bookmarks, audio |
| **mushaf-imad-flutter** (`Itqan-community/mushaf-imad-flutter`) | Flutter | Cross-platform: display, bookmarks, search, offline storage |
| **Quran MCP** (mcp.quran.ai) | AI (Claude/ChatGPT) | Semantic search & retrieval via MCP protocol |

Prefer existing packages over building from scratch. These libraries handle the hardest parts of Quran app development — mushaf rendering, audio synchronization, offline storage — that are complex and error-prone to reimplement.

### MushafImad Quick Start (iOS/macOS)

MushafImad is the most comprehensive open-source Quran package for Apple platforms:

```swift
// 1. Add package: github.com/ibo2001/MushafImad
// 2. Initialize
try? RealmService.shared.initialize()
FontRegistrar.registerFontsIfNeeded()
// 3. Use
MushafView(initialPage: 1)
    .environmentObject(ReciterService.shared)
    .environmentObject(ToastManager())
```

Key components:
- `MushafView` — renders 604 pages, RTL paging, theming
- `QuranPlayer` / `QuranPlayerViewModel` — audio with verse timing sync
- `ReciterService` — reciter selection and persistence
- `AyahTimingService` — loads verse timing JSON for word/ayah highlighting
- Custom layouts: `horizontalPageView()`, `verticalPageView()`, `pageContent()`
- Asset override: `MushafAssets.configuration` for custom colors/images

## AI/ML Datasets & Models

| Resource | Type | Notes |
|----------|------|-------|
| **tarteel-ai/whisper-base-ar-quran** | ASR model | Used by 80 HuggingFace spaces (checked 2026-09-29) |
| **wav2vec2-base-word-by-word-quran-asr** | ASR model | Word-by-word Quran ASR |
| **QDAT (Univ. of Mosul)** | Audio dataset | Quran recitation dataset for training |
| **Iqra'Eval** | Audio dataset | ~79 hours |
| **prepare-quran-dataset** | Tool | `github.com/obadx/prepare-quran-dataset` |
| **QurSim** | NLP dataset | ~7,600 ayah pairs with graded relatedness scores |
| **CAMeL Tools** | NLP toolkit | `github.com/CAMeL-Lab/camel_tools` — Arabic morphology, dialect ID |
| **AraBERT** | Language model | `github.com/aub-mind/arabert` — Arabic BERT |

## Open-Source Quran Projects

| Project | Stack | Description |
|---------|-------|-------------|
| **OpenMushaf** | React Native (Expo) | Offline mushaf with Hafs + Warsh, tafsirs. `github.com/adelpro/open-mushaf-native` |
| **OpenTarteel** | Next.js, GunDB | Audio streaming, 30+ reciters, PWA. `github.com/adelpro/open-tarteel` |
| **BAHETH** | Python, Elasticsearch, FAISS | Hybrid semantic+lexical search. `github.com/engsaleh/Baheth-Quran` |
| **SyncQuran** | HTML/JS, WebRTC (PeerJS) | Real-time synchronized mushaf for halaqat. `github.com/hadealahmad/SyncQuran` |
| **check-telawa** | Flask, Whisper | Recitation evaluation. `github.com/engsaleh/check-telawa` |
| **Dhikr al-Huda** | Flutter | Accessibility-focused, by a blind developer. `github.com/ahmed1hegazy/Thikr_al-huda` |
| **Al-Bayan** | — | Accessible Quran app. `github.com/tecwindow/albayan` |
| **QuranApp** | Web | Word-by-word Uthmani rendering. `github.com/oazabir/QuranApp` |

## CMS & Management Platforms

| Platform | Purpose |
|----------|---------|
| **Itqan CMS** | Django 5.2 + Angular + PostgreSQL (Angular version unverified). `github.com/Itqan-community/cms-backend` |
| **RATQ** | Development guidelines + tech catalog. `github.com/Itqan-community/RATQ` |

## Community Resources

- **Itqan Platform:** `itqan.dev` — Community of developers serving the Quran
- **Itqan Community Forum:** `community.itqan.dev`
- **Quran Apps Directory:** `quran-apps.itqan.dev` — curated catalog of Quran apps
- **Quran.com Developers:** `quran.com/developers` — API docs, OAuth2, MCP
