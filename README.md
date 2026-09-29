# QuranTech — an Agent Skill for Quran App Development

[![Status: Experimental](https://img.shields.io/badge/status-experimental-orange)](#-status-experimental)
[![Agent Skill](https://img.shields.io/badge/type-agent%20skill-blue)](https://code.claude.com/docs/en/skills)
[![Plugin](https://img.shields.io/badge/type-claude%20code%20plugin-purple)](https://code.claude.com/docs/en/plugins)
[![skills.sh](https://skills.sh/b/quran-ws/qurantech-skill)](https://skills.sh/quran-ws/qurantech-skill)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](#-contributing--feedback)

**QuranTech** teaches AI coding agents how to build Quran applications *correctly* on top of the Quran.ws building blocks and other trusted sources — with verified text sources, qira'at-aware data models, proper Arabic rendering, and the etiquette (adab) the Quranic text deserves.

Building Quran apps has hidden domain traps that generic coding knowledge walks straight into: hardcoding 6,236 ayahs (counts differ across riwayat), matching verses across mushafs by number (they merge and split), rendering Uthmani script in system fonts (glyphs break), auto-generating tafsir with an LLM (dangerous), Unicode-normalizing the text (destroys it). This skill encodes the know-how that prevents all of that — gathered from production Quran platforms, open datasets, and the Muslim developer community.

Works with [Claude Code](https://code.claude.com), [Claude.ai](https://claude.ai), the Claude API, and any agent runtime that supports the [Agent Skills](https://code.claude.com/docs/en/skills) format.

## What is in it

Seven skills. `qurantech` is the router: it picks the right [Quran.ws](https://quran.ws) building block or third-party source, then hands off. Six block skills carry the working detail for one block each.

| Skill | Use it for |
|-------|-----------|
| **`qurantech`** (router) | Choosing blocks and sources, adab rules, qira'at, data models, offline architecture, testing, audio, search, translations, tafsir, i'rab, hifz |
| `quran-svg` | Printed mushaf pages as SVG with ayah polygons |
| `quran-svg-elements` | Word- and mark-level interaction on mushaf pages |
| `quran-engine` | Fast native page rendering (web, iOS, Android, Flutter, React Native) |
| `quran-tajweed` | Tajweed annotation spans over unchanged text |
| `qiraat-ayah-map` | Converting ayah references between the six counting systems |
| `quran-assets` | Surah headers, ayah markers, page frames, ornaments |

`quran-text` and `quranic-terminology` ship their own skills in [`quran-ws/quran-text`](https://github.com/quran-ws/quran-text) and [`quran-ws/docs`](https://github.com/quran-ws/docs); the router points to them.

Two rules run through everything:

1. **Never compromise the text.** Verified sources only, byte-exact storage, no truncation, no normalization, integrity checks in CI.
2. **Don't reinvent solved problems.** Use a building block when one fits, a third-party source when none does, and say which.

## Installation

### Claude Code (plugin marketplace)

```bash
/plugin marketplace add https://github.com/quran-ws/qurantech-skill
/plugin install qurantech@qurantech-skill
```

Installs all seven skills as namespaced Claude Code plugin skills (`/qurantech:qurantech`, `/qurantech:quran-svg`, …), with versioned updates. Requires Claude Code v2.1.205 or later.

### One command (any supported agent)

```bash
npx skills add quran-ws/qurantech-skill
```

Installs via the [skills.sh](https://skills.sh) CLI for Claude Code, Cursor, Codex, Gemini CLI, GitHub Copilot, and more.

### Claude Code (manual)

```bash
git clone https://github.com/quran-ws/qurantech-skill.git
mkdir -p ~/.claude/skills
cp -r qurantech-skill/plugins/qurantech/skills/* ~/.claude/skills/
```

Either way — verify with a prompt like *"add Warsh support to my Quran app"* and watch the skill trigger.

### Claude.ai / Claude API

Upload the packaged skill files (`dist/*.skill`, start with `qurantech.skill`) via **Settings → Capabilities → Skills** on Claude.ai, or attach it through the API's skills support. To rebuild the package yourself, use the [skill-creator](https://github.com/anthropics/skills) tooling:

```bash
for d in plugins/qurantech/skills/*/; do python -m scripts.package_skill "$d" dist; done
```

## Example prompts

- *"Build a mushaf reader web app with tajweed coloring"*
- *"My app is Hafs-only — add support for Warsh"*
- *"Identify which ayah is being recited from microphone audio, fully offline"*
- *"Design the database schema for a multi-riwayah Quran app with bookmarks"*
- *"I have a WordPress tafsir blog — let readers tap a verse to see its tafsir"*
- *"Design a hifz app with automatic recitation checking"*
- *"Which Quran API should I use for translations in 50 languages?"*

## Repository layout

```
qurantech-skill/
├── .claude-plugin/marketplace.json     # Claude Code plugin marketplace catalog
├── plugins/qurantech/
│   ├── .claude-plugin/plugin.json      # Plugin manifest
│   └── skills/
│       ├── qurantech/                  # Router skill
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── blocks.md           # Quran.ws building-block catalog
│       │       ├── concepts/           # adab, qira'at, rendering, data models, architecture, QA
│       │       ├── features/           # audio, search, hifz, tafsir, i'rab, verse recognition…
│       │       └── sources/            # third-party APIs and datasets, QuranPedia API and embed
│       ├── quran-svg/
│       ├── quran-svg-elements/
│       ├── quran-engine/
│       ├── quran-tajweed/
│       ├── qiraat-ayah-map/
│       └── quran-assets/               # each: SKILL.md + references/
├── evals/                              # Test prompts + assertions
├── dist/                               # Packaged .skill files for Claude.ai / API
└── README.md
```

## 🧪 Status: Experimental

This skill is **young and actively evolving**. The guidance is drawn from real production systems and verified datasets, but coverage is uneven, some recommendations will age as APIs and datasets evolve, and we are still benchmarking how much it improves agent output (an eval suite lives in `evals/`).

Treat it as a knowledgeable colleague, not a fatwa: **verify religious-content decisions with qualified scholars, and verify technical output like any other code review.** If the skill leads an agent to do something wrong — especially anything touching text integrity or Islamic content — we want to know immediately.

## 🤝 Contributing & Feedback

This project gets better through the community's eyes. All of these help:

- **🐛 Report issues** — wrong facts, dead links, outdated API details, misbehaving guidance, or an agent doing something un-adab with the skill loaded. Open an issue with the prompt you used and what went wrong.
- **📚 Improve references** — deeper qira'at knowledge, more verified data sources, corrections from scholars, new domains (recitation pedagogy, accessibility, Indo-Pak script…).
- **🧪 Add evals** — realistic prompts + objective assertions in `evals/evals.json` are as valuable as content.
- **🌍 Share experience** — built a Quran app using this skill? Tell us what the skill missed; the gaps you hit are the roadmap.

Guidelines for content PRs:

1. **Cite sources** — guidance should trace to verified data, production experience, or scholarly reference.
2. **Stay technology-agnostic** — patterns over frameworks; name a specific stack only as evidence that a pattern works.
3. **Be lean** — this content ships inside an AI context window; every paragraph must earn its tokens.
4. **Respect the adab rules** — including in code examples and test data (`references/adab.md`).

## Acknowledgements

This skill stands on the work of the wider Quran-tech community: the King Fahd Glorious Quran Printing Complex, Tanzil, the Quran Foundation / Quran.com, QUL (Tarteel), QuranPedia, MP3Quran, EveryAyah, the Quranic Arabic Corpus, the offline-tarteel project, and the [Itqan community](https://itqan.dev) of developers serving the Quran. May Allah reward them all.

## License

[MIT](LICENSE) — free to use, modify, and redistribute. Note that the *datasets and content sources the skill points to* each carry their own licenses (some require attribution, e.g. the Quranic Arabic Corpus); the skill's references flag these where they apply.
