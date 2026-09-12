# Adab (Etiquette) Rules for Quran Applications

These rules are **mandatory** — not suggestions. Every Quran app must respect the sanctity of the Quranic text.

## Text integrity and display

These rules are the Quran.ws guidelines, stated once there and copied here by
`tools/generate_adab.py` in quran-ws/docs. Each line names its rule; the page
carries the example and the check that catches a violation.

- **Never edit the source in place; any processing produces a new copy or a new layer, and the source stays reproducible from the published original.** (Quranic text 1.2, https://quran.ws/docs/guidelines/quranic-text/)
- **Never type Quranic text by hand, in code, prose, tests or documentation; quote it by reference, or copy it from a released dataset and name the release.** (Quranic text 1.4, https://quran.ws/docs/guidelines/quranic-text/)
- **Never run `normalize` on the source, to `NFC`, `NFD`, `NFKC` or `NFKD`.** (Quranic text 2.2, https://quran.ws/docs/guidelines/quranic-text/)
- **Don't trim, strip "weird characters", collapse whitespace, swap look-alike characters or remove marks from the source; generate a separate copy when search needs one.** (Quranic text 2.3, https://quran.ws/docs/guidelines/quranic-text/)
- **Edition marks are not part of an ayah: end of ayah ۝ (`U+06DD`), rubu al-hizb ۞ (`U+06DE`), sajdah ۩ (`U+06E9`).** (Quranic text 3.4, https://quran.ws/docs/guidelines/quranic-text/)
- **Check your character set against the font's `cmap` before adopting it, because a character with no glyph disappears or renders as a box and the reader won't notice.** (Quranic text 3.3, https://quran.ws/docs/guidelines/quranic-text/)
- **Fallback fonts are forbidden for Quranic text; a missing glyph fails the build and is never drawn by another font, because a substituted shape can read as a different mark.** (Engineering 5.3, https://quran.ws/docs/guidelines/engineering/)
- **Numbering systems are not interchangeable, and ayah boundaries do not line up across them.** (Quranic text 5.2, https://quran.ws/docs/guidelines/quranic-text/)
- **The basmalah is its own field, because whether it counts as an ayah depends on the numbering system, and surah al-Tawbah has none.** (Quranic text 5.3, https://quran.ws/docs/guidelines/quranic-text/)
- **An ayah number alone is not a location; bind it to its surah and its numbering system.** (Quranic text 4.2, https://quran.ws/docs/guidelines/quranic-text/)
- **Never trim the text to fit the layout, and never let an ellipsis stand in Quranic text.** (Quranic text 7.1, https://quran.ws/docs/guidelines/quranic-text/)
- **A fragment is presented as a fragment, with its reference and a link, and never reads as the complete ayah.** (Quranic text 7.2, https://quran.ws/docs/guidelines/quranic-text/)
- **Never render an ayah that hasn't finished loading; show a loading state or an error.** (Quranic text 7.4, https://quran.ws/docs/guidelines/quranic-text/)
- **Keep the text out of placeholders, fixtures, error logs, filenames and URLs; a reference like `114:1` is enough.** (Quranic text 7.5, https://quran.ws/docs/guidelines/quranic-text/)
- **When the text is not what you expected, fail loudly; never auto-repair and never guess at missing text or metadata.** (Quranic text 8.4, https://quran.ws/docs/guidelines/quranic-text/)
- **A mushaf data update is never silent; a new version is a new dataset with a known origin and a known diff, announced to the reader.** (Quranic text 8.5, https://quran.ws/docs/guidelines/quranic-text/)
- **A recitation never plays without the reader's action; autoplay is off by default, and a notification or an advertisement never carries it.** (Engineering 6.5, https://quran.ws/docs/guidelines/engineering/)

## Naming, layout and interface

- **Variable and database column names follow the Quran.ws naming guideline** (https://quran.ws/docs/guidelines/naming/): `ayah`, `surah`, `mushaf`, one canonical name in the model, the table, the foreign key and the API; never `quran_string`, `verse_blob` or `raw_text`.
- **Never place Quranic text in UI elements that imply dismissal** (swipe-to-delete, dismissible toasts, error messages), and never let a user edit it in the UI.
- **Right-to-left layout is mandatory** for all Quranic text, with proper bidi handling in mixed-language contexts.
- **Basmalah:** whether it is counted as an ayah depends on the numbering system; it is absent from surah 9 and part of the text in 27:30. Read it from the dataset, never assume it.

## Audio Etiquette

- **Audio recitations must start from the beginning of an ayah**, not from the middle.
- **Provide a way to seek by ayah**, not arbitrary timestamps that land mid-recitation.
- **Attribute the reciter clearly** when playing audio.

## Search & Results

- **Search results must show complete ayahs**, not fragments or snippets with the match highlighted mid-word.
- **Never rank or sort Quranic ayahs by "relevance"** in a way that implies some ayahs are more important than others. Sort by mushaf order (surah:ayah) by default.

## Error States

- **If Quranic text fails to load, show a respectful placeholder** (e.g., "Unable to load ayah" with the reference) — never show broken/partial text.
- **If a font fails to load, fall back to another Quranic font**, not a system font. If no Quranic font is available, show the reference only.

## AI & LLM Integration

- **Never let AI generate tafsir freely.** Use RAG (Retrieval-Augmented Generation) with authoritative tafsir sources only.
- **AI hallucination in Quranic context is unacceptable.** Real example: an LLM explained "Fa waylun lil-musalleen" (Al-Ma'un:4) without the crucial context that the "woe" is for those who are *negligent* of their prayer, not those who pray. Without the following ayah and asbab al-nuzul, the AI gives misleading interpretations.
- **Human review is mandatory** for any AI-generated Islamic content before it reaches users.
- **AI-generated translations must be clearly labeled** as AI-generated and not attributed to any scholar.
- **Include transparent sourcing** — always show which tafsir/translation the AI's answer is based on.

## Accessibility

- **Screen reader compatibility is mandatory**, not optional. Many popular Quran apps are completely inaccessible.
- **Blind users need the simplest possible interface** — every unnecessary UI element is an obstacle.
- **Test with VoiceOver (iOS), TalkBack (Android), and NVDA/JAWS (desktop).**

## Translations & Tafsir

- **Always label translations as "ترجمة معاني القرآن"** (Translation of the meanings of the Quran), never as the Quran itself. Make the distinction visually clear.
- **Always attribute translations** to their author/scholar.
- **Tafsir must be clearly separated** from the Quranic text visually and semantically.

## Linguistic Adab (Grammar Features)

If the app displays grammatical analysis, the *terminology* itself carries adab. Classical scholars phrased grammar about the Quran with deliberate reverence — reproduce their choices:

- Passive verbs: **«مبنيٌّ لما لم يُسمَّ فاعلُه»**, never «مبني للمجهول».
- لفظ الجلالة as object: **«منصوبٌ على التعظيم»**.
- Imperatives addressed to Allah are **دعاء, not أمر**; لا before them is «حرف دعاء», not «ناهية».
- **Never label any Quranic particle «زائد»** (redundant); use «صلة» or «تأكيد».
- **Don't derive or display a root for لفظ الجلالة** — its derivation is disputed among scholars.

Implement these as a presentation layer over imported linguistic data (never edit the data), and keep judgment calls — like which addresses are divine — in a human-reviewed data file rather than inferring at runtime. Full detail and rationale: [irab.md](irab.md).
