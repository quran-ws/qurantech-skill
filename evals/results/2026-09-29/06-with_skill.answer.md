### FILE answer.md
# Surah banners and ayah markers for a paid Quran app

## Where to get them

Use the Quran.ws **quran-assets** library (repo: `quran-ws/quran-assets`). It is a beta set of 71 recolourable SVGs in three types: `surah-headers`, `page-frames` and `ayah-markers`. There are two lineages:

| Lineage | Count | What it is |
|---|---|---|
| `font` | 47 ayah markers | Taken from the U+06DD glyph of Arabic fonts |
| `scan` | 24 assets (8 of each type) | Traced from eight printed mushafs |

The scan lineage looks most like the printed mushaf. It is also the one with the licence problem (see below).

**Package status:** the library is not published as a package yet. Vendor the files from the repo's `assets/` directory and **pin the commit**. If you inline several assets in one page, use a build after commit `5843b12`, which makes the `<use>` ids unique.

## What you can ship in a paid app

`catalog.json` is the source of truth. Each entry has a `license` object with `id`, `status`, `attribution` and `note`.

| Assets | Licence | Status | Paid app? |
|---|---|---|---|
| 40 font ayah markers | OFL-1.1 | confirmed | **Yes.** Ship the OFL text and the font-family notice with them (`dist/LICENSES.md`, `sources[].license`). |
| 7 font markers (designs 014-020) | none asserted | unverified / pending | **No.** Exclude them. |
| All 24 scan assets, including every surah header banner | CC-BY-NC-SA-4.0 | provisional | **No, not until cleared.** These are publishers' ornaments and the permission is still being settled. NC means non-commercial, so a paid app is out of bounds. |

**Surah header banners:** all the banners in this library are scan assets. That means none of them can go into a paid app today.

Options for the banners:
1. Get written permission from the publisher of the mushaf you like, or clear it through the Quran.ws project. Then record that clearance in your repo.
2. Have a designer draw original banners. You can use the scan banners as layout references, such as slot positions, but not as artwork.
3. Launch with the OFL markers and a plain, self-made header until the banners are cleared.

Even with clearance, keep the attribution the asset's `license.attribution` and `sources` fields ask for (the mushaf and the archive item).

## Checklist before shipping

1. **Build-time licence gate.** Read each asset's `license.status` and fail the build on anything that is not `confirmed`, unless you have recorded a clearance. Filter by licence status, not by lineage alone.
2. **Ship the notices.** Include the OFL text and font-family notices for every marker you use, plus attributions for anything else. Show them in an About or Licences screen.
3. **Exclude markers 014-020.**
4. **Pin the vendored commit.** The library is unpublished and in beta, so it can change under you.
5. **Ayah numbers use the edition's own count.** Write the number from the edition you display. Ayat al-Kursi is 255 in Hafs and 253 in Warsh. If you support more than one riwayah, map counts properly (see the `qiraat-ayah-map` block).
6. **Size the number from the marker's slot height or `r`, not its width.** Use the `data-slot` rectangle (`x y w h` in viewBox units) and convert it to percentages to overlay your text.
7. **Match asset keys to the printing.** Scan asset keys use names such as `mushaf-douri`, `-sousi` and `-qalon`. These differ from the quran-text keys (duri, susi, qalun), so map them explicitly.
8. **Inline the SVG; do not use `<img>`.** Recolour with CSS: `fill` on the `c1`..`cN` groups and `stroke` on `line`. Leave `slot` transparent. `c1` is often the paper colour, so do not map it to a dark colour. Size with CSS, because the root has a `viewBox` of height 100 and no width or height.
9. **Adab.** The assets contain no Quranic text. Render the surah name and the ayah number in the slot with your own text. Never alter or truncate Quranic text to fit an ornament. Check that banners and markers stay legible in dark mode and at large accessibility text sizes.
10. **Frames:** if you use the `mushaf-hafs-madinah-kabir` page frame, it has no `slices`, so scale its `color.svg`. Page frames carry the same scan licence caveat as the banners.

## Related option

If you want complete printed pages, letters and ornaments included, use the Quran.ws `quran-svg` block. Check its own licence separately.

## Recommendation

Launch with OFL-confirmed font markers, which are safe. Treat the banners as blocked on permission, and put the licence gate in your build now so nothing provisional slips in later.


### FINAL MESSAGE
I wrote the answer to `answer.md`. In short:

- **Source:** the Quran.ws `quran-assets` library (repo `quran-ws/quran-assets`). It isn't published as a package yet, so vendor the files from the repo and pin the commit.
- **Ayah markers:** 40 of the font-derived markers are OFL-1.1 and confirmed, so you can ship them in a paid app. The OFL text and font notices must travel with them.
- **Markers to exclude:** 7 font markers (designs 014-020) have no verified licence.
- **Surah header banners:** all banners in the library are scan assets under CC-BY-NC-SA-4.0, marked provisional. The publisher permission is still being settled, and NC rules out a paid app. You need clearance or your own artwork first.
- **Before shipping:**
  - Add a build-time gate that fails on any asset whose `license.status` is not `confirmed`.
  - Ship the attributions.
  - Write the ayah number from the edition's own count.
  - Inline the SVGs rather than using `<img>`.

The file also covers the recolouring and slot details.