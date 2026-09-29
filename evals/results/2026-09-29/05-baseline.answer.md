### FILE answer.md
# Wrong or missing tafsir on Warsh ayahs

(The working directory was empty, so this is based on your description, not your code.)

## What is going wrong

Your tafsir table is keyed by `(surah, ayah)` in **Hafs numbering**, which is the Kufan verse count (6236 ayahs). Your Warsh text is numbered by **its own verse count**, the Madani count (about 6214 ayahs). The two systems agree on the words but not on where verses start and end.

Joining on `(surah, ayah)` therefore assumes the number means the same verse in both systems, and it doesn't. Three things go wrong:

1. **Offset (wrong tafsir).** Al-Fatiha is the clearest case. Hafs counts the basmala as 1:1, and Warsh does not.

   | Verse | Hafs | Warsh |
   |---|---|---|
   | Basmala | 1:1 | not numbered |
   | الحمد لله | 1:2 | 1:1 |
   | ... | ... | ... |
   | اهدنا الصراط المستقيم | 1:6 | 1:5 |
   | صراط الذين أنعمت عليهم | 1:7 (start) | 1:6 |
   | غير المغضوب عليهم ولا الضالين | 1:7 (end) | 1:7 |

   Warsh 1:2 joins to the tafsir of Hafs 1:2, but that is the tafsir of a different verse.
2. **Split or merged verses (wrong tafsir, or none).** In many surahs, one Hafs ayah is two Warsh ayahs, or two Hafs ayahs are one Warsh ayah. Examples are the disconnected letters (Ha-Mim, Ta-Ha, Ya-Sin and similar), which are counted differently, and various mid-surah breaks. From the first difference onward, every later ayah in that surah is shifted by one. That gives a wrong tafsir, or none once the number runs past the end of the Hafs surah.
3. **Missing rows.** A Warsh surah can have a different last ayah number than the Hafs one. Where Warsh has a number Hafs doesn't, the join returns NULL.

The relationship is many-to-many (one Warsh ayah can span several Hafs ayahs, and the reverse). No formula or constant offset fixes it. It needs an explicit mapping table.

## Fix: add a Warsh to Hafs mapping table and join through it

### Schema

```sql
CREATE TABLE ayah_map (
  surah        INTEGER NOT NULL,
  warsh_ayah   INTEGER NOT NULL,
  hafs_ayah    INTEGER NOT NULL,   -- one row per overlapping Hafs ayah
  PRIMARY KEY (surah, warsh_ayah, hafs_ayah)
);
CREATE INDEX ayah_map_hafs ON ayah_map (surah, hafs_ayah);
```

### Query

```sql
SELECT w.surah, w.ayah AS warsh_ayah, w.text,
       t.ayah AS hafs_ayah, t.tafsir_text
FROM   warsh_text w
LEFT JOIN ayah_map m ON m.surah = w.surah AND m.warsh_ayah = w.ayah
LEFT JOIN tafsir   t ON t.surah = m.surah AND t.ayah       = m.hafs_ayah
WHERE  w.surah = :surah
ORDER  BY w.ayah, t.ayah;
```

The application layer should:
- Group by `warsh_ayah`. When a Warsh ayah maps to several Hafs ayahs, show all their tafsir entries, labelled with the Hafs number ("Tafsir of Hafs 7:12-13").
- When a Hafs ayah spans several Warsh ayahs, the same tafsir is correctly shown under each. Say so in the UI.
- Treat "no mapping" (for example the basmala) as an intentional state and don't show it as an error.

### Building the map (offline, once)

Don't hand-write the map, and don't hard-code rules like "Fatiha is +1". Derive it from the two texts, since they share the same words. Align them **word by word** and record which Hafs ayah each Warsh word falls in.

