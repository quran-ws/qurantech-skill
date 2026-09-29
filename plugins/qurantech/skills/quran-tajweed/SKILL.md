---
name: quran-tajweed
description: Use when adding tajweed or tajwid colouring to Quran text, explaining a recitation rule while reading, building tajweed-learning tools, or reading, projecting or validating tajweed annotation spans (start/end/rule) from Quran.ws quran-tajweed.
---

# quran-tajweed

Follow the `qurantech` skill's adab rules (never alter or truncate Quranic text).

## Model
Annotations are positions, never markup. The text stays unchanged; spans `[start, end, ruleIndex]` map to a presentation (colour, tooltip, legend). The data holds no Quranic text.

## Addressing and edition
- Spans are keyed `"surah:ayah"` (Hafs count, 6,236 ayahs). `start`/`end` are half-open code-point positions: index with `[...text]`, never UTF-16 `slice`.
- `ruleIndex` indexes `annotations.ruleIds`; `corpus` (rules package) resolves rule to hukum, category, topic (7 topics).
- Offsets are measured against one edition, `editions/uthmani-hafs.json` in the repo (not in the npm packages). Its SHA-256 is `annotations.edition.sha256`.
- Verify first: `await assertEdition(edition, annotations.edition.sha256)`. If the app's text differs by one code point, do not use the precomputed spans; render the tajweed edition's text, or run `@quran.ws/tajwid` (`new Tajweed(corpus).analyze(text)`) over the app's own text.
- Hafs only; other riwayat are unsupported.

## Packages
- npm, 0.1.0 (verified on the registry): `@quran.ws/tajwid` (engine, `unpack`, `resolveOverlaps`, `clusterEnd`, `bridgeJoins`), `@quran.ws/tajwid-rules`, `@quran.ws/tajwid-annotations`, `@quran.ws/tajwid-react` (`TajweedText`, `TajweedLegend`). The site guide still says unpublished; trust the registry.
- Python reader: not published. Take the dataset from a GitHub release: `gh release download v0.4.3 -R quran-ws/quran-tajweed`.

## Projecting
- Text: split into runs and colour by topic. Break runs only before a base letter, extend each boundary with `clusterEnd`, and join cuts with `bridgeJoins`, so shadda and harakat stay on their letter and words stay joined. Keep joiners out of offsets and clipboard.
- Overlaps are normal (1:6 has eleven spans). Keep them for teaching, or flatten with `resolveOverlaps`.
- quran-svg / quran-svg-elements: spans address characters, not printed shapes. Do not apply offsets to SVG paths. Style marks through Quran SVG Elements by name; the joining of characters to shapes is unverified here (see references/spans.md).

## Minimal example (React: colour ayah 1:1)
```tsx
import corpus from '@quran.ws/tajwid-rules'
import annotations from '@quran.ws/tajwid-annotations'
import { unpack, assertEdition } from '@quran.ws/tajwid'
import { TajweedText, TajweedLegend } from '@quran.ws/tajwid-react'

await assertEdition(edition, annotations.edition.sha256)
const text = edition.ayahs['1:1']
<TajweedText text={text} corpus={corpus} spans={unpack(annotations, corpus, '1:1')} colors={MY_COLOURS} />
<TajweedLegend corpus={corpus} colors={MY_COLOURS} />
```
Real data: `annotations.spans['1:1']` is `[[8,10,52],[17,18,22],[22,25,129],[30,31,22],[33,36,131]]`; index 52 is `mutamathilain-idgham-kamil.23`.

## Licence
Corpus, annotations, editions, docs: CC BY 4.0 (attribute). Engine, tools, React, Python: MIT.

## Maturity and gotchas
- Colour by topic (Arabic labels only; add your own English mapping keyed on ids). The palette is yours: label it as your own, never as a printed mushaf's scheme; always ship a legend.
- Silence is not "no rule applies": only 7 topics are covered; named gaps exist (e.g. 20:1 has no spans).
- Rule status: `stable`, `disabled` (silent gap), `disputed` (spans ship; surface the objection when naming the ruling). Some rules are `needsReview`: not signed off by a qualified reviewer.
- Never edit the text to add colour or wrapper characters.
- Present output as a study aid, not a substitute for a qualified teacher.

Details: `references/spans.md`.
