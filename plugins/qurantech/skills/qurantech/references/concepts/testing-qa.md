# Testing & QA for Quran Apps

## Table of Contents
- [Why Quran Apps Need Special QA](#why-quran-apps-need-special-qa)
- [Block gates first](#block-gates-first)
- [Text Integrity Verification](#text-integrity-verification)
- [Rendering QA](#rendering-qa)
- [Multi-Qira'a Test Matrix](#multi-qiraa-test-matrix)
- [Audio QA](#audio-qa)
- [Search QA](#search-qa)
- [Accessibility QA](#accessibility-qa)
- [Expert Review](#expert-review)
- [Release Checklist](#release-checklist)

## Why Quran Apps Need Special QA

A rendering bug in a normal app is cosmetic. In a Quran app, a dropped diacritic, a missing waqf mark, or a mis-numbered ayah silently corrupts sacred text for every user. Text integrity bugs are the one category that must reach production probability zero — automate the checks, don't rely on eyeballing Arabic.

## Block gates first

Each Quran.ws block ships its own checks. Run them, and make your CI verify against a released dataset, before writing generic tests (see [blocks.md](../blocks.md)).

- **quran-text**: sources carry recorded SHA-256 digests, and the repo has a `conformance/` folder (a search-fold suite in JS and Python) that your search normalization should pass. Numbering checks are invariants of the format (`numbering.total` identical in all seven files; every number covered by a word or listed in `missing`). `counting.measured_from` names the release each count was measured from.
- **quran-tajweed**: `assertEdition(edition, annotations.edition.sha256)` at load, and the repo's `edition:check` gate. If your text differs by one code point, the precomputed spans do not apply.
- **qiraat-ayah-map**: the repo's `tests/validate.mjs`, and `docs/consuming-the-mappings.md` for the traps (`merges_with_next` independent of `status`; the reverse direction is lossy at splits). Turn its proof entries into your own fixtures.
- **quran-svg**: `tools/audit_ayah_polygons.py` audits the ayah polygons; run it, or its checks, on any mushaf you add or change. Assert both `polygon` shapes parse (path data on pages 3+, bare point list on pages 1-2).
- **quran-assets**: read each asset's `license` in `catalog.json` at build time and fail on anything not `confirmed` unless cleared.

**CI recipe against a released dataset digest:**
1. Pin one edition, not a mix of sources: Tanzil, KFGQPC and QUL are different texts. Record its version and SHA-256 in your repo. `quran-text` does this with one primary source (the KFGQPC v3.0 `.docx`), hashed in `data/manifest.json`, files under `sources/`.
2. Take the expected SHA-256 from upstream (the `manifest.json` pattern), never from a hash you computed yourself: a self-computed hash cannot detect a bad import.
3. In CI, download the release, compute the digest, and fail the build on mismatch. Also assert the corpus is non-empty (expected ayah and word counts), so an empty file cannot pass.
4. At startup, recompute the digest of the bundled text and assert it equals the pinned value.
5. Re-run the gates above whenever the pin changes, and record the new digest in the changelog.

## Text Integrity Verification

The single most important test suite in any Quran app.

- **Byte-exact comparison against the source.** After every build/import step, compare each stored ayah byte-for-byte against the pinned edition (for example the `quran-text` release). Any transformation (trimming, normalization, encoding conversion) is a bug. This byte comparison is the real guard against normalization. A test like `NFC(text) != text` cannot serve as one: it passes vacuously wherever NFC equals the text.
- **One exception, comparing across datasets:** normalise both sides to NFC in a throwaway comparison copy, never in the stored source (`quran-text` `docs/format.md`; the adab rule against normalising the source still holds). The `quran-text` Hafs text is not NFC (about 22,000 of 84,000 tokens write shaddah before the vowel), and it keeps waqf and sajdah signs in a separate layer (`docs/text-source.md`), so a raw comparison against another dataset fails for reasons that are not errors.
- **Checksum the corpus** against the upstream digest (above); catches partial writes, corrupted bundles, and accidental edits.
- **Assert counts from metadata, not constants, and check structure, not only totals:** 114 surahs; per-surah ayah counts matching the active mushaf's metadata; total ayahs matching the mushaf, keyed by counting system id. A correct total is not a correct parse (`quran-text` lessons): also check each surah's ayahs, numbering and word coverage.
- **Unicode pipeline test:** pass ayahs with special codepoints (small alef `U+0670`, waqf signs `U+06D6–U+06DC`, other Quranic marks up to `U+06ED`) through DB, API and UI and assert they survive. Load the fixtures from the pinned source by reference (`surah:ayah`), as `quran-text` `conformance/search-fold.json` does; never hand-type Quranic text ([adab.md](adab.md)). Compare scalars, not grapheme clusters: waqf marks are combining characters.
- **Basmalah rules:** read `has_basmalah` per surah and per edition. Whether the basmalah is part of 1:1 depends on the counting system: it is counted in Kufi/Makki, not in Warsh (`counting.basmalah_counted`, unnumbered ayah 0).

## Rendering QA

Automated string tests can't catch shaping bugs — use screenshot tests on real renderers.

- **Golden-glyph pages:** screenshot-test a fixed set of known-problematic passages: madd signs mid-word, alif khanjariyya, stacked diacritics, waqf marks, ayah-end markers with numbers. Compare against approved reference images.
- **Test iOS and Android separately,** on real devices: the platform text engines differ (see [text-rendering.md](text-rendering.md)).
- **Font fallback test:** simulate font-load failure and assert the app shows a Quranic fallback font or the ayah reference — never a system Arabic font ([adab.md](adab.md)).
- **Dark mode:** verify tajweed colors remain distinguishable and mushaf images/SVGs remain legible (never naive color inversion).
- **Bidi/mixed content:** ayah + translation + Latin numbers on one screen; assert no reordering artifacts. Test with actual Quranic text, which has more combining marks than generic Arabic.
- **Text scaling:** maximum Dynamic Type / font-scale settings must not truncate ayahs (rewrap or scroll instead — truncation violates adab).

## Multi-Qira'a Test Matrix

Each supported riwayah multiplies the QA surface. Minimum matrix per riwayah:

| Check | Why |
|-------|-----|
| Ayah count matches the edition's counting system (read from data) | Totals (6,204–6,236) belong to counting systems, and printed counts can differ from attributed ones ([qiraat.md](qiraat.md)) |
| Boundary ayahs where systems split/merge | The classic cross-qira'a bug; take cases from qiraat-ayah-map (`covers_multiple`, `merges_with_next`; the `merged` and `split` status strings are unverified). Concrete case: 2:1 and 2:2 merge in Warsh/Qalun ([qiraat.md](qiraat.md)) |
| Bookmarks/progress carry mushaf key and counting system | Page 300 in Hafs ≠ page 300 in Warsh |
| Font matches the riwayah | Hafs fonts misrender Warsh letterforms |
| Audio reciter's riwayah matches displayed text | A Hafs recording over Warsh text is a data bug |
| Known word variants render correctly | Use quran-text `differences.json` (277 words) as fixtures |

## Audio QA

- **Boundary test:** every ayah audio file starts at the beginning of the ayah — spot-check per reciter, especially first/last ayahs of surahs.
- **Timestamp drift:** for word-level highlighting, verify sync at the start, middle, and end of long surahs (drift accumulates).
- **Completeness:** assert the app knows which surahs/ayahs a reciter is missing and degrades gracefully.

## Search QA

Test the Arabic normalization edge cases from [search.md](../features/search.md) as fixtures:

- Query without diacritics matches Uthmani text with diacritics.
- Hamza/alef variants (أ إ آ ا) all match; ة matches ه.
- Reference patterns navigate directly: `2:255`, `البقرة 255`, `Al-Baqarah 255`.
- Results always contain complete ayahs, sorted in mushaf order.
- Zero-result queries show a graceful fallback, not an empty screen.

## Accessibility QA

Run with real assistive tech, not just automated audits (most Quran apps fail here — see [architecture.md](architecture.md)):

- VoiceOver (iOS) / TalkBack (Android) can navigate to and read every ayah, and announces surah:ayah references sensibly.
- All controls (play, repeat, bookmark) have labels; the mushaf page view exposes ayah-level elements, not one giant image.
- Contrast passes WCAG AA for translation/tafsir text and tajweed colors; color is never the only indicator.

## Expert Review

Some things cannot be verified by tests:

- **Tajweed coloring** must be reviewed by someone qualified in tajweed — wrong coloring teaches wrong recitation.
- **Translations/tafsir content** must come from verified sources with licensing confirmed; digitized tafsirs need OCR-error spot checks, including quoted ayahs checked against the pinned text.
- **Any AI-generated content** requires human scholarly review before release ([adab.md](adab.md)).
- Recruit beta testers from the actual audience (Warsh readers, huffaz); they catch errors developers cannot.

## Release Checklist

Before every release:

- [ ] Block gates green and dataset digest matches the pinned release; text integrity suite green (byte-exact, counts, Unicode survival)
- [ ] Golden-glyph screenshots approved on iOS and Android
- [ ] Multi-qira'a matrix run for every bundled riwayah
- [ ] Offline mode exercised: fresh install, airplane mode, core reading + audio + search work
- [ ] Audio spot checks per newly added reciter
- [ ] Screen reader pass on the main reading flow
- [ ] Licenses verified for any new translation/tafsir/audio content
- [ ] Data version, SHA-256 and changelog updated (source and version of the Quranic text documented)
