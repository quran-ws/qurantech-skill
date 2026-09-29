# I'rab (Grammatical Analysis)

## Table of Contents
- [Overview](#overview)
- [What the Blocks Give You](#what-the-blocks-give-you)
- [Three Kinds of I'rab Data](#three-kinds-of-irab-data)
- [Data Sources & Licenses](#data-sources--licenses)
- [The Token Alignment Problem](#the-token-alignment-problem)
- [Morphological Features](#morphological-features)
- [Use Cases in Quran Apps](#use-cases-in-quran-apps)
- [Design Rules](#design-rules)
- [Linguistic Adab (House Convention)](#linguistic-adab-house-convention)
- [Best Practices](#best-practices)

## Overview

I'rab (إعراب) is the grammatical analysis of Quranic Arabic — identifying each word's syntactic role and case markers. Essential for educational apps and Arabic learning tools, and (via roots/lemmas) a force multiplier for search.

## What the Blocks Give You

I'rab data itself is outside the Quran.ws blocks ([blocks.md](../blocks.md)); take it from the sources below. The blocks give you the join and the display:

- **quran-text** numbers every word (77,434), and the same word carries the same number in every riwayah. Key any word-level grammar layer (morphology, syntax, i'rab notes) on that number and it survives a riwayah switch. Show the edition's own spelling (`forms["<key>"]`) beside the grammar.
- **quran-svg-elements** (Hafs only) shows grammar per word on a printed page: `g.word[data-word-key]` is `surah:ayah:word`, which equals `quran-text`'s `m.word(surah, ayah, index)`. Elements has 77,432 words against 77,434 in quran-text, so join by key and spot-check.
- Join on keys, never strings.

## Three Kinds of I'rab Data

Serious i'rab features combine three distinct layers — don't treat them as one:

| Layer | What it is | Granularity |
|-------|-----------|-------------|
| **Classical i'rab books** (كتب الإعراب) | Scholarly prose analyses | Per ayah, prose |
| **Morphology** (صرف) | Word segmentation: prefix/stem/suffix with POS, root, lemma, features | Per word segment |
| **Syntax** (نحو) | Dependency treebank: grammatical relations between words | Per token/relation |

Offer three views: books, a word-by-word morphology table, and a dependency tree split at the treebank's own sentence boundaries.

## Data Sources & Licenses

| Source | Content | License |
|--------|---------|---------|
| **Quranic Arabic Corpus** (corpus.quran.com) | Morphology of every word; its dependency treebank is partial (about 40% per the Extended Treebank paper) | **GNU GPL v3** (corpus.quran.com/license.jsp); the treebank has no separate licence. Attribution required |
| **Extended Quranic Treebank** | Complete dependency treebank (CoNLL-X); the complete-syntax option | **CC BY 4.0**. Mendeley Data DOI 10.17632/rk96pn66m4.1; paper PMC12361616 |
| **mustafa0x/quran-morphology** | Arabized fork of the corpus | No licence file in the repo: GPL is inherited from upstream, not declared. Ask before redistributing |
| **QuranPedia API** | `e3rab`, `morphology`, `syntax` services | Verify against the live API and preserve any licence blocks it returns; see [quranpedia-api.md](../sources/quranpedia-api.md) |

Never implement Arabic morphological analysis from scratch: the corpus already exists. The corpus tagset is documented at corpus.quran.com/documentation/tagset.jsp.

## The Token Alignment Problem

The corpus tokenizes **Uthmani** text (يَٰٓأَيُّهَا as one token) while your app's text may spell or split differently, so word sequences differ in both spelling and count — naive position matching mis-assigns grammar to words.

If your text is quran-text, align to its numbered words. Otherwise solve it **once at import time** with a global sequence alignment (Needleman–Wunsch works, allowing 1↔2 merges), store the aligned result, and keep any corrections to upstream data in a separate reviewed file so future upstream fixes are detected instead of silently double-applied.

## Morphological Features

| Feature | Values | Example |
|---------|--------|---------|
| **Part of speech** | noun, verb, particle, pronoun, etc. (QAC tagset, link above) | كِتَابٌ → noun |
| **Root** | 3–4 letter root | كِتَابٌ → ك-ت-ب |
| **Pattern (wazn)** | General grammar; no QAC tagset counterpart | كِتَابٌ → فِعَال |
| **Case** | مرفوع / منصوب / مجرور | |
| **State** | definite, indefinite, construct | |
| **Person / Gender / Number** | 1st–3rd / masc, fem / sg, dual, pl | |
| **Verb form** | I–X | |
| **Voice / Mood** | active, passive / indicative, subjunctive, jussive, imperative | |

## Use Cases in Quran Apps

- **Word-by-word grammar view** — tap a word → segments, POS, root, case. Color-code by POS.
- **Root & lemma exploration** — navigate to all words sharing a root/lemma. Key lemma pages on the unvowelled form but keep homograph lexemes apart.
- **Grammar search** — "all form-II verbs", "all words from ر-ح-م" — index roots/lemmas per ayah ([search.md](search.md)).
- **Dependency tree display** — per treebank sentence.
- **Derived features** — root/lemma indexes, collocation views, grammar lessons and drill questions fall out of the same tables.

## Design Rules

- **Words, not counts.** Show the words filling a relation, not frequency tables (dominated by repeated formulas like the basmala).
- **Suppress pronoun subjects in aggregates** (noise), and state how many.
- **Drill questions must be answerable from the ayah itself** — a valid answer is another word in the ayah, not a relation label.
- **Evidence, not verdicts** on contested analyses — present the grammar, let scholars rule.
- **Report data gaps honestly** — label missing/cross-ayah relations instead of guessing.

## Linguistic Adab (House Convention)

These rules are a house convention, scholar-dependent: **scholar review** before shipping. Grammar terminology for the Quran carries its own adab. Apply it as a presentation layer over imported data (never mutate the source), and keep judgment calls in human-reviewed data files, not runtime inference:

- Passive: **«مبنيٌّ لما لم يُسمَّ فاعلُه»**, not «مبني للمجهول».
- لفظ الجلالة as object: **«منصوبٌ على التعظيم»**.
- Imperatives addressed to Allah are **دعاء, not أمر**; لا before them is «حرف دعاء».
- **Never label a Quranic particle «زائد»** — use «صلة» or «تأكيد».
- **Don't display a root for لفظ الجلالة** (house convention: derivation is disputed; scholar review); handle words like «رب» location-aware (divine in most contexts, human master in a few).

See [adab.md](../concepts/adab.md) for general adab rules.

## Best Practices

- **Use pre-computed data** and honor its licenses (GPL v3 for the corpus, CC BY 4.0 for the Extended Treebank).
- **I'rab is educational, not core reading**: keep it optional.
- **Display terms in Arabic** (فاعل, مفعول به…) with optional English equivalents.
- **Note scholarly disagreement** where multiple parsings exist.