```python
import re, difflib, sqlite3
from collections import defaultdict

# Strip diacritics, tatweel, Quranic marks; unify letter variants that differ
# between Warsh (Maghrib) and Hafs orthography.
_MARKS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ࣓-ࣿ]")
_VARIANTS = str.maketrans({"ٱ": "ا", "أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي",
                           "ی": "ي", "ک": "ك", "ۀ": "ه", "ة": "ه", "ؤ": "و", "ئ": "ي"})

def norm(word: str) -> str:
    return _MARKS.sub("", word).translate(_VARIANTS)

def words_with_ayah(ayahs):
    """ayahs: list of (ayah_no, text) -> parallel lists (normalized words, ayah_no per word)"""
    ws, owner = [], []
    for no, text in ayahs:
        for w in text.split():
            n = norm(w)
            if n:
                ws.append(n)
                owner.append(no)
    return ws, owner

def build_surah_map(warsh_ayahs, hafs_ayahs):
    """Returns {warsh_ayah: sorted set of hafs ayahs it overlaps}."""
    w_words, w_owner = words_with_ayah(warsh_ayahs)
    h_words, h_owner = words_with_ayah(hafs_ayahs)

    # For every Warsh word, find the aligned Hafs word (if any).
    w2h = [None] * len(w_words)
    sm = difflib.SequenceMatcher(a=w_words, b=h_words, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                w2h[i1 + k] = j1 + k
        elif tag == "replace":               # spelling differences: pair up by position
            span_a, span_b = i2 - i1, j2 - j1
            for k in range(span_a):
                w2h[i1 + k] = j1 + min(span_b - 1, k * span_b // span_a)

    result = defaultdict(set)
    for wi, hi in enumerate(w2h):
        if hi is not None:
            result[w_owner[wi]].add(h_owner[hi])
    return result

def build_all(warsh_db, hafs_db, out_db):
    out = sqlite3.connect(out_db)
    out.execute("""CREATE TABLE IF NOT EXISTS ayah_map(
        surah INT, warsh_ayah INT, hafs_ayah INT,
        PRIMARY KEY (surah, warsh_ayah, hafs_ayah))""")
    problems = []
    for surah in range(1, 115):
        warsh = warsh_db.execute(
            "SELECT ayah, text FROM warsh_text WHERE surah=? ORDER BY ayah", (surah,)).fetchall()
        hafs = hafs_db.execute(
            "SELECT ayah, text FROM hafs_text WHERE surah=? ORDER BY ayah", (surah,)).fetchall()
        m = build_surah_map(warsh, hafs)

        # Sanity checks: every Warsh ayah mapped, every Hafs ayah covered
        # (Hafs 1:1 is the basmala, which is legitimately uncovered).
        missing_w = {a for a, _ in warsh} - m.keys()
        covered_h = set().union(*m.values()) if m else set()
        missing_h = {a for a, _ in hafs} - covered_h
        if missing_w or (missing_h - ({1} if surah == 1 else set())):
            problems.append((surah, sorted(missing_w), sorted(missing_h)))

        out.executemany("INSERT OR REPLACE INTO ayah_map VALUES (?,?,?)",
                        [(surah, w, h) for w, hs in m.items() for h in hs])
    out.commit()
    return problems   # review these by hand
```

Notes on the build:
- **Check the output.** Word alignment is heuristic, so review every surah where `problems` is non-empty. Also review every surah where the number of ayahs differs between the two texts, since those are the ones that matter. Confirm at least Fatiha and a few known split points against a printed Warsh mushaf.
- **Or use a published map.** If you have a verified dataset of Warsh and Hafs verse boundaries (for example from a qira'at-aware Quran dataset), load that into `ayah_map` instead. The alignment script is a way to generate or cross-check it.
- **Store the result.** Commit the generated `ayah_map` as data, not code, so it can be audited and fixed line by line.
- **Check the counts.** Test that the number of distinct `(surah, warsh_ayah)` in the map equals your Warsh text row count (about 6214 for the Madani count), and that every Hafs ayah other than 1:1 is covered.
- **Missing tafsir.** After the join, count Warsh ayahs that still have no tafsir. It should be zero, apart from any Hafs ayahs your tafsir source doesn't cover.

### Regression tests

```python
def test_fatiha(db):
    rows = db.execute("SELECT warsh_ayah, hafs_ayah FROM ayah_map WHERE surah=1").fetchall()
    assert (1, 2) in rows          # Warsh 1:1 (الحمد لله) -> Hafs 1:2, not 1:1
    assert (6, 7) in rows and (7, 7) in rows   # Hafs 1:7 covers Warsh 1:6 and 1:7
    assert all(h != 1 for _, h in rows)        # the basmala has no Warsh ayah

def test_no_orphans(db):
    orphans = db.execute("""
      SELECT w.surah, w.ayah FROM warsh_text w
      LEFT JOIN ayah_map m ON m.surah=w.surah AND m.warsh_ayah=w.ayah
      WHERE m.hafs_ayah IS NULL""").fetchall()
    assert orphans == []
```

## Summary

- **Cause:** the join treats Warsh and Hafs verse numbers as identical, but Warsh numbers verses differently. Verses split, merge or shift, and Al-Fatiha's basmala is not verse 1 in Warsh.
- **Fix:** an explicit `(surah, warsh_ayah) to hafs_ayah` many-to-many table, generated by aligning the two texts and then verified. Join tafsir through it and display every overlapping Hafs entry.


### FINAL MESSAGE
I wrote the explanation and fix to `/tmp/eval5-baseline-e8a9c5a7/answer.md`. I haven't run any of the code, and the directory was empty, so it's based on your description and not your actual code.

**Cause:** Warsh uses the Madani verse count (about 6214 ayahs) and your tafsir table uses the Hafs count (6236). Joining on `(surah, ayah)` treats the numbers as the same verse when they aren't.
- **Al-Fatiha:** Hafs counts the basmala as 1:1 and Warsh doesn't. Warsh 1:1 therefore gets the tafsir for the wrong verse, and Hafs 1:7 covers both Warsh 1:6 and 1:7.
- **Other surahs:** verses are split or merged elsewhere, so every later ayah in that surah is off by one. That gives a wrong tafsir, or none when the number runs past the end of the Hafs surah.

**Fix:** add an `ayah_map(surah, warsh_ayah, hafs_ayah)` table with one row per overlapping Hafs ayah. It has to allow many-to-many because one ayah can span several on the other side. Join the Warsh text to the tafsir through it and show every matching tafsir entry.

`answer.md` also has:
- The schema and join query.
- A Python script that builds the map by aligning the two texts word by word.
- Sanity checks and two regression tests.

The alignment is heuristic. Review the surahs it flags and any where the ayah counts differ, and check Fatiha against a printed Warsh mushaf. Or load a verified dataset of verse boundaries into `ayah_map` instead.