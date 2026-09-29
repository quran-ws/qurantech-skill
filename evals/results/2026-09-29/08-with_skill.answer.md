### FILE schema.md
# Quran app schema: key decisions

The DDL is in `schema.sql` (PostgreSQL 13+). It covers Hafs and Warsh text, user bookmarks, reading progress and per-ayah notes.

**Status:** I wrote the DDL but have not run it against a database, so treat it as unverified until it loads cleanly.

## 1. An ayah reference is never just `surah:ayah`

Hafs uses Kufan numbering and Warsh uses Last Madinan (`madani-last`). The two differ: Hafs 1:1 (the basmalah) and 1:2 are one ayah in Warsh, and Hafs 1:7 is split into 6 and 7. So `2:5` is ambiguous without context.

Every reference in the schema carries `mushaf_key + counting_system + surah + ayah`. Composite foreign keys enforce two things:
- The counting system matches the mushaf: `(mushaf_key, counting_system) → mushaf`.
- The ayah exists in that edition: `(mushaf_key, surah, ayah) → ayah`.

Counting system ids are the exact ids used by Quran.ws `qiraat-ayah-map` (`kufi`, `madani-first`, `madani-last`, `makki`, `basri`, `dimashqi`). A system is never identified by its ayah total.

## 2. Counting systems and mushafs are data, not an enum

Adding another riwayah means inserting rows, not migrating the schema.

- `mushaf` records `riwayah`, `counting_system`, and `source_hash`, a SHA-256 of the source text. That hash lets you prove which text a stored reference was measured against.
- It keeps two separate count fields, `counting_system_associated_with_qari` and `counting_system_printed`. One is the system the qari is attributed, the other is what a printed edition measures. They can differ, and neither is derived from the other. NULL printed means "unmeasured", not "agrees".
- Totals are not stored. `mushaf_surah_ayah_count` derives ayah counts from the `ayah` rows, because the counts are contested (the First Madinan total is disputed upstream).
- `mushaf_surah.basmalah_counted` is a separate fact from `has_basmalah`. Only Surah 9 lacks a basmalah, but editions differ on whether it is numbered as an ayah in al-Fatihah.
- Page and juz sit on `ayah` per mushaf, because page N is edition-specific.

## 3. Cross-riwayah mapping goes through Kufan (the hub)

`ayah_crosswalk` is loaded from `qiraat-ayah-map` and always has `kufi` on one side. A `CHECK` rejects direct Basri↔Makki rows, and the upstream data has no such mapping either.

- **One row per (source ayah, target ayah) pair.** A split (Kufan 7 → Warsh 6 and 7) or a merge (Warsh 1 → Kufan 1 and 2) is just multiple rows. This avoids assuming the arrays are contiguous ranges and avoids storing arrays in a column.
- **Forward and reverse are separate loads.** They are not inverses: the reverse of a split loses which half you were on, since both halves return Kufan 7. Never "normalise" by a round trip.
- `merges_with_next` is its own column, independent of `status`.
- `mapping_version` pins the data version, since the package is at 0.1.0 and has 246 disputed positions.

## 4. Surviving a riwayah switch: the Kufan anchor range

A user with a Hafs bookmark on 2:255 switches to Warsh. Every user table (`bookmark`, `note`, `reading_position`, `reading_session`) therefore stores two things:

1. **The original reference**, where the user actually made it. It is authoritative and never rewritten.
2. **A Kufan anchor range** `kufi_first..kufi_last`, computed once at write time. It is a range, not a single ayah, because a Warsh ayah can cover two Hafs ayahs.

Switching is then one query (see the bottom of `schema.sql`). It joins `kufi → target` through the crosswalk on `src_ayah BETWEEN kufi_first AND kufi_last` and returns `MIN..MAX` of the target ayahs. The UI shows the range and never silently picks the first ayah.

Why not rewrite the reference on switch? Rewriting is lossy at splits, and the user's data would change when they merely changed a setting. Keeping the original and converting for display is reversible. The anchor is a derived cache, so it can be recomputed from the original whenever the mapping data is updated.

Notes work the same way. A note written under Warsh appears under Hafs wherever the Kufan ranges overlap, and the overlap check is indexed by `(user_id, surah, kufi_first, kufi_last)`.

## 5. Quranic text is stored byte-exact, search text separately

`ayah.text` comes from a verified source (Quran.ws `quran-text`) and is never transformed, truncated or stripped of diacritics. `ayah.text_search` is the stripped or normalised form, used only for search. Notes are the user's own words in `note.body`, so there is no path in this schema that generates or edits Quranic text or tafsir.

## 6. User data

