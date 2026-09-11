# QuranTech

Domain knowledge for the AI coding agent that is about to write your Qurʾān
feature. Nineteen reference files and a short set of non-negotiable rules,
loaded by the agent when the task needs them. It ships no code into your
application, changes nothing at runtime, and is not in your dependency graph.

| Repository | Version | References | Ships |
|---|---|---|---|
| [`quran-ws/qurantech-skill`](https://github.com/quran-ws/qurantech-skill) | `1.0.0` in the manifest — no tag or release | 19 files, ~21,500 words | An Agent Skill. No runtime code |

> **Experimental, and the label is doing real work.** The content comes from
> production Qurʾān platforms, open datasets and the developer community, but
> coverage is uneven, recommendations about APIs and datasets age, and the
> benchmark suite is three prompts (`evals/evals.json`). Treat it as a
> knowledgeable colleague, not a fatwa: verify anything touching Islamic content
> with a qualified scholar, and review its technical output like any other code.

## What it provides

Building Qurʾān apps has traps that generic coding knowledge walks straight
into: hard-coding 6,236 ayat (the count differs between readings), matching
verses across editions by number (they merge and split), rendering Uthmani
script in a system font (the glyphs break), Unicode-normalising the text (it
destroys it), generating tafsīr — scriptural commentary — with a language model.
This skill encodes the knowledge that prevents that.

- **A lean entry point.** `SKILL.md` carries the triggers, an interview
  workflow, the mandatory rules and an index; the agent loads a reference file
  only when the task calls for it.
- **Nineteen references**, grouped as data and sources, text and display,
  qirāʾāt, audio, scholarly content, features, engineering, and adab (the
  etiquette owed to the text).
- **An interview before an architecture.** For a new project the agent is told
  to ask what you are building, the platform, which
  [qirāʾah](https://quran.ws/docs/concepts/glossary/#qiraah) — which transmitted
  reading of the Qurʾān — which features, whether it must work offline, and
  which data sources, before it recommends anything. That is the decision that is
  expensive to reverse.
- **Rules it will not trade away.** From `references/adab.md`, marked mandatory:
  never truncate an ayah mid-text; never strip diacritical marks; verified text
  sources only, never typed by hand; Qurʾānic fonts, not generic Arabic ones;
  never log Qurʾānic text — log the reference; never use it as test data or
  placeholder text; label translations as translations; never auto-play audio
  without user intent.
- **Eleven engineering principles**, including the one this project repeats
  most: never hard-code an ayah count; derive it from the edition's metadata.
- **Technology-agnostic.** Patterns rather than frameworks — Flutter, Swift,
  Kotlin, React, Laravel or anything else.

## Use it when you need

- An AI agent to write code that touches Qurʾānic text, recitation or Qurʾān
  data, and to already know what this domain punishes.
- The domain traps encoded rather than rediscovered one production bug at a time.
- Rules for handling sacred text that are specific enough to review a pull
  request against.

## Not for

| You want | Use |
|---|---|
| Verified Qurʾānic text, in seven riwāyāt, with word numbering | [Quran Text](https://github.com/quran-ws/quran-text) |
| Printed pages as vectors, with an addressable ayah layer | [Quran SVG](https://github.com/quran-ws/quran-svg) |
| The word and mark shapes of a split muṣḥaf | [Quran SVG Elements](https://github.com/quran-ws/quran-svg-elements) |
| Those pages rendered fast inside a mobile app | [Quran Engine](https://github.com/quran-ws/quran-engine) |
| [Tajwīd](https://quran.ws/docs/concepts/glossary/#tajweed) rules as spans over the text | [Quran Tajweed](https://github.com/quran-ws/quran-tajweed) |
| Translation between ayah-numbering systems | [Qiraat Ayah Map](https://github.com/quran-ws/qiraat-ayah-map) |
| A runtime dependency of any kind | None of the above — QuranTech ships no code |

And it is not verification. A skill changes what the agent knows; it does not
check what the agent produced. A dropped diacritic does not throw — it renders as
slightly wrong Qurʾān forever. Keep the integrity check in CI, comparing stored
text byte-for-byte against the published source. The skill tells the agent to do
this; it cannot do it for you.

## See it work

- **[quran.ws/blocks/qurantech/](https://quran.ws/blocks/qurantech/)** — what it
  covers and the traps it prevents.
- **[quran.ws/demo/](https://quran.ws/demo/)** — switch the QuranTech layer on and
  it surfaces the relevant trap for whichever other layers are running.
- **[quran.ws/docs/reference/qurantech/](https://quran.ws/docs/reference/qurantech/)**
  — what ships, the four install routes, and the limits below in full.

## Provenance

| | |
|---|---|
| Entry point | `plugins/qurantech/skills/qurantech/SKILL.md` |
| References | `plugins/qurantech/skills/qurantech/references/*.md` — 19 files |
| Packaged skill | `dist/qurantech.skill`, a 73,515-byte zip on the default branch |
| Evals | `evals/evals.json` — three prompts with assertions |
| Version | `1.0.0` in both `plugin.json` files. There are no releases and no tags |

There is nothing to pin. "The version you have" means "the state of the default
branch on the day you installed it", and neither the packaged file nor the
directory has a published digest to check it against. If you need a fixed
version today, record the commit SHA you installed from and keep a copy.

## Quick start

```
/plugin marketplace add https://github.com/quran-ws/qurantech-skill
/plugin install qurantech@qurantech-skill
```

That installs it in Claude Code as `/qurantech:qurantech`. Requires Claude Code
v2.1.205 or later.

> Install from the `quranpedia` address. `quran-ws/qurantech-skill` does not
> exist yet — a request for it returns 404 — and it is the address most of
> quran.ws still shows. This will change when the repository transfers.

Three other routes, all in the repository README:

| Route | Command |
|---|---|
| Any supported agent runtime (Cursor, Codex, Gemini CLI, Copilot…) | `npx skills add quran-ws/qurantech-skill` |
| Copy the directory yourself | `git clone` it, then `cp -r qurantech-skill/plugins/qurantech/skills/qurantech ~/.claude/skills/qurantech` |
| Claude.ai or the API | Upload `dist/qurantech.skill` under Settings → Capabilities → Skills |

Skills load on relevance, not on command, so the useful check is a prompt:

```
add Warsh support to my Quran app
```

If it is live, the agent should open by asking which qirāʾah you support today
and what your data model looks like, rather than writing a migration. There is no
version string to read back — see Provenance.

## Two limits to know before you rely on it

**It does not name the quran.ws blocks.** The string `quran-ws` does not appear
anywhere in the skill. The references point at external sources — Quran
Foundation, QUL, Tanzil, QuranPedia, MP3Quran — and at two of these repositories
under their pre-transfer names, `quranpedia/quran-svg` and
`quranpedia/qiraat-ayah-map`. Quran Text, Quran Tajweed, Quran Engine, Quran
Assets, Quran SVG Elements and Quran PNG are not mentioned. If you want an agent
to reach for those, name them in your own prompt or project instructions.

**One of its numbers is contested.** `references/qiraat.md` assigns the reading
of Abū ʿAmr al-Baṣrī — and so both of its riwāyāt, al-Dūrī and al-Sūsī — to the
Basran counting system, total 6,204 ayat. Measured against the printed KFGQPC
editions we publish, al-Dūrī numbers 6,217 and al-Sūsī 6,218, both closest to
First Madinan. Both kinds of number can be meaningful — one is a scholarly
counting position for the reading, the other is what a publisher set in type —
and which belongs where is **unresolved**. Do not let an agent write either into
a schema as settled. See
[ayah-counting systems](https://quran.ws/docs/concepts/ayah-counting/).

## Works with

| | |
|---|---|
| [Quran Text](https://github.com/quran-ws/quran-text) | The verified text an agent should be reaching for first. |
| [Qiraat Ayah Map](https://github.com/quran-ws/qiraat-ayah-map) | The mapping behind the counting advice; named in the skill under its `quranpedia` address. |
| [Quran SVG](https://github.com/quran-ws/quran-svg) | The page artwork the muṣḥaf-display reference recommends, likewise. |

## Documentation

- [Reference: QuranTech](https://quran.ws/docs/reference/qurantech/) — what
  ships, every install route, and what it changes about an agent's output.
- [Choosing a block](https://quran.ws/docs/start/choosing-a-block/) — the eight
  building blocks this guidance is about.
- [Glossary](https://quran.ws/docs/concepts/glossary/) — qirāʾah, riwayah,
  muṣḥaf, tajwīd, in plain English.

## Contributing

Wrong facts, dead links, outdated API details, or an agent doing something
un-adab with the skill loaded: open an issue with the prompt you used and what
went wrong. Content pull requests should cite their source, stay
technology-agnostic, stay lean — this ships inside a context window — and
respect the adab rules, including in code examples and test data.

## Licence

Code is **MIT**; the skill content in `plugins/` and `dist/` is **CC BY 4.0**,
with a standing waiver of attribution for use inside a product. See
[LICENSE](LICENSE).

The datasets and sources the references point to carry their own licences, some
requiring attribution — the references flag these where they apply.

## Acknowledgements

This skill stands on the work of the wider Qurʾān-tech community: the King Fahd
Glorious Qurʾān Printing Complex, Tanzil, the Quran Foundation / Quran.com, QUL
(Tarteel), QuranPedia, MP3Quran, EveryAyah, the Quranic Arabic Corpus, the
offline-tarteel project, and the [Itqan community](https://itqan.dev) of
developers serving the Qurʾān. May Allah reward them all.
