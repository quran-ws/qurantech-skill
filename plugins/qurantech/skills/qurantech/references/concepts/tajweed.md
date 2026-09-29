# Tajweed Color Coding

## Table of Contents
- [Overview](#overview)
- [quran-tajweed: The Block](#quran-tajweed-the-block)
- [Rules and Example Colours](#rules-and-example-colours)
- [Waqf (Pause) Marks](#waqf-pause-marks)
- [Alternatives and Why They Are Worse for Text Integrity](#alternatives-and-why-they-are-worse-for-text-integrity)
- [Implementation Notes](#implementation-notes)
- [Best Practices](#best-practices)

## Overview

Tajweed is the set of rules governing pronunciation of Quranic recitation. Colour-coded tajweed marks the letters where a rule applies. Present it as a study aid, not a substitute for a qualified teacher.

## quran-tajweed: The Block

Start with the Quran.ws `quran-tajweed` block (see the `quran-tajweed` skill). It holds 182 authored rules (127 produce spans) and 147,255 precomputed spans. Review is partial: 12 rules are `needsReview` (not signed off by a qualified reviewer) and 2 are `disputed`.

**The span model:**
- Annotations are positions, never markup: spans `[start, end, ruleIndex]` over unchanged text. The data holds no Quranic text.
- Each span set is measured against one recorded text edition (with a SHA-256). Verify the edition before use and never apply spans to a different text. If your text differs, use its engine over your own text, or render the tajweed edition's text.
- Presentation (colour, tooltip, legend) is yours. The data covers 7 topics; silence does not mean no rule applies. The published spans are Hafs only.

Pair it with `quran-text`. It also applies to `quran-svg` and `quran-svg-elements`, but spans address characters, not printed shapes, so do not apply offsets to SVG paths.

**Rule coverage is evolving.** Open pull requests (#1 to #4) on `quran-ws/quran-tajweed` add Hafs-specific waqf and verse-ending performances (imala, tashil, ishmam, rawm) and change ra' mumala to tarqiq. Rule text and counts may change; check the released package. Surface `needsReview` and `disputed` status when naming a ruling.

## Rules and Example Colours

The palette below is **Quran.com's**, taken from the stylesheet `app/assets/stylesheets/shared/tajweed.scss` in TarteelAI/quranic-universal-library (QUL). The colours are a presentation choice of that app, not part of the rules and not a printed mushaf's scheme. Choose your own, label it as yours, and always ship a legend. `quran-tajweed` resolves each rule to a topic (7 topics) you can colour.

| Rule (Quran.com class) | Arabic | Quran.com colour | Applies To |
|------|--------|-------|-----------|
| **Ghunnah** (`ghunnah`) | غنّة | Orange `#FF7E1E` | Noon/meem with shaddah (nasalization) |
| **Ikhfa** (`ikhafa`) | إخفاء | Purple `#9400A8` | Noon sakinah/tanween before specific letters |
| **Ikhfa shafawi** (`ikhafa_shafawi`) | إخفاء شفوي | Magenta `#D500B7` | Meem sakinah before ب |
| **Idgham with ghunnah** (`idgham_ghunnah`) | إدغام بغنّة | Green `#169200` | Noon sakinah/tanween before ي ن م و |
| **Idgham without ghunnah** (`idgham_wo_ghunnah`) | إدغام بلا غنّة | Green `#169200` (same as with ghunnah) | Noon sakinah/tanween before ل ر |
| **Iqlab** (`iqlab`) | إقلاب | Cyan `#26BFFD` | Noon sakinah/tanween before ب |
| **Qalqalah** (`qalaqah`) | قلقلة | Red `#DD0008` | Letters ق ط ب ج د when sakin |
| **Madd** (`madda_normal`, `madda_permissible`, `madda_necessary`, `madda_obligatory`) | مد | Blues `#537FFF`, `#4050FF`, `#000EBC`, `#2144C1` | Alef, waw, ya when elongated |
| **Lam shamsiyyah** (`laam_shamsiyah`) | لام شمسية | Gray `#AAAAAA` | Lam in ال before sun letters |
| **Hamzat wasl** (`ham_wasl`) | همزة الوصل | Gray `#AAAAAA` | Alef of wasl, written but not pronounced when joined |
| **Silent letter** (`slnt`) | حرف لا يُنطق | Gray `#AAAAAA` | Other written letters not pronounced |

Idhhar has no row: the Quran Foundation API returns no idhhar class, so unmarked text is not proof that the rule is absent. Colour is your choice; allow customization.

## Waqf (Pause) Marks

Waqf marks tell the reciter where stopping is required, preferred, permitted, or forbidden. They are part of the mushaf text and must never be stripped or rendered incorrectly.

| Mark | Codepoint | Name | Meaning |
|------|------|------|---------|
| مـ | U+06D8 | Waqf lazim | Stop is required — continuing may distort meaning |
| قلى | U+06D7 | Al-waqf awla | Stopping is preferred |
| صلى | U+06D6 | Al-wasl awla | Continuing is preferred |
| ج | U+06DA | Waqf ja'iz | Stop or continue — both acceptable |
| لا | U+06D9 | La waqfa fih | Do not stop here |
| ∴ ∴ | U+06DB | Mu'anaqah (three dots) | Stop at one of the two marks, not both |
| س | U+06DC | Saktah | Brief pause without taking a breath |

**Implementation notes:**
- Waqf signs are the Arabic-block characters `U+06D6–U+06DC`. Neighbouring codepoints are not waqf: `U+06DD` end of ayah, `U+06DE` start of rub el hizb, `U+06E9` place of sajdah, and `U+06EA–U+06EC` marks used for imala, tashil and ishmam (quran-tajweed PR #1 matches on these). Arabic Extended-A (`U+08D3–U+08FF`) is outside this range. `quran-text` carries waqf marks as combining characters on words (with a separate `marks` layer), so inspect Unicode scalars, not grapheme clusters. Never filter them out during processing or normalization.
- They render as small superscript glyphs; a proper Quranic font is required (generic Arabic fonts often render them as boxes or misplace them).
- Treat waqf data as part of the mushaf edition, not universal. Whether stop points differ between riwayat needs scholar review before you state it.
- In tajweed-learning apps, waqf marks deserve their own legend entry alongside the color rules.

## Alternatives and Why They Are Worse for Text Integrity

Use these only when `quran-tajweed` does not fit.

| Alternative | Why it is worse |
|-------------|-----------------|
| Pre-coloured or tag-embedded text (for example the Quran Foundation API) | Markup or markers sit inside the text, so the stored text is no longer the plain source; you cannot verify it against a digest |
| Regex or rule detection over plain Uthmani text | Contextual rules and optional marks make it error-prone, and an untested regex near Quranic text can silently change it. Acceptable only inside a tajweed-education tool with expert review |
| Tajweed colour font | Colours are fixed; the tajweed edition becomes its own glyph-coded "mushaf" that needs the searchability caveats in [text-rendering.md](text-rendering.md). Specific fonts are unverified here |
| Pre-rendered tajweed images | Pixels only: no text, no toggle, no legend control |

**Quran Foundation endpoint:** `https://api.quran.com/api/v4/quran/verses/uthmani_tajweed?verse_key=1:1` returns `text_uthmani_tajweed` with `<tajweed class=...>` markup and 17 distinct classes (measured over chapter 2). Content APIs now need client credentials; check the current Quran Foundation docs.

## Implementation Notes

- **Rules overlap.** Keep overlaps for teaching, or flatten with `resolveOverlaps`.
- **Highlight precisely.** Colour only the letters the rule applies to, not the whole word, and keep shadda and harakat with their letter.
- **Matching against Uthmani text needs normalization** of optional marks. Keep an explicit list of what your matcher strips, and never apply it to the displayed text ([adab.md](adab.md)).

## Best Practices

- **Make tajweed colors toggleable.** Not all users want colored text — advanced readers find it distracting.
- **Provide a color legend** accessible from the tajweed view so users can learn what each color means.
- **Use reviewed annotation data** (`quran-tajweed`) rather than implementing rule detection from scratch.
- **Test with a tajweed expert.** Incorrect tajweed colouring is worse than none.
- **Accessibility:** Ensure color choices have sufficient contrast. Offer alternative indicators (underline, bold) for color-blind users.
- **Dark mode:** Tajweed colors must remain distinguishable on dark backgrounds. Test and adjust the palette for both modes.
- **Match the edition.** Annotations must match the active riwayah and text edition; `quran-tajweed` spans are Hafs only.
