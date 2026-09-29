# Arabic Text Rendering & Fonts

## Table of Contents
- [Block-First Summary](#block-first-summary)
- [RTL Layout](#rtl-layout)
- [Fonts: quran-text First](#fonts-quran-text-first)
- [Skipping Font Shaping: Glyph Outlines](#skipping-font-shaping-glyph-outlines)
- [Unicode & Encoding](#unicode--encoding)
- [Line Breaking](#line-breaking)
- [Common Pitfalls](#common-pitfalls)

## Block-First Summary

- Text and the font each riwayah needs: `quran-text`.
- Original KFGQPC files: `kfgqpc-resources` (mirror).
- No shaping at all: `quran-svg`, `quran-svg-elements`, `quran-engine`.
- Other fonts: the third-party table below.

## RTL Layout

- Set `dir="rtl"` on the root container of any Quranic text.
- Use CSS `direction: rtl` and `text-align: start` (follows the direction) for Quranic content areas.
- In mixed-language UIs (Arabic + English), use CSS `unicode-bidi: isolate` to prevent bidi algorithm issues.
- Flexbox and Grid follow `dir="rtl"` on their own. Do not add `flex-direction: row-reverse`: under RTL it flips the row back to LTR order. Use logical properties (`margin-inline-start` instead of `margin-left`).
- Mobile: set `android:layoutDirection="rtl"`. SwiftUI follows the system layout direction; `Environment(\.layoutDirection)` only reads it. To force RTL, use `.environment(\.layoutDirection, .rightToLeft)`.
- **Test with real ayahs loaded from a released dataset** (`quran-text`), not generic Arabic — Quranic text has more diacritics and special characters ([adab.md](adab.md)).

## Fonts: quran-text First

The `quran-text` skill ships the text with KFGQPC fonts. Its `catalog.json` calls each font the only one guaranteed to draw its mushaf, and each mushaf's `font` block names the one it needs (`m.font.family`, `m.font.file`).

- **Hafs:** every `quran-text` package bundles the Hafs font next to `hafs.json`. Flutter uses `TextStyle(fontFamily: m.font.family, package: 'quran_text')`; the web uses `m.fontFace()` for a `@font-face` rule; Swift and Kotlin register the file with the system.
- **Other riwayat:** take the font from `quran-text`'s `data/fonts/` (or its download service). Read the family and file from the mushaf's `font` block; the repo bundles these seven TTFs:

| Riwayah | Family name | File |
|---------|-------------|------|
| Hafs | KFGQPC HAFS Uthmanic Script | `UthmanicHafs-v-3.0.ttf` |
| Warsh | KFGQPC Warsh Uthmanic Script | `UthmanicWarsh-v-3.0.ttf` |
| Qaloun | KFGQPC Qaloun Uthmanic Script | `UthmanicQaloun-v-3.0.ttf` |
| Duri | KFGQPC Douri Uthmanic Script | `UthmanicDouri-V20.ttf` |
| Shu'ba | KFGQPC Shuba Uthmanic Script | `UthmanicShubah-v-3.0.ttf` |
| Sousi | KFGQPC Sousi Uthmanic Script | `UthmanicSousi-v-3.0.ttf` |
| Bazzi | KFGQPC Bazzi Uthmanic Script | `UthmanicBazzi-v-3.0.ttf` |

- **Font licence:** the fonts are under KFGQPC's own terms, not a standard licence (`quran-text` `NOTICE.md`: copied unmodified, they remain under the Complex's terms). The terms allow use in websites and software. They do not cover printing mushafs or importing them for commercial sale. They say nothing about modification, so get the Complex's permission before you convert to woff2 or edit the file in FontForge.
- **Warsh, Qalun and Sousi:** the text uses Arabic Extended-B codepoints that general fonts cannot draw. A blank line means the wrong font, not missing data.
- **Render helper:** `render(marks, ayahMarks, lines)` adds waqf marks, division/sajdah signs, ayah-end markers and line breaks. Waqf marks are combining characters: inspect Unicode scalars, not grapheme clusters.
- **Original files:** `kfgqpc-resources` mirrors the King Fahd Complex downloads byte for byte, with `SHA256SUMS`. It is not the official site: point users to the Complex as the authority and use the mirror when the site is unreachable.

### Font loading rules

1. **Load the font the active mushaf names**, and preload it.
2. **Do not fall back to another Quranic font or a system font.** A missing glyph disappears or shows as a box, and the reader may not notice. Check the character set against the font's `cmap` at build time; if the font fails at runtime, show the reference and an error ([adab.md](adab.md)). The Quran.ws guidelines say this too (status Proposed).
3. **Use `font-display: block`**, not `swap`: a short blank is better than Quranic text in the wrong font.

```css
@font-face {
  font-family: 'KFGQPC HAFS Uthmanic Script'; /* use m.font.family */
  src: url('/fonts/UthmanicHafs-v-3.0.ttf') format('truetype');
  font-display: block;
}
```

### Third-party fonts (fallback, not the default)

Use only when `quran-text`'s fonts do not fit. Check licence and glyph coverage of your text first. Do not use one for Warsh or another riwayah unless you have checked its glyph coverage against that text.

| Font | Style | Riwayah | Licence | Note |
|------|-------|---------|---------|------|
| **Amiri Quran** | Traditional Naskh | Hafs | OFL-1.1 ([aliftype/amiri](https://github.com/aliftype/amiri)) | Readable on screen; verify glyph coverage against your text |
| **Me Quran** | Modern digital | Hafs | Unverified | Check licence |
| **Digital Khatt** | Variable font | Hafs | Unverified | Check licence |

## Skipping Font Shaping: Glyph Outlines

The Quran.ws page blocks draw the printed mushaf as glyph outlines, so no shaping engine is involved and no font is needed.

| Block | What you get |
|-------|--------------|
| `quran-svg` | Vector pages, no text in the files, one clickable polygon per ayah (5 riwayat) |
| `quran-svg-elements` | The same pages split into words and marks (Hafs only, Beta); colour is `fill` on paths |
| `quran-engine` | Native rendering with each platform's own canvas (QVP pages); use when SVG is too heavy |

### iOS and Android shaping

Quranic fonts rely on OpenType shaping (contextual alternates, mark positioning), and the platform text engine decides how well it runs. This file has no tested evidence of which iOS or Android versions break which passages. Test on real devices ([testing-qa.md](testing-qa.md)). To avoid the question, draw outlines instead of text: `quran-svg` or `quran-svg-elements` through `react-native-skia` or `react-native-svg`, or `quran-engine` (React Native wrapper `@quran.ws/qvp-react-native`, Android only per its skill). `batoulapps/quran-svg` is an unrelated project.

### Per-page glyph fonts (third-party)

Quran Foundation ships per-page woff2 fonts where each word is one glyph (`verses.quran.foundation/fonts/quran/hafs/v2/woff2/p{PAGE}.woff2`). The result is pixel-faithful but is not real text: copy-paste, search and screen readers need a separate `quran-text` layer. Prefer the outline blocks above.

## Unicode & Encoding

- **Always use UTF-8** encoding for Quranic text.
- Quranic Arabic uses characters from several Unicode blocks:
  - `U+0600–U+06FF` — Arabic (base letters, harakat, and small Quranic signs)
  - `U+0610–U+061A` — honorific and small signs (`U+0610` salla, `U+061A` small kasra)
  - `U+06D6–U+06DC` — waqf and small high signs; `U+06D6–U+06ED` also holds small letters and other Quranic marks, so it is not waqf-only
  - `U+08D3–U+08FF` — Arabic Extended-A marks
  - Arabic Extended-B — used by Warsh, Qalun and Sousi in `quran-text`
  - `U+FB50–U+FDFF` and `U+FE70–U+FEFF` — Presentation Forms-A and B (legacy ligatures; unverified for Quranic use here, so do not depend on them)
- **Uthmani text uses codepoints outside basic Arabic**, such as the superscript alef `U+0670` (in the standard Arabic block) and small high noon `U+06E8`. Ensure your font and rendering pipeline supports them.
- **Normalization caution:** Do not normalize Quranic text stored or shown. NFC and NFD both reorder or compose marks (both reorder shadda+fatha; NFC turns alef+maddah into `U+0622`), so the codepoint sequence no longer matches the source. The one exception is comparing across datasets: normalise both sides to NFC in a throwaway comparison copy, never in the stored source, as `quran-text`'s `docs/format.md` says ([testing-qa.md](testing-qa.md)).

## Line Breaking

- **Never break in the middle of a word.** Arabic cursive script connects letters; browsers do not break inside Arabic words by default, so do not add `word-break: break-all` or `overflow-wrap: anywhere` to Quranic containers. `word-break: keep-all` is a CJK setting and has no use here.
- **Prefer breaking at ayah boundaries** for Quranic text.
- **Justify carefully:** `text-align: justify` changes spacing in text that is set for its printed lines. Avoid it, or check the result against the printed page.
- **Printed line breaks:** `quran-text` `render(lines=true)`; lines are reconstructed, so treat them as a layout aid.

## Common Pitfalls

1. **String length ≠ character count** in Arabic. Diacritics are separate Unicode characters. `"بِسْمِ"` is 3 visible letters but 6 Unicode code points.
2. **String reversal breaks Arabic.** Never reverse a string containing Arabic text.
3. **Substring operations are dangerous.** Cutting at byte/codepoint boundaries can split a letter from its diacritics.
4. **Copy-paste introduces invisible characters.** Always sanitize pasted Quranic text against verified sources.
5. **Emoji and Arabic in the same line** can cause bidi rendering chaos. Isolate them with `U+2068` (FSI) and `U+2069` (PDI) or CSS `unicode-bidi: isolate`.
6. **HTML tags in API responses.** Quran.com API translations sometimes contain `<sup>` tags. Clean with regex before display.
