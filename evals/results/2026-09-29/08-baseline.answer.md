### FILE schema.md
# Quran App Schema – Design Notes

Target: PostgreSQL 14+. DDL is in `schema.sql`.

## 1. Ayahs are stored per riwaya

Hafs and Warsh differ in more than diacritics: verse *numbering* differs
(different verse-split conventions, so surahs have different ayah counts, and
some verses are split or merged), and the text differs in places. Modelling a
single `ayahs` table keyed by `(surah, ayah)` with a text column per riwaya
would break the moment numbering diverges.

So `ayahs` has one row per **(riwaya, surah, ayah_number)**, with its own text.
`surah_riwaya` holds the per-riwaya ayah count, and a composite FK stops an
ayah from existing in a riwaya/surah combination that isn't declared. Adding a
third riwaya (Qalun, Duri…) is just new rows, no schema change.

`surahs` (114 rows) stays riwaya-independent: names and revelation type are shared.

## 2. Layout is separate from text (`mushafs`, `ayah_layout`)

Pages, juz and hizb belong to a *printed layout*, not to a riwaya. Hafs uses the
604-page Madinah layout; Warsh mushafs have their own pagination. `ayah_layout`
maps ayah → page range/juz/hizb per mushaf. It stores `page_start`/`page_end`
because an ayah can straddle a page break. A riwaya can have multiple mushafs.

## 3. Cross-riwaya concordance (`ayah_concordance`)

Users may switch riwaya, and their bookmarks/notes shouldn't vanish. Because
boundaries can split or merge, the mapping is **many-to-many** with a
`relation` tag (`same`, `split`, `merge`, `partial`). Rows are stored in both
directions so "translate this ayah to the other riwaya" is one indexed lookup.
It's reference data, generated once during content import.

## 4. User data points at `ayahs.id`, not (surah, ayah)

Bookmarks and notes reference the riwaya-specific `ayah_id`. This is exact
(a note on Warsh 2:1 stays on that verse) and gives a plain integer FK. The
riwaya is implied by the ayah, so it isn't duplicated. When the user views
another riwaya, the app follows the concordance to show or offer the
corresponding items. Notes are personal commentary on a particular verse's text,
so they are deliberately not silently rewritten on switching.

- **Bookmarks**: `UNIQUE (user_id, ayah_id)`; optional folder and label.
  Folders are a separate table so they can be renamed/coloured once.
- **Notes**: separate from bookmarks (a note doesn't imply a bookmark and vice
  versa). Multiple notes per ayah are allowed; partial index on live rows.
- Both use UUID keys and `updated_at` + `deleted_at` soft deletes so mobile
  clients can create offline and sync deltas without ID collisions or losing
  deletions.

## 5. Reading progress is three things

Different questions need different shapes, so they are not crammed into one table:

- `reading_position` – the "continue reading" pointer; one row per
  (user, riwaya), upserted often, tiny.
- `ayah_read` – set of ayahs read with first/last/count; powers % complete and
  khatm progress with a simple `COUNT(*)` against `surah_riwaya` totals.
- `reading_sessions` – append-only log for history, time spent and streaks.

Progress is tracked per riwaya implicitly (through the ayah), so completing
Hafs doesn't mark Warsh complete. Completion across riwayat can be derived
through the concordance if wanted.

## 6. Other decisions

- Two text columns: `text_uthmani` for display and `text_search` (normalized,
  no diacritics/variant letters) with a GIN full-text index, since Arabic search
  should ignore tashkeel.
- Integer identity keys for static content (compact, joins fast); UUIDs for
  user-authored rows.
- `ON DELETE CASCADE` from `users` so account deletion removes all personal data.
- Translations/tafsir/audio are out of scope; they would hang off `ayahs.id`
  in their own tables.

## Known trade-offs

- Switching riwaya relies on the concordance being correct; its quality depends
  on the import data, which needs manual review for split/merge verses.
- Bookmarks are not shared across riwayat automatically; a user with both will
  have separate rows (intended, but the UI must handle it).