**Bookmarks**
- Optional `word_number` holds a shared cross-riwayah word number for word-level bookmarks. Positions inside a file are file-local, so only the shared number is safe to store.
- A partial unique index prevents duplicate live bookmarks on the same spot. It uses `COALESCE(word_number, 0)` because NULLs are otherwise distinct in unique indexes.
- The same ayah bookmarked in Hafs and Warsh is intentionally two rows, since they are separate references.

**Notes**
- Several notes per ayah are allowed, so a note works like a journal entry rather than a single field.

**Reading progress is two tables with two jobs**
- `reading_position` holds one row per user, the "resume where I left off" pointer. Its `page` is only a cache.
- `reading_session` is an append-only log of ranges read (within one surah each). It supports history, streaks and percent-complete, with completion computed against the derived ayah counts rather than a stored total.
- The two are separate because overwriting a single position row would lose all history.

**Sync**
- Primary keys are UUIDs, so they can be generated on-device offline.
- `updated_at` and `deleted_at` (soft delete) allow simple last-writer-wins sync of bookmarks and notes.

## Not included (deliberately)

- **Translations, tafsir, audio.** They are Hafs-indexed in most sources, so join them through the Kufan anchor. `ayah_from..ayah_to` ranges suit tafsir better than one row per ayah. They belong in their own tables when needed.
- **Users' auth.** `app_user` is a stub, so plug in your identity provider.
- **Word-level text and tajweed layers.** These would be additional layers keyed by shared word number and tied to a `mushaf.source_hash`.

## Open points to verify before shipping

- The upstream `qiraat-ayah-map` package is at 0.1.0. Check the loader against the generated `dist/mappings` files, including odd keys like `"11:82"` in the forward tables.
- Whether Abū ʿAmr-style cases (attributed `basri`, printed `madani-first`) matter for you. They only affect you if you add more riwayat, and then `counting_system_printed` is the value to prefer for what a physical muṣḥaf shows.


### FILE schema.sql
-- Quran app schema: Hafs + Warsh, bookmarks, reading progress, per-ayah notes.
-- Dialect: PostgreSQL 13+. Portable to SQLite with uuid -> TEXT, timestamptz -> TEXT.
-- Design rationale: see schema.md.

BEGIN;

-- ─────────────────────────────────────────────────────────────
-- Reference data (read-only, shipped with the app / loaded from sources)
-- ─────────────────────────────────────────────────────────────

