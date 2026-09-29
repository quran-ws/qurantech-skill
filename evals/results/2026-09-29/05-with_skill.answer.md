### FILE answer.md
# Warsh ayahs showing the wrong tafsir, or none

## What is going wrong

Warsh (riwayat Warsh from Nafiʿ) is numbered by the **Madani-last** counting system (`madani-last`, 6,214 ayahs). Your tafsir table is keyed by **Kufan/Hafs** numbering (`kufi`, 6,236 ayahs). The two systems disagree on where ayahs begin and end, so a Warsh `(surah, ayah)` pair is not a Hafs `(surah, ayah)` pair.

Joining on the raw pair fails in three ways:

1. **Wrong tafsir (shift).** After a disputed boundary the numbers drift. Warsh 2:5 may be Hafs 2:6, and you show the tafsir of a neighbouring ayah.
2. **Wrong or partial tafsir (merge).** One Warsh ayah can cover two Hafs ayahs. The classic case is Al-Fatiha. Warsh counts the basmala as 1:1, so Warsh 1:1 covers Hafs 1:1 and 1:2. A direct join returns only Hafs 1:1 and drops the other.
3. **None (split or overrun).** One Hafs ayah can be split into two Warsh ayahs. Near the end of a surah, the Warsh number may not exist in Hafs, or the Warsh surah may have a different count. The lookup then returns no row.

Round-tripping does not fix this. The reverse of a split loses which half you were on.

## The fix

Kufan is the hub. Convert **Warsh → Kufan** with `madani-last-to-kufi`, then join on the Kufan numbers. The conversion returns an array. Join over all of it and never take only the first element.

Install and pin the data:

```
npm i @quran.ws/qiraat-ayah-map@0.1.0
```

Confirm the version with `npm view`. The README still says "not published". The tarball ships `data/` and `dist/mappings`.

Reverse-map entries look like this:

- `{ hafs_ayah, status: "mapped" }`
- `{ hafs_ayah, hafs_ayahs: [...], status: "covers_multiple" }`

Keys are strings.

```js
import rev from "@quran.ws/qiraat-ayah-map/dist/mappings/by-counting-system/madani-last-to-kufi.json" with { type: "json" };
// If your build lacks the dist/ files, run `npm run generate` in the repo,
// or use the committed data/*.json.

/** Warsh (surah, ayah) -> array of Hafs ayah numbers. Always an array. */
export function warshToHafs(surah, ayah) {
  const e = rev.surahs?.[String(surah)]?.ayahs?.[String(ayah)];
  if (!e) return [];                       // unmapped: handle explicitly, do not guess
  return e.status === "covers_multiple" ? e.hafs_ayahs : [e.hafs_ayah];
}

/** Tafsir entries for a Warsh ayah. tafsirByHafs is keyed "surah:ayah" in Hafs. */
export function tafsirForWarsh(surah, ayah, tafsirByHafs) {
  const hafs = warshToHafs(surah, ayah);
  return hafs
    .map(a => ({ hafsRef: `${surah}:${a}`, text: tafsirByHafs[`${surah}:${a}`] }))
    .filter(t => t.text != null);
}
```

Example: `warshToHafs(1, 1)` returns `[1, 2]`, so you render both tafsir entries under Warsh 1:1.

Do not assume `surah` is unchanged. Use the surah key you looked up. In these mappings the surah number is stable, and only the ayah numbers move.

### SQL version

If the join is in SQL, load the mapping into a table. It has one row per Warsh ayah and Hafs ayah pair:

```sql
CREATE TABLE warsh_to_hafs (
  surah INT, warsh_ayah INT, hafs_ayah INT,
  PRIMARY KEY (surah, warsh_ayah, hafs_ayah)
);

SELECT m.warsh_ayah, t.hafs_ayah, t.text
FROM warsh_to_hafs m
JOIN tafsir t ON t.surah = m.surah AND t.ayah = m.hafs_ayah
WHERE m.surah = :surah AND m.warsh_ayah = :ayah
ORDER BY t.hafs_ayah;
```

Populate it by expanding each reverse-map entry: one row for `hafs_ayah`, or one row per element of `hafs_ayahs`.

## Rendering rules

- **Show every returned tafsir entry** for a merged ayah. Never show only the first.
- If the array is empty, show "no tafsir mapped for this ayah". Do not fall back to the raw `(surah, ayah)` pair. That fallback is the original bug.
- The forward direction (Kufan → Warsh) uses `kufi-to-madani-last.json`. A Hafs ayah with `status: "split"` carries `splits_into: [n, m]`, so show a range. `merges_with_next: true` is a separate field, so test it directly and not through `status === "merged"`.
- Never rely on `_counting_system` or `_mapping_file`. They are deprecated aliases.

## Prevent it recurring: store the counting system

Store `{surah, ayah, counting}` for bookmarks, notes, and progress, never a bare `surah:ayah`. Better still, store the **Kufan reference** and convert only when displaying. Then a riwayah switch cannot silently move a bookmark to a different ayah.

```js
// bookmark = { surah: 2, ayah: 5, counting: "madani-last" }
```

Do not normalise by round trip. Warsh → Kufan → Warsh is lossy for split ayahs.

## Caveats

- The package is version 0.1.0 and has no schema or types. Files mix `_` metadata with data, so read only the `surahs` tree.
- The data has 246 disputed boundary positions.
- `data/` is CC BY 4.0, so attribute it.
- Do not identify a counting system by its total ayah count. The First Madinan total is under dispute.
- If you also ship the seven editions bundled with `quran-text`, its `data/ayah-map.json` maps a Hafs reference to each of them. Use that instead if it covers your editions.
- I did not run this against your app. Test the mapping against known cases: 1:1 (merge), and a few ayahs after each disputed boundary in the surahs users reported.


### FINAL MESSAGE
I wrote the explanation and fix to `/tmp/eval5-with_skill-zfi1ee8u/answer.md`. I haven't run any of the code, and the mapping files themselves weren't available to check here.

**What's going wrong:** Warsh uses the `madani-last` counting system (6,214 ayahs) and your tafsir table uses Hafs/Kufan numbering (6,236). Joining on the raw `(surah, ayah)` pair therefore gives:
- **Wrong tafsir:** numbers drift after disputed boundaries, so you get a neighbouring ayah's tafsir.
- **Partial tafsir:** one Warsh ayah can cover two Hafs ayahs. Warsh 1:1 covers Hafs 1:1 and 1:2, so a direct join returns only the first.
- **No tafsir:** a Warsh number can fall on a split ayah or overrun a surah, and then no Hafs row exists.

**The fix:**
- Convert Warsh to Kufan with the `madani-last-to-kufi` mapping from `@quran.ws/qiraat-ayah-map`, pinned to 0.1.0.
- The conversion always returns an array. Join over all of it and show every tafsir entry.
- An empty result should show "no tafsir mapped", not fall back to the raw pair.
- `answer.md` has a JS helper (`warshToHafs`, `tafsirForWarsh`) and a SQL version of the join.
- For bookmarks and notes, store the counting system with the reference, or store the Kufan reference and convert only on display.

Two things to watch: don't round-trip Warsh → Kufan → Warsh, because splits lose which half you were on. Also test 1:1 and a few ayahs after each disputed boundary in the surahs users reported.