### FILE schema.sql
-- Quran app schema (PostgreSQL 14+)

-- ---------- Reference content (read-only at runtime) ----------

CREATE TABLE riwayat (
    id          SMALLINT PRIMARY KEY,
    code        TEXT NOT NULL UNIQUE,          -- 'hafs', 'warsh'
    name_en     TEXT NOT NULL,
    name_ar     TEXT NOT NULL,
    reader      TEXT NOT NULL                  -- 'Asim' / 'Nafi'
);

-- A physical/printed layout (pagination, juz/hizb marks). Riwaya can have several.
CREATE TABLE mushafs (
    id          SMALLINT PRIMARY KEY,
    riwaya_id   SMALLINT NOT NULL REFERENCES riwayat(id),
    code        TEXT NOT NULL UNIQUE,          -- 'madinah_hafs_604', 'warsh_maghrib'
    name        TEXT NOT NULL,
    page_count  SMALLINT NOT NULL
);

-- Riwaya-independent surah identity (114 rows).
CREATE TABLE surahs (
    id          SMALLINT PRIMARY KEY CHECK (id BETWEEN 1 AND 114),
    name_ar     TEXT NOT NULL,
    name_en     TEXT NOT NULL,
    revelation  TEXT NOT NULL CHECK (revelation IN ('meccan','medinan'))
);

-- Ayah count (and numbering conventions) differ per riwaya.
CREATE TABLE surah_riwaya (
    surah_id    SMALLINT NOT NULL REFERENCES surahs(id),
    riwaya_id   SMALLINT NOT NULL REFERENCES riwayat(id),
    ayah_count  SMALLINT NOT NULL,
    PRIMARY KEY (surah_id, riwaya_id)
);

-- One row per ayah PER RIWAYA. Numbering and text can differ.
CREATE TABLE ayahs (
    id            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    riwaya_id     SMALLINT NOT NULL REFERENCES riwayat(id),
    surah_id      SMALLINT NOT NULL REFERENCES surahs(id),
    ayah_number   SMALLINT NOT NULL CHECK (ayah_number >= 1),
    text_uthmani  TEXT NOT NULL,               -- with tashkeel/rasm of that riwaya
    text_search   TEXT NOT NULL,               -- normalized, no diacritics
    UNIQUE (riwaya_id, surah_id, ayah_number),
    FOREIGN KEY (surah_id, riwaya_id) REFERENCES surah_riwaya(surah_id, riwaya_id)
);
CREATE INDEX ayahs_search_idx ON ayahs USING gin (to_tsvector('simple', text_search));

-- Page/juz/hizb placement, per mushaf. An ayah may start on one page and end on the next.
CREATE TABLE ayah_layout (
    mushaf_id     SMALLINT NOT NULL REFERENCES mushafs(id),
    ayah_id       INTEGER  NOT NULL REFERENCES ayahs(id),
    page_start    SMALLINT NOT NULL,
    page_end      SMALLINT NOT NULL,
    juz           SMALLINT NOT NULL CHECK (juz BETWEEN 1 AND 30),
    hizb_quarter  SMALLINT NOT NULL CHECK (hizb_quarter BETWEEN 1 AND 240),
    PRIMARY KEY (mushaf_id, ayah_id),
    CHECK (page_end >= page_start)
);
CREATE INDEX ayah_layout_page_idx ON ayah_layout (mushaf_id, page_start);

-- Cross-riwaya concordance. Verse boundaries differ (splits/merges), so this is
-- many-to-many. Stored in BOTH directions so lookups are a single indexed join.
CREATE TABLE ayah_concordance (
    from_ayah_id  INTEGER NOT NULL REFERENCES ayahs(id),
    to_ayah_id    INTEGER NOT NULL REFERENCES ayahs(id),
    relation      TEXT NOT NULL CHECK (relation IN ('same','split','merge','partial')),
    PRIMARY KEY (from_ayah_id, to_ayah_id),
    CHECK (from_ayah_id <> to_ayah_id)
);
CREATE INDEX ayah_concordance_to_idx ON ayah_concordance (to_ayah_id);

