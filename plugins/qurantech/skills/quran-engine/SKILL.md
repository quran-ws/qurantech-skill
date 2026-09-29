---
name: quran-engine
description: Use when a Quran app needs fast native Mushaf page rendering on mobile or desktop, word-level tap hit-testing, highlights, masking or search over QVP page files, the Quran.ws quran-engine, @quran.ws/engine, its lite Canvas decoder, cdn.quran.ws page data, or when SVG pages are too slow.
---

# quran-engine (Quran.ws rendering block)

Follow the `qurantech` skill's adab rules (never alter or truncate Quranic text).

## What it is
Rust core behind one C ABI, drawn by each platform's own canvas. It renders the split Hafs Mushaf (KFGQPC Madani) as compact binary pages (`NNN.qvp`, magic `QVP1`) with word addressing `surah:ayah:word`. Status: Beta (README banner); the site page may lag the repo, so trust the repo.

## Choose
- Browser and fast enough: use `quran-svg` (ayah tap) or `quran-svg-elements` (word tap). Engine not needed.
- Phone, desktop, or word hit-testing, masking, search costing microseconds: use the engine.
- Small Canvas reader needing page drawing and word bands: lite decoder.

## Web entry points
- Lite, no Wasm: `import { loadPage } from '@quran.ws/engine/lite'`; `page.draw(ctx, page.fit(canvas, 24))`. Words carry `surah`, `ayah`, `word`, `box`. Also `drawWords(ctx, indices, options)`, `drawDecorations(ctx, options)`, `decodeGeometry(buffer)`. Verse excerpts: `QvpPassage` from `@quran.ws/engine/lite/passage` (complete ayah range, cross-page ok, needs Canvas2D and `Path2D`; see `docs/LITE-PASSAGES.md`).
- Full: `import ... from '@quran.ws/engine'` (Wasm): layout, exact hit-testing, search, styling, selection, masks, animation.

## Install status (per README)
- Web: README shows "not published"; `npm view` returned 0.3.0 for `@quran.ws/engine`. Treat as published, verify with `npm view`.
- iOS/macOS: SwiftPM `from: "0.2.2"`, product `QvpKit`. Android: Maven `ws.quran:qvp-android:0.2.2`. Flutter: `qvp_flutter ^0.2.2`. React Native: `@quran.ws/qvp-react-native` (Android only; needs Kotlin library as Gradle project).
Details: `references/platforms.md`.

## Page data is separate
No package bundles pages. Load from `https://cdn.quran.ws/qvp/<version>/042.qvp` (also `NNN.words.json`, `atlas.qva`, `manifest.json`). Pin an exact `vX.Y.Z` (immutable, cached one year); `latest.json` names the current one (v0.4.0 when checked). Never hardcode "latest" in production. Web: fetch pages one at a time; the brotli bundle is not decodable in browsers.

## Canvas resolution rule
Backing pixels per CSS pixel: `Math.max(2, devicePixelRatio)`. Use DPR itself, never extra supersampling (softens strokes and diacritics). Set `canvas.width/height` to rect times ratio, `style` to CSS size, pass `24 * pixelRatio` to `fit`. Cap total pixels for memory.

## Hit-testing and words
- Full engine (documented): `hitTestExact(x, y)`, `hitTest(x, y, {maxDistance})`, `hitTestView`, `hitTestViewEx`, `hitBoxes()`, `wordKey(i)`, `findWord(s,a,w)`, `resolve('1:2')`, `highlight`, `mask`, `search`, `cropSvg`.
- Page units differ from viewport pixels (`…View` calls): subtract layout offset, divide by scale.
- Lite README names `page.hitTestExact(x, y)`; `web/lite.mjs` at HEAD defines `hitTest(x, y)` (box lookup). Check the installed version.

## Gotchas
- `page.nAyahs` counts per-line fragments; count ayat with `ayahKeys().length`.
- An ayah may continue on the next page; check `ayahWordCount(s,a).complete`.
- Search needs `attachWords(sidecar)`; check `hasForm('search')`.
- `revealStart()` threw in an older web wrapper; verify before use.

## Licence
Code MIT, `docs/` CC BY 4.0. Page data carries KFGQPC source-bundle terms, not MIT.