-- Ayah counting systems (madhahib of 'add al-ay). Ids exactly as in
-- Quran.ws qiraat-ayah-map. No totals are stored: they are disputed
-- (First Madinan) and derivable from the ayah table.
CREATE TABLE counting_system (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);
INSERT INTO counting_system (id, name) VALUES
    ('kufi',         'Kufan'),          -- the hub; Hafs
    ('madani-first', 'First Madinan'),
    ('madani-last',  'Last Madinan'),   -- Warsh (Qalun)
    ('makki',        'Makki'),
    ('basri',        'Basri'),
    ('dimashqi',     'Dimashqi');

CREATE TABLE riwayah (
    key  TEXT PRIMARY KEY,             -- 'hafs', 'warsh', ...
    name TEXT NOT NULL
);

-- One row per installed edition of the text.
CREATE TABLE mushaf (
    key                                 TEXT PRIMARY KEY,   -- 'hafs', 'warsh'
    riwayah                             TEXT NOT NULL REFERENCES riwayah(key),
    counting_system                     TEXT NOT NULL REFERENCES counting_system(id),
    -- What the qari is attributed vs. what this printed edition measures.
    -- Never derive one from the other; NULL printed = unmeasured, not "agrees".
    counting_system_associated_with_qari TEXT REFERENCES counting_system(id),
    counting_system_printed             TEXT REFERENCES counting_system(id),
    edition                             TEXT NOT NULL,
    version                             TEXT NOT NULL,
    source_hash                         TEXT NOT NULL,      -- SHA-256 of the source text file
    UNIQUE (key, counting_system)       -- target for composite FKs below
);

CREATE TABLE surah (
    number           INTEGER PRIMARY KEY CHECK (number BETWEEN 1 AND 114),
    name_arabic      TEXT NOT NULL,
    name_transliterated TEXT NOT NULL,
    revelation_type  TEXT CHECK (revelation_type IN ('makki', 'madani')),
    revelation_order INTEGER
);

-- Per-edition facts about a surah (ayah count is derived, never stored).
CREATE TABLE mushaf_surah (
    mushaf_key       TEXT    NOT NULL REFERENCES mushaf(key),
    surah            INTEGER NOT NULL REFERENCES surah(number),
    has_basmalah     BOOLEAN NOT NULL,
    basmalah_counted BOOLEAN NOT NULL,   -- numbered as an ayah in this edition?
    start_page       INTEGER,            -- edition-specific
    PRIMARY KEY (mushaf_key, surah)
);

-- Ayah text per edition, numbered in that edition's counting system.
CREATE TABLE ayah (
    mushaf_key  TEXT    NOT NULL REFERENCES mushaf(key),
    surah       INTEGER NOT NULL REFERENCES surah(number),
    ayah        INTEGER NOT NULL CHECK (ayah >= 1),
    text        TEXT    NOT NULL,   -- byte-exact from the verified source; never normalised
    text_search TEXT    NOT NULL,   -- stripped form, for search only
    page        INTEGER,            -- edition-specific
    juz         INTEGER,
    PRIMARY KEY (mushaf_key, surah, ayah)
);
CREATE INDEX ayah_page_idx ON ayah (mushaf_key, page);

-- Crosswalk between counting systems, routed through kufi (the hub).
-- One row per (source ayah, target ayah) pair, so splits and merges are
-- ordinary multi-row results with no range assumptions. Forward and reverse
-- are separate loads because they are NOT inverses (reverse of a split is lossy).
CREATE TABLE ayah_crosswalk (
    src_system       TEXT    NOT NULL REFERENCES counting_system(id),
    dst_system       TEXT    NOT NULL REFERENCES counting_system(id),
    surah            INTEGER NOT NULL REFERENCES surah(number),
    src_ayah         INTEGER NOT NULL,
    dst_ayah         INTEGER NOT NULL,
    status           TEXT    NOT NULL
        CHECK (status IN ('mapped', 'merged', 'split', 'covers_multiple')),
    merges_with_next BOOLEAN NOT NULL DEFAULT FALSE,   -- independent of status
    mapping_version  TEXT    NOT NULL,                 -- pinned qiraat-ayah-map version
    PRIMARY KEY (src_system, dst_system, surah, src_ayah, dst_ayah),
    CHECK ((src_system = 'kufi') <> (dst_system = 'kufi'))  -- always via the hub
);
CREATE INDEX ayah_crosswalk_dst_idx
    ON ayah_crosswalk (dst_system, src_system, surah, dst_ayah);

-- ─────────────────────────────────────────────────────────────
-- User data
-- ─────────────────────────────────────────────────────────────

CREATE TABLE app_user (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Every user reference below has the same shape ("ayah ref"):
--   mushaf_key + counting_system + surah + ayah   = where the user made it
--   kufi_first..kufi_last                          = Kufan anchor range, computed
--                                                    at write time, used to follow
--                                                    the user across riwayat
-- The composite FKs guarantee the mushaf and the counting system agree, and
-- that the ayah exists in that edition.

CREATE TABLE bookmark (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),   -- client-generated OK (offline sync)
    user_id         UUID    NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    mushaf_key      TEXT    NOT NULL,
    counting_system TEXT    NOT NULL,
    surah           INTEGER NOT NULL,
    ayah            INTEGER NOT NULL,
    word_number     INTEGER,               -- optional, shared cross-riwayah word number
    kufi_first      INTEGER NOT NULL,
    kufi_last       INTEGER NOT NULL,
    label           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,           -- soft delete for sync
    FOREIGN KEY (mushaf_key, counting_system) REFERENCES mushaf (key, counting_system),
    FOREIGN KEY (mushaf_key, surah, ayah)     REFERENCES ayah (mushaf_key, surah, ayah),
    CHECK (kufi_first <= kufi_last)
);
CREATE UNIQUE INDEX bookmark_unique_idx
    ON bookmark (user_id, mushaf_key, surah, ayah, COALESCE(word_number, 0))
    WHERE deleted_at IS NULL;
CREATE INDEX bookmark_anchor_idx ON bookmark (user_id, surah, kufi_first, kufi_last);

CREATE TABLE note (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID    NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    mushaf_key      TEXT    NOT NULL,
    counting_system TEXT    NOT NULL,
    surah           INTEGER NOT NULL,
    ayah            INTEGER NOT NULL,
    kufi_first      INTEGER NOT NULL,
    kufi_last       INTEGER NOT NULL,
    body            TEXT    NOT NULL,      -- the user's own words, plain text
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    FOREIGN KEY (mushaf_key, counting_system) REFERENCES mushaf (key, counting_system),
    FOREIGN KEY (mushaf_key, surah, ayah)     REFERENCES ayah (mushaf_key, surah, ayah),
    CHECK (kufi_first <= kufi_last)
);
-- Several notes per ayah are allowed (a journal, not a single field).
CREATE INDEX note_ayah_idx   ON note (user_id, mushaf_key, surah, ayah) WHERE deleted_at IS NULL;
CREATE INDEX note_anchor_idx ON note (user_id, surah, kufi_first, kufi_last) WHERE deleted_at IS NULL;

-- "Where I am": exactly one row per user.
CREATE TABLE reading_position (
    user_id         UUID PRIMARY KEY REFERENCES app_user(id) ON DELETE CASCADE,
    mushaf_key      TEXT    NOT NULL,
    counting_system TEXT    NOT NULL,
    surah           INTEGER NOT NULL,
    ayah            INTEGER NOT NULL,
    kufi_first      INTEGER NOT NULL,
    kufi_last       INTEGER NOT NULL,
    page            INTEGER,               -- cache; page N differs per mushaf
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (mushaf_key, counting_system) REFERENCES mushaf (key, counting_system),
    FOREIGN KEY (mushaf_key, surah, ayah)     REFERENCES ayah (mushaf_key, surah, ayah),
    CHECK (kufi_first <= kufi_last)
);

-- Append-only log of what was read: powers history, streaks, % complete.
-- A range lives inside one surah; a span across surahs is several rows.
CREATE TABLE reading_session (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID    NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    mushaf_key      TEXT    NOT NULL,
    counting_system TEXT    NOT NULL,
    surah           INTEGER NOT NULL,
    ayah_from       INTEGER NOT NULL,
    ayah_to         INTEGER NOT NULL,
    kufi_first      INTEGER NOT NULL,
    kufi_last       INTEGER NOT NULL,
    read_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (mushaf_key, counting_system) REFERENCES mushaf (key, counting_system),
    FOREIGN KEY (mushaf_key, surah, ayah_from) REFERENCES ayah (mushaf_key, surah, ayah),
    FOREIGN KEY (mushaf_key, surah, ayah_to)   REFERENCES ayah (mushaf_key, surah, ayah),
    CHECK (ayah_from <= ayah_to AND kufi_first <= kufi_last)
);
CREATE INDEX reading_session_user_idx ON reading_session (user_id, read_at DESC);
CREATE INDEX reading_session_anchor_idx ON reading_session (user_id, surah, kufi_first, kufi_last);

-- ─────────────────────────────────────────────────────────────
-- Views
-- ─────────────────────────────────────────────────────────────

-- Ayah counts are derived, never hardcoded.
CREATE VIEW mushaf_surah_ayah_count AS
SELECT mushaf_key, surah, COUNT(*) AS ayah_count
FROM ayah
GROUP BY mushaf_key, surah;

-- Re-express any user reference in another counting system (the riwayah-switch
-- query). Returns the full span of target ayahs; callers show a range, never
-- just one. The same pattern works for note, reading_position and
-- reading_session. Parameters: :target_system, :user.
--
--   SELECT b.id, b.surah, MIN(x.dst_ayah) AS ayah_first, MAX(x.dst_ayah) AS ayah_last
--   FROM bookmark b
--   JOIN ayah_crosswalk x
--     ON x.src_system = 'kufi' AND x.dst_system = :target_system
--    AND x.surah = b.surah
--    AND x.src_ayah BETWEEN b.kufi_first AND b.kufi_last
--   WHERE b.user_id = :user AND b.deleted_at IS NULL
--   GROUP BY b.id, b.surah;
--
-- (If :target_system = 'kufi' skip the join and use kufi_first..kufi_last.)

COMMIT;


### FINAL MESSAGE
I've written the schema and the explanation, but I haven't run the SQL against a database, so it may not load cleanly yet. I tried to check whether Postgres is installed, but that command was blocked.

- **`schema.sql`** (PostgreSQL 13+):
  - Reference tables: counting systems, riwayat, mushafs, surahs and ayah text.
  - A crosswalk table that maps between counting systems through Kufan (Hafs numbering), which handles splits and merges.
  - User tables for bookmarks, notes, the current reading position and a reading-session log.
- **`schema.md`** covers the key decisions. The main ones:
  - **References:** every ayah reference carries its mushaf, counting system, surah and ayah, never just `surah:ayah`. Hafs and Warsh number ayahs differently, for example Hafs 1:1–2 is one ayah in Warsh.
  - **Riwayah switch:** user data keeps its original reference and also a computed Kufan range. Switching riwayah converts that range for display and never rewrites the original.
  - **Text integrity:** Quranic text is stored exactly as received, with a separate stripped copy for search only.
  - **Counts:** ayah counts are derived from the data, not stored.

The Warsh/Hafs mapping data comes from the upstream `qiraat-ayah-map` package, which is at version 0.1.0 with disputed positions. I haven't checked the loader against its generated files.

Files are in `/tmp/eval8-with_skill-uc7yi1mu`:
- `schema.sql`
- `schema.md`