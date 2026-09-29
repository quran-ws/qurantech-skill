# Eval results (2026-09-29, model sonnet)

| config | checks passed |
|---|---|
| with_skill | 6/6 (100%) |
| baseline | 4/6 (67%) |

| eval | category | with_skill | baseline | skills invoked (with_skill) | expected |
|---|---|---|---|---|---|
| 3 interactive-mushaf-word-highlight | routing | 6/6 | 4/6 | qurantech:quran-engine, qurantech:quran-svg-elements, qurantech:qurantech | qurantech, quran-svg-elements, quran-engine |

## Failed checks

### 3 interactive-mushaf-word-highlight (baseline)
- FAIL [assert] Chooses quran-engine (native QVP pages) and/or quran-svg-elements (web SVG) for word-level interaction rather than quran-svg (ayah polygons only) — The plan never mentions quran-engine or quran-svg-elements; it picks a Flutter QCF-font approach instead.
- FAIL [assert] States that quran-svg-elements currently covers Hafs only, or otherwise flags coverage limits — quran-svg-elements is not mentioned, so it never says it covers Hafs only. The plan does flag limits on timing coverage, but the check is about the block's coverage.