-- ---------- User data ----------

CREATE TABLE users (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email                 TEXT UNIQUE,
    display_name          TEXT,
    preferred_riwaya_id   SMALLINT NOT NULL REFERENCES riwayat(id),
    preferred_mushaf_id   SMALLINT REFERENCES mushafs(id),
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE bookmark_folders (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    color       TEXT,
    UNIQUE (user_id, name)
);

CREATE TABLE bookmarks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ayah_id     INTEGER NOT NULL REFERENCES ayahs(id),
    folder_id   UUID REFERENCES bookmark_folders(id) ON DELETE SET NULL,
    label       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ,                   -- soft delete for device sync
    UNIQUE (user_id, ayah_id)
);
CREATE INDEX bookmarks_user_idx ON bookmarks (user_id, updated_at) ;

CREATE TABLE ayah_notes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ayah_id     INTEGER NOT NULL REFERENCES ayahs(id),
    body        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);
CREATE INDEX ayah_notes_user_ayah_idx ON ayah_notes (user_id, ayah_id) WHERE deleted_at IS NULL;

-- "Continue reading" pointer: exactly one per user per riwaya.
CREATE TABLE reading_position (
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    riwaya_id   SMALLINT NOT NULL REFERENCES riwayat(id),
    ayah_id     INTEGER NOT NULL,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, riwaya_id),
    FOREIGN KEY (ayah_id) REFERENCES ayahs(id)
);

-- Which ayahs a user has read (drives % complete, khatm, streaks).
CREATE TABLE ayah_read (
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ayah_id     INTEGER NOT NULL REFERENCES ayahs(id),
    first_read  TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_read   TIMESTAMPTZ NOT NULL DEFAULT now(),
    read_count  INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (user_id, ayah_id)
);

-- Append-only session log for history and daily streaks.
CREATE TABLE reading_sessions (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    riwaya_id       SMALLINT NOT NULL REFERENCES riwayat(id),
    start_ayah_id   INTEGER NOT NULL REFERENCES ayahs(id),
    end_ayah_id     INTEGER NOT NULL REFERENCES ayahs(id),
    started_at      TIMESTAMPTZ NOT NULL,
    duration_sec    INTEGER NOT NULL CHECK (duration_sec >= 0)
);
CREATE INDEX reading_sessions_user_idx ON reading_sessions (user_id, started_at DESC);


### FINAL MESSAGE
I wrote the schema to `schema.sql` (PostgreSQL 14+) and the explanation to `schema.md`. I haven't run the SQL against a database.

The main decisions:

- **Ayahs are stored per riwaya.** There is one row for each riwaya, surah and ayah number, because Hafs and Warsh differ in verse numbering, ayah counts and text. A per-riwaya `surah_riwaya` table holds the ayah counts. A third riwaya is just new rows.
- **Layout is separate from text.** Pages, juz and hizb sit in `mushafs` and `ayah_layout`, since pagination belongs to a printed edition rather than a riwaya. An ayah can span two pages.
- **A concordance maps ayahs between riwayat.** It is many-to-many, with relations for same, split, merge and partial, because verse boundaries differ. Rows are stored in both directions so a lookup is one indexed join.
- **User data references the specific ayah row.** Bookmarks and notes point at `ayahs.id`, so a Warsh note stays on that Warsh verse. Bookmarks have optional folders. Notes are separate and can be several per ayah. User-authored rows use UUID keys and soft deletes so offline devices can sync.
- **Reading progress is three tables.** `reading_position` is the "continue reading" pointer, `ayah_read` gives completion percentage, and `reading_sessions` is a history log for streaks.

Bookmarks and notes are not carried across riwayat automatically. A user who reads both will have separate rows, and the app has to use the concordance to show or offer the matching items. The concordance data itself needs manual review for split and merge verses when it is imported.

Translations, tafsir and audio are left out; they would attach to `ayahs.id` in their own tables.