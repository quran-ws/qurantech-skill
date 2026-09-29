# Eval results (2026-09-29, model sonnet)

| config | checks passed |
|---|---|
| with_skill | 70/72 (97%) |
| baseline | 57/72 (79%) |

| eval | category | with_skill | baseline | skills invoked (with_skill) | expected |
|---|---|---|---|---|---|
| 0 warsh-support-flutter | integrity | 9/9 | 8/9 | qurantech:qiraat-ayah-map, qurantech:qurantech | qurantech, qiraat-ayah-map |
| 1 wordpress-ayah-embed | routing | 5/6 | 5/6 | qurantech:qurantech | qurantech |
| 2 hifz-app-design | honesty | 8/8 | 8/8 | qurantech:qurantech | qurantech |
| 3 interactive-mushaf-word-highlight | routing | 5/6 | 4/6 | qurantech:quran-engine, qurantech:quran-svg-elements, qurantech:qurantech | qurantech, quran-svg-elements, quran-engine |
| 4 tajweed-reader | integrity | 6/6 | 6/6 | qurantech:quran-tajweed | qurantech, quran-tajweed |
| 5 warsh-tafsir-join | integrity | 6/6 | 4/6 | qurantech:qiraat-ayah-map | qurantech, qiraat-ayah-map |
| 6 ornament-licence-check | honesty | 6/6 | 4/6 | qurantech:quran-assets | qurantech, quran-assets |
| 7 translations-and-audio-no-block | honesty | 6/6 | 5/6 | qurantech:qurantech | qurantech |
| 8 multi-riwayah-schema | integrity | 7/7 | 6/7 | qurantech:qiraat-ayah-map, qurantech:qurantech | qurantech, qiraat-ayah-map |
| 9 daily-ayah-notification | adab | 6/6 | 3/6 | qurantech:qurantech | qurantech |
| 10 offline-verse-recognition | honesty | 6/6 | 4/6 | qurantech:qurantech | qurantech |

## Failed checks

### 0 warsh-support-flutter (baseline)
- FAIL [must_not] Produces the Warsh text by transforming the Hafs text with code — The verse_map is built by aligning both texts, but the Warsh text itself is sourced from KFGQPC and is not derived from Hafs. The plan does not violate the check.

### 1 wordpress-ayah-embed (with_skill)
- FAIL [must_not] Recommends building a custom backend or WordPress plugin — It offers an optional custom shortcode (~10 lines in functions.php) and suggests a snippet plugin, though the main recommendation is a hosted widget with no custom plugin.

### 1 wordpress-ayah-embed (baseline)
- FAIL [assert] Recommends an embed/oEmbed solution that requires no custom backend or plugin maintenance (e.g., an embeddable Quran widget service), rather than building one — It recommends a custom-written JS snippet calling the Quran.com API rather than an embeddable Quran widget or oEmbed service, so the user has to maintain their own code.

### 3 interactive-mushaf-word-highlight (with_skill)
- FAIL [assert] Chooses quran-svg-elements and quran-engine for word-level interaction rather than quran-svg (ayah polygons only) — Chooses quran-engine but explicitly puts quran-svg-elements under 'Not chosen' (web-only), so it does not choose both.

### 3 interactive-mushaf-word-highlight (baseline)
- FAIL [assert] Chooses quran-svg-elements and quran-engine for word-level interaction rather than quran-svg (ayah polygons only) — The plan never mentions quran-svg-elements or quran-engine; it picks QCF fonts and Quran.com/QUL data.
- FAIL [assert] States that quran-svg-elements currently covers Hafs only, or otherwise flags coverage limits — It doesn't mention Hafs-only coverage of quran-svg-elements or any coverage limit of that kind.

### 5 warsh-tafsir-join (baseline)
- FAIL [assert] Converts through a maintained mapping dataset (for example qiraat-ayah-map) instead of hand-written offsets — Says 'Don't hand-write the map' but builds it with a custom word-alignment script; a published dataset is only an optional alternative and qiraat-ayah-map isn't named.
- FAIL [assert] Recommends scoping ayah keys by counting system or riwayah — It never recommends scoping ayah keys by counting system or riwayah. It only adds a Warsh-to-Hafs mapping table.

### 6 ornament-licence-check (baseline)
- FAIL [assert] Recommends quran-assets (or equivalent open, recolourable SVG source) instead of redrawing or copying from another app — Does not recommend quran-assets or an equivalent open recolourable SVG source; it suggests fonts, commissioning, marketplaces, and drawing your own.
- FAIL [assert] Warns that some assets are non-commercial or provisional and not safe for a paid app without clearance — Warns about CC-BY-NC/share-alike and restrictive KFGQPC terms, but doesn't say some assets are provisional or not cleared for a paid app.

### 7 translations-and-audio-no-block (baseline)
- FAIL [assert] States that the Quran.ws building blocks do not provide translations or audio, or otherwise does not present them as translation or audio sources — The answer never mentions Quran.ws building blocks, so it doesn't state that they lack translations or audio.

### 8 multi-riwayah-schema (baseline)
- FAIL [assert] Text is loaded from a versioned dataset and the schema does not require editing or normalising the Quranic text — The schema stores text_uthmani and a derived text_search normalized column, but never mentions a versioned dataset or load provenance; the normalization is a stored derived column.

### 9 daily-ayah-notification (baseline)
- FAIL [assert] Does not let an ellipsis or a mid-ayah cut stand in for the ayah text — The answer includes a shorten() fallback that ends with "…" for the collapsed line, so an ellipsis-cut ayah can still stand in for the text.
- FAIL [assert] Shows either a labelled fragment with its reference and a way to the full ayah, or the reference only, with the full ayah rendered in the app — The main approach sends the full ayah text in the body, and the reference-only option appears only as a fallback, so it does not clearly show a labelled fragment or a reference only.
- FAIL [must_not] Truncates Quranic text with an ellipsis as the solution — The shorten() helper truncates the text on a word boundary and appends "…" for the collapsed line.

### 10 offline-verse-recognition (baseline)
- FAIL [assert] States accuracy or capability limits honestly and does not claim reliable tajweed grading — It lists accuracy limits, but the closest it comes on tajweed is 'Do not claim it verifies recitation correctness unless you build that separately', which doesn't clearly state that tajweed grading is unreliable.
- FAIL [assert] Maps the recognised result to an ayah reference and notes it depends on the counting system or riwayah — It maps matches to surah:ayah using a bundled Tanzil text, but never says the reference depends on the counting system or riwayah; it mentions qira'at only as an accuracy factor.

## Notes

- Eval 3's assertion was loosened after this run (a native app can use quran-engine with QVP pages instead of quran-svg-elements); the re-run in `../2026-09-29-rerun-3/` scores 6/6 with the skill and 4/6 without. With that re-run, the skill scores 71/72 (99%) and the baseline 57/72 (79%).
- The one remaining skill failure is eval 1: the main answer is the hosted embed widget, but it also offered an optional custom shortcode, which trips the `must_not` on custom plugins.
- Evals where the baseline also passes everything (2 and 4) test the model, not the skill.
- One run per eval; the judge is a model. Treat differences of one check as noise.
