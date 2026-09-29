# Quran.ws Building Blocks

Quran.ws publishes open building blocks for Quran apps. Each block solves one focused problem, works alone, and combines with the others. **Check this catalog first**: use a block when it fits, and reach for third-party sources only for what the blocks do not cover (audio, translations, tafsir, search, i'rab).

Org: `github.com/quran-ws` · Site and docs: `quran.ws` · Assets host: `cdn.quran.ws`. The repo README is the source; the site holds the usage docs (`quran.ws/blocks/<name>`, `quran.ws/docs/reference/<name>`, `quran.ws/docs/build/<task>`). Fetch those pages for exact APIs — versions and package names move.

## Which block for which job

| You need to… | Use | Not this |
|---|---|---|
| Display Quran text (any of 7 riwayat), stable word IDs | **quran-text** | Hand-copied text, Hafs text transformed into Warsh |
| Show a printed mushaf page, make ayahs tappable | **quran-svg** | Rebuilding page layout from text |
| Word- or mark-level interaction (recitation highlight, word audio, meanings) | **quran-svg-elements** + **quran-engine** (+ quran-text) | quran-svg (ayah polygons only) |
| Fast native mushaf rendering on mobile/desktop | **quran-engine** | WebView over SVG for large-scale rendering |
| Tajweed colouring or rule explanations | **quran-tajweed** | Regex over text, or a tajweed-coloured font |
| Non-Hafs riwayah, or convert between ayah-counting systems | **qiraat-ayah-map** | Matching ayahs by number |
| Markers, surah headers, page frames, ornaments | **quran-assets** | Redrawing them, or copying from a live mushaf site |
| A single ayah range as an image (Canva, slides, print) | **quran-png** | Screenshotting a page |
| Naming, storing text, versioning, repo conventions | **docs** (Quran.ws guidelines) + `quranic-terminology` skill | Ad-hoc names (`aya`, `sura`, `tajweed`) |
| An original KFGQPC file (font, mushaf PDF, book, audio) | **kfgqpc-resources** | Random mirrors |

**Not covered by any block** — take from `sources/data-sources.md`: audio, translations, tafsir, search, morphology/i'rab, word-level audio timings.

## Common stacks

| App | Stack |
|---|---|
| Text reader | quran-text |
| Accurate mushaf viewer | quran-svg |
| Interactive mushaf | quran-svg-elements + quran-engine + quran-text |
| Tajweed reader | quran-text + quran-tajweed |
| Multi-riwayah app | quran-text + qiraat-ayah-map |
| Design or export tool | quran-svg + quran-assets |

Quran Tajweed also applies to quran-svg and quran-svg-elements. These are combinations, not bundles. Pull in a second block only when the experience needs it.

## The blocks

Maturity labels come from each README banner; re-check before promising stability.

### quran-text · Data · Beta
Source-verified text in **7 printed riwayat**, built from KFGQPC packages with recorded SHA-256 digests. 77,434 numbered words; the **same word carries the same number in every riwayah**, so words match across riwayat. Ships the 277 cross-riwayah differences, page and line layout, juz, sajdat, waqf marks, and the font each riwayah needs.
- Install: `npm i @quran.ws/text` · `pip install quran-text` · `composer require quran-ws/quran-text` · SwiftPM `quran-ws/quran-text-swift` · Dart and Kotlin libraries live in the main repo (`lib/`). The `-swift` and `-php` repos are read-only mirrors; file issues on `quran-ws/quran-text`.
- Data download: `text.quran.ws`. Licence: CC BY 4.0 (the work, attribution waived inside a product) plus KFGQPC terms for the text itself.
- Gotchas: waqf marks are combining characters, so inspect Unicode scalars, not grapheme clusters. Some layers are absent by riwayah (Bazzi has no juz) and the API says why. PHP: one mushaf takes ~20 MB and the word index a few hundred MB — load it in a CLI or worker, not per web request.

### qiraat-ayah-map · Data · Stable
Mappings across the **six counting systems** (madhhabs of ʿadd al-āy), covering the ten qiraat, with numbering differences, splits and merges. Use it whenever an ayah key crosses systems: a Warsh ayah to a Hafs-indexed tafsir, translation or recording.
- Install: `npm i @quran.ws/qiraat-ayah-map` (0.1.0 on the registry, includes generated `dist/mappings`; the README still says "not published"). Licence: CC BY 4.0 (data), MIT (tooling).
- **Two count fields, never joined together.** `counting_system_associated_with_qari` is the count a qāriʾ is attributed. `counting_system_printed` is what a measured printed muṣḥaf carries. They differ (Abū ʿAmr is attributed the Basri count; both King Fahd muṣḥafs of his rāwīs measure onto the First Madinan count). Join on the one that matches your source: printed text → printed count.
- Read `docs/consuming-the-mappings.md` in the repo before writing conversion code — it lists what code gets wrong, with proof entries.

### quran-svg · Pages & Assets · Stable
Vector mushaf pages with **31,118 ayah polygons**, **5 riwayat** (Hafs, Warsh, Qalun, Duri, Shubah — KFGQPC editions), one directory per mushaf under `mushafs/`.
- Fetch one page, not the repo (a plain clone is ~5.3 GiB): `curl -O https://raw.githubusercontent.com/quran-ws/quran-svg/main/mushafs/hafs/kfqc/svg/001.svg`, or sparse-checkout one mushaf.
- CDN: `https://cdn.quran.ws/svg/pages/<version>/<edition>/001.svg` and `001.json` (polygons); editions `hafs-kfqc`, `warsh-kfqc`, `qalon-kfqc`, `douri-kfqc`, `shubah-kfqc`. Page files return 200 today, but the `manifest.json` and `latest.json` the README describes for `svg/pages` returned 404 when checked (2026-09-29); `svg/elements` and `qvp` have both. Take the current version from the GitHub release (`gh release list -R quran-ws/quran-svg`) and pin it; version folders are meant to be immutable.
- A page holding two surahs also has per-surah files (`106-surah4.svg`). Read `docs/FORMAT.md` for stacking order and the two `polygon` shapes before drawing hit regions.
- Licence: CC BY 4.0 (metadata and polygons), MIT (tools).

### quran-svg-elements · Pages & Assets · Beta
The same pages decomposed into addressable **words (77,432) and marks (436,398)**. Only **Hafs (KFGQPC)** is split so far. Use for recitation highlighting, clickable words, word-level audio or meanings, cropping an ayah.
- `gh release download v1.0.0 -R quran-ws/quran-svg-elements`, or CDN `https://cdn.quran.ws/svg/elements/<version>/pages/001.svg` and `index/by-page/001.json`.
- Word count is 77,432 here and 77,434 in quran-text; expect a small difference and map by surah/ayah/word, not by count.
- Licence: CC BY 4.0 (the work), KFGQPC terms (the artwork).

### quran-engine · Rendering · Beta
Rust core rendering interactive mushaf pages with each platform's native graphics; wrappers for Web (Wasm, 311 KB), iOS/macOS (SwiftPM `QvpKit`), Android, Flutter, React Native. Pages ship in **QVP** (its optimized page format, not a separate product): whole mushaf ~26 MB as one bundle.
- Two web entry points: `@quran.ws/engine/lite` (dependency-free Canvas decoder: page drawing, word bands, hit-testing) and the full package (layout, exact hit-testing, search, styling, selection, masks, animation). `@quran.ws/engine/lite/passage` renders a standalone verse excerpt.
- Set the canvas backing size to at least 2× CSS pixels, then use the device pixel ratio; extra supersampling softens thin strokes and diacritics.
- Page data is separate: app-bundled or `cdn.quran.ws/qvp/<version>/`. Install: `@quran.ws/engine` is on npm (0.3.0 when checked, although the README says "not published"), plus `@quran.ws/qvp-react-native`; SwiftPM for iOS/macOS; the README lists Maven and pub.dev packages for Android and Flutter. Registries move faster than READMEs: confirm with `npm view` before writing install steps.
- Use it when quran-svg's ayah-level interaction is not enough, or when SVG rendering is too heavy. Otherwise skip it.

### quran-tajweed · Annotations · Stable
**182 authored rules** (127 produce spans) and **147,255 precomputed spans**, reviewed by specialists. Annotations are positional spans kept **apart from the text**: unchanged text + spans → coloured presentation. Editions in `editions/` record the exact text each span set was measured against.
- `npm i @quran.ws/tajwid @quran.ws/tajwid-rules @quran.ws/tajwid-annotations` (plus `react`, `core`, `cli` packages). The Python package is unpublished; take the dataset from a release (`gh release download v0.4.3 -R quran-ws/quran-tajweed`).
- The spans only apply to the text edition they were measured on (`edition:check` gate). Never apply them to a different text.
- Licence: CC BY 4.0 (corpus), MIT (engine).

### quran-assets · Pages & Assets · Beta
71 recolourable SVGs: surah headers, page frames, ayah markers, ornaments, Rub al-Hizb and sajdah marks. `catalog.json` is the contract: every asset carries its provenance, licence and status.
- Not published to a package registry: read `assets/` from the repo.
- **Licence varies per asset.** 40 of 47 font-derived markers are OFL-1.1. The 24 scan-derived ornaments are CC BY-NC-SA 4.0, *provisional*, so they are not safe for commercial products. Read the entry's licence in `catalog.json` before shipping.

### quran-png · Tool · Beta
Print-quality PNG/SVG/PDF of an ayah range from the real KFGQPC mushaf, transparent background, built on quran-svg-elements. Service at `png.quran.ws`; e.g. `curl -O 'https://png.quran.ws/api/v1/image/1/1-7.png'`. Includes a Canva app. Use for design tools and static images, not for in-app rendering.

### docs · Guidelines · **Proposed**
Quran.ws guidelines: naming, Quranic text, versioning and corrections, engineering, repositories. Ships the terminology dictionary (180 concepts, 755 spellings) and the `quranic-terminology` skill and audit script. **Status is "Proposed. Nothing is adopted yet"**: build against a page only once it is marked `adopted`, and present it as a strong option, not a standard. Route naming questions (ayah/surah/riwayah/tajwid spellings) to the `quranic-terminology` skill.

### kfgqpc-resources · Archive
Unmodified, byte-for-byte mirror of King Fahd Complex downloads with metadata and checksums (fonts, Hafs and riwayat mushaf editions, translations, tafsir books, audio). **Not the official site**: use it when the Complex's site is unreachable, and point users to the official source as the authority. Browse: `quran-ws.github.io/kfgqpc-resources/`. Direct URL pattern: `cdn.quran.ws/KFGQPC/resources/<group>/<resource>/<file>`. Verify downloads with the `SHA256SUMS` file. All rights remain with the Complex.

### qurantech-skill (this skill)
Guidance across all blocks; not a runtime dependency.

## Cross-block rules

1. **Start with the smallest block that works.** quran-text alone covers a reader; add blocks per need.
2. **Every block states its source, edition and riwayah.** Carry that into your data model: never assume one ayah count or one edition. Keys such as `2:255` need a counting-system or riwayah context (see `concepts/qiraat.md`, `concepts/data-models.md`).
3. **Pin versions.** Pin package and CDN versions (`v1.1.1`-style folders are immutable). Do not depend on `latest.json` at runtime.
4. **Mind licences.** Text and artwork inherit KFGQPC terms; some assets are non-commercial. Read `quran.ws/docs/reference/licensing` before shipping.
5. **Fetch the live docs for API details.** Several packages are unpublished or `0.x`. Confirm install status in the README before writing an install command.
6. **Respect maturity.** Say so when you recommend a Beta block, and note that quran-svg-elements covers Hafs only.
7. **The text stays untouched.** Annotations (quran-tajweed), highlights and styling are layers over unchanged text. `concepts/adab.md` and `concepts/testing-qa.md` still apply to every block.
