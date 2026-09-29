# Quran Search

Start with the Quran.ws blocks ([blocks.md](../blocks.md)): whole-word search over the text, and showing hits on a page. Root, lemma, meaning and translation search are outside them; third parties answer those.

## Table of Contents
- [Search Types](#search-types)
- [Full-Text Search with quran-text](#full-text-search-with-quran-text)
- [Showing Hits on a Page](#showing-hits-on-a-page)
- [Root-Based Search](#root-based-search)
- [Semantic Search](#semantic-search)
- [Transliteration Search](#transliteration-search)
- [Pattern Search](#pattern-search)
- [Hybrid Search Example (BAHETH)](#hybrid-search-example-baheth)
- [Building It Yourself: One Elasticsearch Approach](#building-it-yourself-one-elasticsearch-approach)
- [Arabic NLP Tools](#arabic-nlp-tools)
- [Services & APIs](#services--apis)
- [Best Practices](#best-practices)

## Search Types

| Type | Description | Covered by |
|------|-------------|-----------|
| **Full-text** | Words or phrases as printed, typed without marks | **quran-text** |
| **Root-based** | Words sharing an Arabic root | Third party (morphology data; see [irab.md](irab.md)) |
| **Semantic** | Ayahs by meaning | Third party |
| **Transliteration** | Latin input for Arabic text | Your own mapping layer |

## Full-Text Search with quran-text

A user types the plain letters; the mushaf prints vowel marks, hamzat al-wasl and dagger alifs, so the two strings never compare equal. Match on a folded form. The `quran-text` skill and [quran.ws/docs/build/search](https://quran.ws/docs/build/search) give the recipe:

- **One edition at a time.** `Mushaf.hafs()` (or another riwayah's file), then `m.search(text)`. It folds the query, matches whole words in sequence and returns Spans: positions into `m.words`. Highlight by those positions, never by re-finding the string in rendered text.
- **Across riwayat.** `WordIndex.search(word)` takes one folded word and returns each numbered word with every edition's spelling (`forms`). The index is a server or build-time file (about 50 MB), not a phone asset. Numbers are stable across riwayat; join on them.
- **Match keys.** `pointed`, `plain` and `rasm` are matching keys, not display text: show the edition's own `words[]` or `forms["<key>"]`.
- **Normalisation: defer to the Quran.ws search page.** Use the fold the dataset exports (`fold()`), on the query and on the index. Never write your own normaliser, and never search one dataset's index with another dataset's fold: close folds produce confident zeros. Fold the query with the function the index was built with and show the result count, so an empty result is visible.
- **Whole words only.** `quran-text` search has no prefix or substring mode; `quran-engine` has `mode: "prefix"`.
- **Scope.** The page states these blocks carry no root, lemma or translation lookups. For a translation, search the translation's own text and join the hit to the Quran by `surah:ayah`.
- **Counting.** A hit key belongs to its edition; convert with `qiraat-ayah-map` to open it in another count.

## Showing Hits on a Page

- **quran-svg-elements** (Hafs only) and **quran-engine**: the page's sidecar gives every word a `search` form and a `word_key` (`surah:ayah:word`). `page.search()` in the engine returns hits already keyed for highlighting. `word_key` is the address all blocks share, so a hit is also a `quran-text` lookup and a bookmark.
- **quran-svg**: highlight the ayah polygon (`surah`, `ayah` attributes) when a hit lands on an ayah and the edition has no word split.
- The Elements/engine search form and `quran-text`'s fold differed until a September 2026 fix (per the Quran.ws page): pin versions and test one dagger-alif word.

## Root-Based Search

Root search needs morphology data, which no block carries. Use pre-computed root mappings rather than writing an analyser.

- Quranic Arabic Corpus (corpus.quran.com) has word-level morphology including roots (licence: see [irab.md](irab.md)).
- Index roots and lemmas per word using `quran-text` word numbers as the key, so the index survives a riwayah switch.
- Quran Foundation API: search needs separate pre-live permission; its morphology coverage is not confirmed here.

## Semantic Search

Third-party only; the blocks do not search by meaning.

- **Alfanous.ai** is the current Alfanous site (it returned 403 to curl when checked, so test it in a browser).
- **Quran MCP** (`mcp.quran.ai`) describes itself as "Canonical Quran text, translations, and tafsir for AI". Use it to ground an AI agent in source text, not as a confirmed semantic-search engine.
- See the BAHETH example below for a self-hosted hybrid.

## Transliteration Search

For users who cannot type Arabic: map common schemes and informal spellings to Arabic, then fold and search as above. Offer it as a secondary mode.

## Pattern Search

Search by vowel pattern regardless of letters needs the printed marks, so run it over an edition's own `words[]` (waqf marks are combining characters: inspect Unicode scalars). The blocks ship no pattern index. QuranMorphology.com is reported to offer pattern search; unconfirmed here.

## Hybrid Search Example (BAHETH)

BAHETH (`github.com/engsaleh/quran_semantic_search`) is a personal, MIT-licensed project, not an Itqan project. Its `backend/main.py` shows a hybrid retriever:

- **FAISS** `IndexFlatIP` quantizer with an `IndexIVFFlat` index over L2-normalised embeddings.
- **BM25** via `rank-bm25` (`BM25Okapi`), scores normalised by the maximum.
- **Embeddings** set by `MODEL_ID` in that file (default `hkunlp/instructor-large` with a `intfloat/multilingual-e5-large` fallback when checked; check the file for the current model).
- **Adaptive weight:** `alpha = 0.8 if len(q_tokens) < 4 else 0.6`; candidates sort by `alpha * cos + (1 - alpha) * bm25_normalised`. Short queries lean semantic.
- No Elasticsearch: candidates come from FAISS plus BM25 in memory.

Ideas: Arabic stop-word filtering for BM25; show why each result matched.

## Building It Yourself: One Elasticsearch Approach

If a hosted service will not do, here is one experience-based approach (no public source). The ideas port to OpenSearch, Meilisearch, Typesense, SQLite FTS or an in-app index; the terms are Elasticsearch's.

**Index design (per ayah):**
- Multi-field mapping: raw text, Arabic-analyzed, Arabic-*exact* (normalized, unstemmed), plus a marks-stripped `clean_text` in the same three variants.
- Analyzer chain: standard tokenizer + `lowercase`, `decimal_digit`, `arabic_normalization`, `arabic_stop`, `arabic_stemmer`; a second analyzer without stemming for exact matches; an `edge_ngram(3,20)` filter for autocomplete.
- **Index roots and lemmas per ayah** from morphology data ([irab.md](irab.md)). Keep the dataset's `fold()` as the base key, as above.

**Query design: a boost ladder.** `dis_max` (`tie_breaker` ~0.1) over, in descending boost: exact phrase on raw text, phrase on normalized-unstemmed, phrase on stemmed, phrase-prefix for mid-typing.

**The stopword trap:** the analyzer drops Arabic stopwords, which silently breaks phrase queries. Detect dropped terms and switch to a whitespace-analyzed field with `span_near` (in order, slop 0). Let the first term match **و/ف proclitic variants** via `span_or`, so "من يعمل" also finds "وَمَن يَعمَل".

**Fallback ladder:** strict ordered phrase, then loose stemmed match, then a normalized-query retry. Show "no results" only after all three.

**Post-ranking:** re-rank the top hits by match position (starts-with, then contains, then truncated match). Then choose the display order (see Best Practices).

**Batching:** one `_msearch` round trip per screen.

## Arabic NLP Tools

| Tool | Purpose |
|------|---------|
| **CAMeL Tools** (`github.com/CAMeL-Lab/camel_tools`) | Morphological analysis, dialect ID, sentiment |
| **AraBERT** (`github.com/aub-mind/arabert`) | Arabic BERT for text classification |
| **Arabic-Phonetiser** (`github.com/nawarhalabi/Arabic-Phonetiser`) | 68-phoneme analyzer for tajweed sounds |

## Services & APIs

For exact-word search, use `quran-text` first. These cover what it does not.

| Service | Type | Notes |
|---------|------|-------|
| **Kalimat.dev** | Full-text Arabic | Hosted search |
| **Alfanous.ai** | Semantic/root | Current Alfanous site; blocks curl, test in a browser |
| **Quran Foundation API** | Full-text | Separate pre-live permission |
| **Quran MCP** | Text, translation and tafsir for AI | `mcp.quran.ai`; self-described as "Canonical Quran text, translations, and tafsir for AI" |
| **tafsir.app** | Root search | Unconfirmed; verify before relying on it |

## Best Practices

- **Show complete ayahs in results**, not snippets, and highlight the matched words by position.
- **Ordering:** for a lookup by phrase, present hits in mushaf order (surah:ayah), the reading order users expect. If you re-rank by match position for a "best match first" list, label it as ranked and offer a mushaf-order toggle.
- **Show the surah name and ayah number**; accept with-marks and plain input (fold both).
- **Zero results:** show the count, suggest alternatives, and offer root search from a third-party dataset.
- **Reference search** ("2:255", "البقرة 255") should be instant: detect the pattern and navigate.
- **Offline:** build the folded index at install time with the same `fold()` version you ship, and pin the dataset version.
