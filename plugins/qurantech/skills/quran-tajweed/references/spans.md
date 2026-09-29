# Span data and status detail

Sources: quran-ws/quran-tajweed READMEs and docs, quran.ws/docs/reference/quran-tajweed, /docs/build/tajweed, /offline, /licensing.

## Annotation file
Top-level keys (verified in `@quran.ws/tajwid-annotations@0.1.0`): `corpusVersion` ("0.4.2"), `riwayah` ("hafs-an-asim"), `edition` (`id` "uthmani-hafs", `sha256` "b5d29736...", `ayahCount` 6236), `ruleIds` (164), `spans`.
An ayah without rulings is omitted from `spans`; only `20:1` is. Treat a missing key as no spans.
`@quran.ws/tajwid` `unpack(annotations, corpus, "1:1")` returns full spans: `start`, `end`, `ruleId`, `hukumId`, `categoryId`, `topicId`. `unpack` returns `[]` for an absent ayah.
Check `annotations.corpusVersion === corpus.version` before joining them.

## Topics (ids)
tafkheem-tarqeeq, letter-relations, noon-tanween, meem-sakinah, mushaddadatan, madd, qalqalah. Rules package: 7 topics, 27 categories, 58 ahkam, 182 rules. The site says 127 rules produce spans and 147,255 spans in total; read counts from the file you load, since release and repo versions differ.

## Offline
The offline page lists a v0.4.0 release annotations file (about 1.8 MB) and rules (about 97 KB); latest release is v0.4.3 with assets: annotations JSON, rules JSON, rules schema, playground HTML, SHA256SUMS. The edition file is not a release asset; read it from the repo. Cache annotations tied to the edition digest.

## Digest
SHA-256 over content: each reference and its text in mushaf order, U+0000 between reference and text, U+0001 between entries (site page has the exact code; use `editionDigest`/`assertEdition` rather than reimplement). A mismatch throws `EditionMismatchError`.

## Different edition
`pnpm edition:check <file>` reports normaliser-dependent characters and rule behaviour; `pnpm annotate <edition> <out>` regenerates spans with a new digest (repo scripts). Common differences: precomposed U+0622 vs U+0627+U+0653, sukoon U+06E1 vs U+0652, positional tanween marks, ayah count other than 6,236. Copy edition text exactly; never retype or normalise it.

## Rendering pitfalls (repo docs/rendering.md)
- A browser shapes each element alone, so a colour change splits a word. Fix: ZWJ on both sides of a cut, only when the last base letter before joins forward and the first after joins back (not after ء آ أ ؤ إ ا ة د ذ ر ز و ٱ).
- A span ends on the letter, not its marks. Push every boundary past marks with `clusterEnd`. Waqf signs are not part of a cluster and keep surrounding colour.
- Joiners belong to the drawing only: not in offsets, counts or clipboard. ANSI output adds none.
- React component sets `aria-label` with the ruling on each stretch; colour must never be the only signal.

## Status
stable 162, disabled 18, disputed 2 (site counts; the annotations README says 164 rules, so counts vary by version). Disputed: `qalqalah-kubra.1` (42:2 opening) and `madd-lazim-harfi.1` (ayn of the disjoined letters); the corpus records the objection and leaves the ruling to a qualified reviewer. 12 rules carry `needsReview`. Named gaps: natural madd in disjoined-letter names, qalqalah at mid-ayah stops, madd al-farq, silah kubra, saktah, waqf and ibtida, isti'adha/basmala rulings, al-mutabāʿidayn.
Engine options: `only` (topic, hukum or rule id), `school` ('ibn-al-jazari' and Ibn al-Tahhan both modelled for tafkheem ranks), `includeDisabled`.

## Origin and licence
Port of the system behind tajweed.quranpedia.net, checked over the whole mushaf. CC BY 4.0 for `editions/`, `conformance/`, `docs/`, rule corpus, annotations; MIT for the rest of `packages/`, `python/`, `playground/`, `scripts/`.

## Unverified
- How to map character offsets onto quran-svg or quran-svg-elements shapes: no source documents a bridge; sources only say spans address characters, not printed shapes.
- Whether the site's "Python unpublished" and "npm unpublished" text has been updated; npm 0.1.0 was confirmed directly.
