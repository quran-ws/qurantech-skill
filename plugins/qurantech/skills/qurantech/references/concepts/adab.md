# Adab (Etiquette) Rules for Quran Applications

These rules are **mandatory** — not suggestions. Every Quran app must respect the sanctity of the Quranic text.

Items marked *(house convention, scholar review)* are this skill's conventions, not settled facts; have a qualified scholar confirm them before you rely on them.

## Text Integrity

- **Never truncate an ayah mid-text.** Always display complete ayahs. If space is limited, show fewer ayahs rather than cutting one short.
- **Never split a word across lines in a way that breaks meaning.** Use proper Arabic line-breaking rules.
- **Show the basmalah** at the beginning of every surah except At-Tawbah (Surah 9), taken from the dataset, never typed. Store it as its own field, not inside the first ayah. Whether it counts as an ayah depends on the counting system (`quran-text` records this per edition). In An-Naml (27:30) the basmalah appears within the ayah itself.
- **Preserve diacritical marks** (tashkeel/harakat) in Quranic text. Never strip them for convenience.
- **Use verified text sources only.** Never hand-type Quranic text. Take it from a released dataset with a named release and recorded digests, such as `quran-text` (built from KFGQPC packages with recorded SHA-256 digests), and name the release you used. Pin the version and check the digest in your build. This applies to **every place Quranic text appears**, prose included: when writing *about* an ayah, cite it by reference (surah:ayah).

## Display & Presentation

- **Ayah numbers must be accurate** to the counting system of the edition shown. Counting systems differ (kufi has 6,236 ayahs; madani-first and madani-last have 6,214 each), and riwayat attach to them differently. Never assume a universal count, and never identify a system by its total.
- **Surah names and metadata must match the mushaf edition.** Different mushafs may use slightly different surah header styles.
- **Use the font the mushaf names** — never render Quranic text in generic Arabic fonts. `quran-text` bundles the KFGQPC font each riwayah needs ([text-rendering.md](text-rendering.md)).
- **Right-to-left layout is mandatory** for all Quranic text. Ensure proper bidi handling even in mixed-language contexts.
- **Never place Quranic text in UI elements that imply dismissal** (e.g., swipe-to-delete, dismissible toasts, error messages). *(house convention, scholar review)*

## Data Handling

- **Never log Quranic text in error/debug logs, filenames or URLs.** Use ayah references (surah:ayah) instead.
- **Variable and database column names should be respectful** *(house convention, scholar review)*. Avoid names like `quran_string`, `verse_blob`, or `raw_text`. Prefer `ayah_text`, `surah_name`, `mushaf_page`.
- **Never use hand-typed Quranic text as test data, placeholder text, or lorem ipsum.** Tests load real ayahs from a released dataset (named release) and compare against it.
- **Cache and store Quranic text with care.** Ensure cached text is not corrupted, partially written, or mixed with non-Quranic content.
- **Quranic text should not be modifiable by users** in the UI. It is read-only content.

## Audio Etiquette

- **Audio recitations must start from the beginning of an ayah**, not from the middle.
- **Provide a way to seek by ayah**, not arbitrary timestamps that land mid-recitation.
- **Attribute the reciter clearly** when playing audio.
- **Do not auto-play Quran recitation** without user intent — always require explicit user action.

## Search & Results

- **Search results show complete ayahs by default.** A fragment (a snippet, a notification, an `og:description`) is acceptable only when it is labelled as a fragment, carries its reference and a link, and never reads as the whole ayah. Never cut between a letter and its marks, and never let an ellipsis stand in for text.
- **Never rank or sort Quranic ayahs by "relevance"** in a way that implies some ayahs are more important than others. Sort by mushaf order (surah:ayah) by default.

## Error States

- **If Quranic text fails to load, show a respectful placeholder** (e.g., "Unable to load ayah" with the reference) — never show broken/partial text.
- **If the mushaf's font fails to load, do not fall back to another Quranic font or a system font.** Fail loudly: show an error with the reference, and never render text in a font that may drop glyphs. Check the font's `cmap` coverage at build time (Quran.ws guidelines, status Proposed).

## AI & LLM Integration

- **Never let AI generate tafsir freely.** Use RAG (Retrieval-Augmented Generation) with authoritative tafsir sources only.
- **AI hallucination in Quranic context is unacceptable.** Example, cited by reference (107:4): an explanation that drops the following ayah and the reason for revelation can reverse the meaning, because the woe there is for those who are negligent of their prayer, not for those who pray.
- **Human review is mandatory** for any AI-generated Islamic content before it reaches users.
- **AI-generated translations must be clearly labeled** as AI-generated and not attributed to any scholar.
- **Include transparent sourcing** — always show which tafsir/translation the AI's answer is based on.

## Accessibility

- **Screen reader compatibility is required** *(house convention, scholar review)*.
- **Test with VoiceOver (iOS), TalkBack (Android), and NVDA/JAWS (desktop).** SVG and glyph pages carry no text; add a `quran-text` layer.

## Translations & Tafsir

- **Always label translations as a translation of the meanings** (the conventional Arabic label is «ترجمة معاني القرآن»), never as the Quran itself. Make the distinction visually clear. *(house convention, scholar review)*
- **Always attribute translations** to their author/scholar.
- **Tafsir must be clearly separated** from the Quranic text visually and semantically.

## Linguistic Adab (Grammar Features)

*(House convention, scholar review: the terminology below is not settled fact; have a qualified scholar confirm it.)* If the app displays grammatical analysis, the *terminology* itself carries adab. Classical scholars phrased grammar about the Quran with deliberate reverence; these are the choices this skill follows:

- Passive verbs: **«مبنيٌّ لما لم يُسمَّ فاعلُه»**, never «مبني للمجهول».
- لفظ الجلالة as object: **«منصوبٌ على التعظيم»**.
- Imperatives addressed to Allah are **دعاء, not أمر**; لا before them is «حرف دعاء», not «ناهية».
- **Never label any Quranic particle «زائد»** (redundant); use «صلة» or «تأكيد».
- **Don't derive or display a root for لفظ الجلالة** — its derivation is disputed among scholars.

Implement these as a presentation layer over imported linguistic data (never edit the data), and keep judgment calls — like which addresses are divine — in a human-reviewed data file rather than inferring at runtime. Full detail and rationale: [irab.md](../features/irab.md).
