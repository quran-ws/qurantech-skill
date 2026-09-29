### FILE answer.md
# Surah banners & ayah markers for a paid Quran app

This is from my general knowledge, not live research. Licenses and repos change, so re-verify every item below against its current source before you ship. This is not legal advice.

## Key point: the Quran text is not the issue, the artwork is

The Quran's words are not copyrightable. The specific **artwork, fonts, and digital encodings** are. A "printed mushaf style" banner or ayah marker may be a copyrighted design belonging to a publisher, a calligrapher, or a font foundry. Copying scans or tracing from a printed mushaf can infringe, even though the text is free.

## Where to get assets

1. **Quran-specific fonts that include ayah markers and surah frames**
   - **King Fahd Complex (KFGQPC) fonts**, e.g. Uthmanic Hafs and the QCF page-by-page fonts. These are the standard source and are widely used. Their license terms have historically been restrictive and have changed over time, so read the current terms on the complex's site before using them commercially.
   - **Quran.com's open-source projects** (the quran.com-frontend repos and their font/asset resources). Check each repo's license file and any notes about the font files it bundles, because the code license may not cover the fonts.
   - **Amiri Quran** (Khaled Hosny), **Scheherazade New** (SIL), and **Noto Naskh Arabic**. These are under the SIL Open Font License, which allows commercial use and embedding. Ayah-end glyphs (۝) are in Unicode (U+06DD), and these fonts render them.
2. **Surah name calligraphy/banners**
   - Some Quran apps and data projects publish surah-name glyph fonts or SVGs. Confirm the license for each.
   - Commission an illustrator or calligrapher to draw an original banner and ornament set, with a written **work-for-hire or full-assignment/commercial license** agreement. This is the safest route for a paid app and gives you a distinctive look.
   - Marketplaces such as Envato, Creative Market, and Adobe Stock sell Islamic ornament packs. Read the license, since many exclude apps or require an extended license for distribution inside a paid product.
3. **Build them yourself**
   - Ayah markers are simple geometric rosettes (circle or octagon, with a number inside). Draw them as SVG and place the numerals with an Arabic-Indic digit font. You get full ownership, and they scale cleanly.
   - Surah banners can be a reusable ornamental frame (SVG) with the surah name set in a licensed or OFL calligraphic font.

## Checklist before shipping

- **License for each asset:** does it allow commercial use, embedding in an app, redistribution inside a paid product, and modification? Keep a copy of each license and the download date.
- **Fonts specifically:** check the **embedding/app-bundling** rights, not just "desktop use". SIL OFL is fine. Custom or proprietary font licenses often differ for apps.
- **Attribution requirements:** include the required credits in an in-app Licenses/About screen (OFL and CC-BY need this).
- **Share-alike or non-commercial terms:** avoid CC-BY-NC and CC-BY-SA assets, or understand exactly what obligations they place on your app.
- **Provenance:** don't use images extracted from a printed mushaf, or from another app's bundle, without permission. Publishers such as the King Fahd Complex and Madinah mushaf publishers may claim rights in their layout and ornament.
- **Text source and accuracy:** the Quran text must be correct. Use an authenticated source (for example the King Fahd Complex text, or Tanzil with its license terms) and follow its conditions. Tanzil, for instance, requires that the text not be altered and that attribution be kept. Have a qualified person review the text and rendering. Errors in tashkeel or glyph placement are a serious problem for a Quran app.
- **Rendering:** test ayah numbers and marker glyphs on real devices, in RTL, at different font sizes and OS versions. Text shaping differs across Android, iOS and web.
- **Respectful use:** check that the app never places ornaments, or the text, in undignified contexts. Follow community norms for showing Quranic text (for example, no ads over ayahs).
- **Get written confirmation when a license is ambiguous:** email the author or publisher and keep the reply. For a paid product, this is worth the effort.
- **Trademarks:** don't imply endorsement by the King Fahd Complex, Quran.com, or others unless they have agreed.

## Recommendation

For the lowest risk in a paid app: use an **OFL-licensed Quran font** for the text and ayah-end glyph, **draw your own SVG marker and banner set** (or commission it under a full commercial license), and only use KFGQPC fonts after confirming their current terms in writing. Add a Licenses screen listing everything you use.


### FINAL MESSAGE
I wrote the answer to `answer.md`. It comes from my general knowledge, not live research, so check every license against its current source before you rely on it.

- **The artwork is the risk, not the text.** The Quran's words are free, but printed-mushaf ornaments, fonts and their digital encodings can be someone's copyright.
- **Where to get assets:**
  - Fonts under the SIL Open Font License, which allows commercial use and app embedding: Amiri Quran, Scheherazade New and Noto Naskh Arabic. They render the Unicode ayah-end glyph (U+06DD).
  - King Fahd Complex (KFGQPC) fonts, the standard source. Confirm their current commercial terms in writing first.
  - Quran.com's open-source projects. Check each repo's license, since the code license may not cover the fonts.
  - Ornament packs from stock marketplaces, but only under a license that allows use inside a paid app.
- **What I'd do:** draw your own SVG ayah markers and surah banners, or commission them under a full commercial license. That gives you a distinctive look and clear ownership. Use an OFL font for the text.
- **Before shipping:**
  - Keep a copy of each asset's license.
  - Check font embedding rights.
  - Avoid non-commercial and share-alike terms.
  - Add an in-app Licenses screen for required credits.
  - Don't lift images from a printed mushaf or another app.
  - Use an authenticated text source and follow its conditions.
  - Have a qualified person review the text and rendering.
  - Test RTL rendering on real devices.