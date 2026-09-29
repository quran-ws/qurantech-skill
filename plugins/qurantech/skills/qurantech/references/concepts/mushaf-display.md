# Mushaf Page Display

## Table of Contents
- [Choosing an Approach](#choosing-an-approach)
- [Ayah-Level Pages: quran-svg](#ayah-level-pages-quran-svg)
- [Word-Level and Native: quran-svg-elements and quran-engine](#word-level-and-native-quran-svg-elements-and-quran-engine)
- [Frames and Markers: quran-assets](#frames-and-markers-quran-assets)
- [Text-Based Rendering: quran-text Layout](#text-based-rendering-quran-text-layout)
- [Image-Based Rendering (Fallback)](#image-based-rendering-fallback)
- [Page Navigation](#page-navigation)
- [Best Practices](#best-practices)

## Choosing an Approach

Use the Quran.ws blocks first, in this order:

1. `quran-svg`: printed pages, tap or highlight an ayah (5 riwayat).
2. `quran-svg-elements` + `quran-engine`: words and marks, native rendering (Hafs only).
3. `quran-assets`: frames, headers, markers.
4. `quran-text`: text with page and line layout.
5. Raster images: fallback only.

## Ayah-Level Pages: quran-svg

Vector mushaf pages (glyph outlines) with one clickable polygon per ayah, in Hafs, Warsh, Qalun, Duri and Shubah (KFGQPC editions). Inline the SVG to style and hit-test it. Fetch single pages, not the repo: a plain clone is several GiB. Pin a version; do not depend on `main` or `latest`.

- **The files hold no text.** They are not searchable or copyable. Search and copy use `quran-text`, joined by surah and ayah reference.
- Store the mushaf key beside every page number: page N differs per mushaf.
- Pages are heavy on phones; use the Brotli copies or `quran-engine`.

## Word-Level and Native: quran-svg-elements and quran-engine

- `quran-svg-elements`: the same pages split into addressable words and named marks, keyed `surah:ayah:word`. Only Hafs is split so far. Join to `quran-text` on the key, not on strings.
- `quran-engine`: Rust core drawing natively. Page data (QVP) is separate: bundle it or pin a CDN version. Use it for phones, desktop, hit-testing and search; otherwise skip it.

## Frames and Markers: quran-assets

Recolourable SVG surah headers, page frames and ayah markers (`catalog.json` is the contract). They hold no Quranic text; put the edition's own ayah number in the marker's slot. Check each asset's `license.status` before shipping: the scan-derived ornaments are provisional and non-commercial.

## Text-Based Rendering: quran-text Layout

For apps that do not need exact mushaf layout, `quran-text` supplies the structure:

- Pages, lines, juz, sajdat and waqf marks are layers of positions into the word array; `render(marks, ayahMarks, lines)` builds display strings. Lines are reconstructed, and some layers are absent per riwayah (Bazzi has no juz). Check `has(...)` first.
- Render in the font the mushaf names ([text-rendering.md](text-rendering.md)).
- Add surah headers from your own metadata or `quran-assets` banners. The basmalah is its own field ([adab.md](adab.md)).

## Image-Based Rendering (Fallback)

Use raster page images only when the vector blocks cannot serve the case. For a single ayah range as an image, use `quran-png`.

- **Hit regions:** the `quran-svg` polygons align only with images that share the same page geometry (same mushaf, edition and pixel size). Scale from the SVG `viewBox`, and do not overlay them on a different scan.
- EveryAyah images are per-ayah, not per-page. This skill has no verified source for full-page image sets from other providers, so vet the source and its licence yourself.

## Page Navigation

Page, juz, hizb and rub' counts are specific to the printed edition. The familiar figures describe the Madinah 604-page print; other prints differ. Read divisions from the data instead of hard-coding a table: `quran-text` page and juz layers (`page_starts`, `juz_starts`), or the division indexes in `quran-svg-elements`.

Offer page number, surah, juz and last-read position; store the last-read position with its mushaf key ([data-models.md](data-models.md)).

## Best Practices

- **Always show the mushaf edition/qira'a** in the UI so users know which mushaf they are viewing.
- **Support pinch-to-zoom**; in landscape consider a two-page spread.
- **Dark mode:** for inlined SVG, set ink and paper colours explicitly through `fill` and the page background, and check that thin strokes and marks stay legible. For raster images, use a designed overlay. Never apply a plain invert or a blanket CSS filter to either; it can make text illegible.
- **Orientation:** the mushaf opens right-to-left. In a swipeable view, swipe LEFT to go to the NEXT page.
- **Loading states:** show a placeholder matching the page dimensions; never show a spinner over where Quranic text will appear.
