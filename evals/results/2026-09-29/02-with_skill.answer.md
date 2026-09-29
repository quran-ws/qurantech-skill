### FILE design.md
# Hifz App: Feature Set and Data Model (Mobile)

Status: draft for review. Anything marked **[scholar/teacher review]** is a default that a qualified teacher must confirm before it ships.

## 1. Purpose and stance

The app supports memorization (hifz) **under a teacher**. It does not replace the teacher. It handles what software does well: scheduling revision, keeping records, drilling, and catching gross errors. The teacher does what software cannot: judging tajweed, makhraj and fluency, and deciding when a student is ready to move on.

Design consequences:

- The teacher is a first-class user role, not an afterthought.
- Automated feedback is advisory and always shows its uncertainty.
- The teacher's assessment always outranks the machine's.
- The app never states "your recitation is correct" (see §6).

## 2. Users and roles

| Role | Can do |
|---|---|
| **Student** | Do daily sessions, self-record, view own progress, receive assignments |
| **Teacher** | Assign sabaq, review submissions, mark mistakes by word, grade, override any automated result |
| **Solo learner** | Student without a teacher. Same features, but the app shows a persistent notice that automated checking is not a substitute for a teacher |
| **Guardian** (optional) | Read-only progress for a child's account |

A student can have several teachers (for example, a hifz teacher and a tajweed teacher). Each link has a scope.

## 3. Memorization method the app encodes

Many hifz programmes use a three-tier daily routine **[teacher review]**: *sabaq* (new lesson), *sabqi* (recent revision) and *manzil* (old revision). Amounts and windows vary by school and student, so **they are per-student settings owned by the teacher, not app constants**.

Implications:

- The **page** is the usual unit of progress, but page boundaries come from the active mushaf, not a hardcoded 604.
- The home screen answers "what do I do now?" (today's queue), not "list of surahs".
- Revision is the hard part. A tracker that only records "memorized" without a revision queue fails users.

## 4. Feature set

### 4.1 MVP

1. **Today's queue** with sabaq, sabqi and manzil sections and a time budget rather than a card count.
2. **Teacher assignment**: the teacher sets the next sabaq range and the tier windows and amounts.
3. **Recitation session** in three modes:
   - Full mask: the ayah is hidden, the student recites, then reveals.
   - First-word hint.
   - Progressive reveal (needs word following, §6.2).
4. **Word-level mistake marking** by student or teacher. Teacher marks are authoritative.
5. **Audio loops** for sabaq: repeat an ayah N times, loop a range, adjustable speed, gapless. Playback starts only on user action and begins at an ayah boundary. Reciter is always shown.
6. **Progress** by page and juz, with a surah view as secondary. Statuses are not started, in progress, memorized, needs review.
7. **Similar-verse (mutashabihat) warnings** with a side-by-side diff of the differing words.
8. **Submission to teacher**: the student records a session, and the teacher listens, marks and grades asynchronously. Live sessions happen offline in the real world; the app should not need to be involved.
9. **Offline everything**: queue, drills, masks, recording, and on-device recognition all work without connectivity. Sync happens when a connection returns.

### 4.2 Later

- Testing modes: continue from here, random spot check, page-connection drill (last ayah of a page to first of the next), "where is this from?".
- Mutashabihat drill mode.
- Teacher dashboard for a class: who is overdue, chronic-mistake heat map.
- Adaptive scheduling (FSRS-style), only after enough real review data exists.
- Multi-riwayah support (§5.4).
- Tajweed colouring as a study aid on the review text (annotated, never presented as judgment).

### 4.3 Deliberately excluded

- Leaderboards or public rankings of "amount memorized". This is worship, not competition. Streaks and daily goals are allowed, with a humble tone.
- Any "score" for recitation quality shown as a grade to the student.
- AI-generated tafsir or explanation. If explanations are added later, use retrieval over authoritative sources with human review.
- Khatma (reading completion) is a separate feature and is not mixed into memorization state.

## 5. Data model

### 5.1 Conventions (apply to every entity)

- **A reference is never bare `surah:ayah`.** Every ayah reference carries `mushaf` and `counting_system`. Numbering differs across counting systems, and ayahs split or merge.
- **Word-level data uses the shared word number**, which is stable across riwayat, instead of a file-local position.
- **Totals are derived** from the loaded mushaf, never stored or hardcoded (ayah counts differ by counting system, and page counts by edition).
- **Quranic text is never stored in the user data model.** User records hold references only. Text comes from a pinned, source-verified dataset (for example Quran.ws `quran-text`) and is never edited, normalized, or typed by hand.
- **Hiding is a UI overlay.** Masks and reveals never modify or truncate text. A revealed ayah is always complete.
- **Logs, analytics and fixtures contain references only** (such as `2:255`), never Quranic text.
- Layers (mistakes, timings, tajweed) record the `edition` (with a source hash) they were measured against.

### 5.2 Entities

```
User ──< TeacherLink >── User
User ──< MemorizationUnit ──< ReviewEvent
                         └──< MistakeMark
User ──< Assignment
User ──< Session ──< Attempt ──< AutoCheckResult
                            └── Recording (local file)
                            └──< TeacherFeedback
Mushaf ──< (layers: ayah_starts, page_starts, line_starts, juz_starts)   [from dataset]
SimilarGroup ──< SimilarMember                                            [from dataset]
```

**User**

| Field | Type | Notes |
|---|---|---|
| id | uuid | |
| role | enum | student / teacher / guardian |
| display_name | string | |
| default_mushaf | string | Mushaf key |
| settings | json | Time budget, tier windows and amounts, loop defaults |

**TeacherLink**

| Field | Type | Notes |
|---|---|---|
| student_id, teacher_id | uuid | |
| scope | enum | hifz / tajweed / both |
| status | enum | pending / active / ended |
| consent_recordings | bool | Student (or guardian) consent to share recordings |

**MemorizationUnit** is the item the queue schedules. It is a contiguous range, usually a page or part of one.

| Field | Type | Notes |
|---|---|---|
| id | uuid | |
| student_id | uuid | |
| mushaf | string | Mushaf key |
| counting_system | string | System id |
| start_word, end_word | int | Shared word numbers. Ranges are anchored to words so they survive layout changes |
| surah, ayah_from, ayah_to | int | Denormalized for display and query, in that counting system |
| unit_kind | enum | page / ayah_range / surah |
| status | enum | not_started / in_progress / memorized / needs_review |
| tier | enum | sabaq / sabqi / manzil |
| memorized_on | date | When it first passed teacher sign-off |
| signed_off_by | uuid / null | Teacher who confirmed. Null means self-declared |
| stability, difficulty | float | Scheduler state (see §7) |
| next_review | datetime | |
| last_reviewed | datetime | |

`signed_off_by` matters: **"memorized" is only teacher-verified if a teacher said so.** The UI distinguishes the two.

**Assignment**

| Field | Type | Notes |
|---|---|---|
| id, student_id, teacher_id | uuid | |
| unit_id | uuid | Range to memorize |
| kind | enum | sabaq / sabqi / manzil / tajweed_focus |
| due | date | |
| note | string | Teacher's instruction (not Quranic text) |
| status | enum | open / submitted / accepted / redo |

**Session / Attempt**

A *Session* is one sitting. An *Attempt* is one recitation of one unit within it.

| Field (Attempt) | Type | Notes |
|---|---|---|
| id, session_id, unit_id | uuid | |
| mode | enum | full_mask / first_word / progressive / spot_check / page_connection |
| started_at, duration_ms | | |
| recording_uri | string / null | Local by default. Uploaded only with consent |
| self_mistake_count | int | |
| outcome_source | enum | self / teacher |
| outcome | enum | clean / minor / major / redo. **Only these; no numeric score** |

**MistakeMark** (word-level, the most valuable record for revision)

| Field | Type | Notes |
|---|---|---|
| unit_id, attempt_id | uuid | |
| mushaf, counting_system | string | |
| word_number | int | Shared word number |
| kind | enum | forgot / wrong_word / wrong_order / drifted_to_similar / tajweed / makhraj / hesitation |
| source | enum | student / teacher / auto |
| confidence | float / null | Only for `auto` |
| similar_target | ref / null | Where the student drifted to, if known |
| created_at | datetime | |

`tajweed` and `makhraj` kinds are **teacher-only**. Automation never writes them (§6.3).

**AutoCheckResult** (advisory, stored separately from teacher feedback)

| Field | Type | Notes |
|---|---|---|
| attempt_id | uuid | |
| engine, engine_version | string | Model identity, so results are reproducible and comparable |
| matched_ref | {mushaf, counting_system, surah, ayah, ayah_end} | The recogniser's counting system, converted via an ayah map |
| score | float | Raw engine confidence, not a quality grade |
| word_events | json | [{word_number, state: matched / uncertain / missing / extra}] |
| alternatives | json | Other candidates when ambiguous |
| audio_quality | enum | ok / noisy / too_short |

**TeacherFeedback**

| Field | Type | Notes |
|---|---|---|
| attempt_id, teacher_id | uuid | |
| outcome | enum | Same as Attempt.outcome |
| audio_note_uri, text_note | | Teacher comments, never Quranic text |
| sign_off | bool | Sets `signed_off_by` on the unit |

**SimilarGroup / SimilarMember** are read-only reference data from a curated dataset (for example the Quran Universal Library mutashabihat data). Record the dataset's source and version. Do not compute similarity yourself. Whether a scholar reviewed the curation should be checked before trusting it **[scholar review]**.

### 5.3 Sync

- Local-first: an on-device database is the source of truth during a session. The server holds the shared state between student and teacher.
- Teacher-authored records (assignments, feedback, sign-offs) win over student-authored ones on conflict. Mistake marks are append-only.
- Recordings are large and sensitive. They stay on-device unless the student consents to share each one, and they can be deleted on request.

### 5.4 Riwayah and mushaf switching

Progress is anchored to shared word numbers plus `{mushaf, counting_system}`. Switching riwayah converts ranges through an ayah-map (for example Quran.ws `qiraat-ayah-map`). Splits and merges produce **ranges, not single ayahs**, and the unit may need teacher confirmation after conversion. Page boundaries are re-derived from the new mushaf. Do not silently reuse page numbers.

## 6. Automatic recitation checking: what it does, what it cannot

### 6.1 Level 1: verse identification (feasible, on-device)

Given 16 kHz mono audio, an on-device recogniser returns `{surah, ayah, ayah_end, score}`. Candidate: Tilawa (`@tilawa/core`), which runs ONNX models fully offline, including in React Native.

Use it to:
- Confirm the student recited the assigned range and not a different passage.
- Auto-follow position in the mushaf.
- Identify which ayah in a multi-ayah recitation.

Reported benchmark results are strong on small test sets. The repo's own numbers were about 248 of 256 on its largest set with the default streaming model, with remaining errors mostly among textually identical or near-identical ayahs. **Treat that as an upper bound on clean audio**, not an expected real-world rate. Re-verify the figures before quoting them, since releases change them. Test on your own audio: phone microphones, background noise, children's voices, and non-Arabic-native accents.

Handling:
- Show a match only above a threshold tuned on your own data.
- When the result is ambiguous (identical or near-identical ayahs), show the candidates and ask; never pick silently.
- Route recogniser output through the ayah-map into the user's counting system before it touches any record.

### 6.2 Level 2: word-following and gross-error detection (partly feasible, approximate)

Word alignment against the *expected* text can:
- Drive progressive reveal (reveal as the student recites).
- Flag **omitted words, added words, and substituted words**.
- Flag **drift into a similar passage**, naming the other reference.
- Detect long hesitation or restart.

Limits:
- Output is probabilistic. It will produce false alarms and misses, more so on fast recitation, noisy audio, and unusual voices.
- A mismatch is reported as **"check this word"** (state `uncertain`), never "you made a mistake".
- Because the matcher knows the expected text, it can be biased toward accepting it. A model that fills in the expected word can **hide real errors**. Absence of a flag is therefore not evidence of correctness.
- Only the student or teacher converts an `auto` flag into a stored MistakeMark. The student can dismiss it.

### 6.3 What automation cannot do

| Cannot reliably do | Why | Who does it |
|---|---|---|
| Judge tajweed (madd length, ghunnah, idghām, qalqalah, ikhfāʾ, etc.) | Current open ASR models are not validated for tajweed correctness. Timing- and quality-based rules depend on the reciter's style and the riwayah | Teacher |
| Judge makhraj (articulation points) and sifat | Needs fine phonetic discrimination. Similar-sounding letters are easily confused by models, and by mic and codec | Teacher |
| Certify that a recitation is correct | A false "correct" is worse than no feedback; absence of flags ≠ correct | Teacher |
| Assess fluency, rhythm, melody, and readiness for sign-off | Judgment, not pattern matching | Teacher |
| Handle other riwayat or qira'at as reliably | Models are typically trained mostly on Hafs. Non-Hafs coverage must be measured before enabling | Teacher, plus measurement |
| Work well for all voices | Accuracy varies with age, gender, accent and recording conditions, and may be worse for exactly the beginners who need help | Teacher |
| Replace an *ijazah*-style transmission | Hifz is traditionally taught by listening to a qualified teacher | Teacher |

**Product rules that follow from this:**

1. The UI never shows "correct", a percentage grade, a star rating, or a green tick for recitation quality. It shows *what was heard* (identified range, words to check) and *what is unknown*.
2. The words "tajweed" or "makhraj" never appear in automated feedback. Tajweed colouring is a reference aid on the text and is labelled as such.
3. The status **memorized (teacher-verified)** can only be set by a teacher. A self-declared status is shown differently.
4. Solo learners get a permanent, plain-language notice: the automated check catches gross slips, and recitation should be corrected by a qualified teacher.
5. Automated results are stored separately from teacher feedback, with engine version, so they can be audited or discarded.
6. Automation is opt-in per session and the app works fully without it.

### 6.4 Pipeline

```
mic (16 kHz mono, ~300 ms chunks)
  → on-device VAD / quality check (too short, too noisy → say so, don't guess)
  → recogniser (streaming, ONNX runtime for React Native / native)
  → verse match + word events against expected range
  → map through counting system to the user's mushaf
  → advisory UI: identified range, "check this word" markers, alternatives
  → user/teacher confirms or dismisses → MistakeMark
  → recording (optional, consented) → teacher queue
```

Licensing matters: the default Tilawa streaming model and its phoneme corpus are under a **non-commercial, share-alike** licence, while the alternate FastConformer assets are CC-BY-4.0. Choose per the app's commercial status before building on either, and read the repo's NOTICE file. The model is about 66 MB, so download it on first use with visible progress, not at install.

### 6.5 Evaluation plan (before shipping any auto feature)

- Build a test set from real target users (recordings with consent), labelled by teachers, with deliberate errors: omitted, substituted and swapped words, wrong-similar-verse.
- Measure **false-negative rate on real errors** (missed mistakes) and false-positive rate separately. Missed errors are the dangerous direction.
- Break down by age, gender, accent, device, and noise.
- Have a teacher review a sample of automated flags each release.
- Ship a feature only if its measured behaviour justifies its wording; otherwise weaken the wording.

## 7. Scheduling

- Start with a **fixed rotation seeded from the teacher's tier settings**. It is predictable, explainable, and matches how teachers already work.
- The queue respects a **time budget** (minutes of recitation), since one unit takes minutes.
- Grading input is the teacher's outcome when present, otherwise the student's mistake count (0 = easy, 1–2 = good, 3+ = again). Defaults are tunable and unsourced **[teacher review]**.
- Cap maximum intervals so the whole memorized portion is revisited on a rotation.
- Chronic word-level mistakes raise the review frequency of the pages containing them.
- Adaptive scheduling (FSRS/SM-2 style) is a later step, after real data exists.

## 8. Adab and integrity requirements

- Quranic text comes from a pinned, source-verified dataset with a recorded release and hash. Never hand-typed, never in tests or fixtures (tests load real ayahs from the named release and compare).
- Use the mushaf's own font. No fallback fonts. Fail loudly with the reference if a glyph is missing.
- Never truncate an ayah. Test prompts and revealed text show the complete ayah. A fragment shown for a hint (such as first-word mode) is labelled as a fragment with its reference.
- Do not show an ayah that has not finished loading.
- No Quranic text in logs, analytics, filenames, URLs or crash reports. Use `surah:ayah` with counting system.
- No Quranic text in dismissible UI (swipe-to-delete, toasts) and no user editing of it.
- Audio: no autoplay, always starts at an ayah boundary, seek by ayah, reciter attributed.
- Similar-verse lists are shown in mushaf order, not ranked by "importance".
- Right-to-left layout and screen-reader support (VoiceOver and TalkBack) are required. Page images carry no text, so provide a text layer for accessibility.
- Mushaf data updates are never silent. A new version is a new dataset, announced, with a known diff.

## 9. Privacy and safeguarding

- Recordings of voices, and of children in particular, are personal data. Default is on-device only.
- Sharing with a teacher is per-recording, with a consent record. Guardian consent for minors.
- Teacher–student messaging is limited to the assignment and feedback flow. No open chat or contact details exchange in v1.
- Users can export and delete their data, including recordings.
- Recognition runs on-device, so audio does not need to leave the phone for auto-check.

## 10. Suggested building blocks

| Need | Choice |
|---|---|
| Text, pages, lines, shared word numbers | Quran.ws `quran-text` (or another source-verified dataset) |
| Cross-riwayah or counting conversion | `qiraat-ayah-map` |
| Page rendering, word masks, tap and hit-test | `quran-engine` (native) with `quran-svg-elements` (Hafs only) or `quran-svg` |
| Tajweed colouring (study aid) | `quran-tajweed`, only on the edition it was measured on |
| Similar verses | QUL mutashabihat data |
| Verse recognition | Tilawa, subject to §6.4 licensing |
| Audio | Per-ayah recitation sets with verified licences and word timings where available |

Verify licences of text, fonts, artwork, audio and models before shipping. Pin versions of all datasets and packages.

## 11. Open questions for teachers and scholars

1. Are the default tier windows and amounts acceptable, and what ranges should the app allow?
2. What sign-off vocabulary do teachers actually use (for example, levels of readiness)? The `outcome` enum should match practice.
3. Is a first-word hint acceptable as a fragment display under the app's adab rules?
4. Does the target audience use a riwayah other than Hafs? If so, measure recogniser accuracy first.
5. Who is the first teacher cohort for a pilot, and what error set can they label for §6.5?
6. Has a scholar reviewed the mutashabihat curation we plan to rely on?


### FINAL MESSAGE
I wrote the design doc to `/tmp/eval2-with_skill-gwy3ms6j/design.md`. It's a draft with no code behind it, and the scheduling defaults and the teacher sign-off vocabulary need a teacher's review.

**Feature set**
- The app is built around the teacher-student relationship. Teachers assign the next new lesson (sabaq), set the recent-revision (sabqi) and old-revision (manzil) windows, mark mistakes word by word, and sign off units.
- The home screen is a daily revision queue with a time budget, not a list of surahs.
- The MVP includes hide/reveal drills, audio repeat loops, warnings for similar verses, and recorded submissions that the teacher reviews later.
- Everything works offline.
- Leaderboards, numeric recitation grades and AI-generated tafsir are left out on purpose.

**Data model**
- Every ayah reference carries the mushaf and counting system, never a bare `surah:ayah`. Word positions use the shared word number, and totals are derived from the loaded mushaf.
- User records hold references only, never Quranic text.
- The core entities are `MemorizationUnit`, `Assignment`, `Session` and `Attempt`, plus `MistakeMark` and `TeacherFeedback`.
- `AutoCheckResult` is stored separately from teacher feedback, with the engine version recorded.
- A unit only counts as "memorized (teacher-verified)" if a teacher signed it off.

**What automation can and can't do**
- **Can:** on-device verse identification, for example with Tilawa. It can also follow position word by word, flag omitted, added or substituted words, and name the other passage when a student drifts into a similar verse. Results are advisory and shown as "check this word".
- **Can't:**
  - Judge tajweed or makhraj, or certify that a recitation is correct.
  - Judge fluency or readiness for sign-off.
  - Give reliable results for non-Hafs riwayat.
- A matcher that knows the expected text can hide real errors, so no flag does not mean the recitation was correct.
- The UI never shows "correct", a grade or a green tick. Solo learners get a permanent notice that the check is no substitute for a teacher.
- Before shipping any auto feature, the doc calls for testing on real, teacher-labelled recordings and measuring missed errors separately from false alarms.

Two things to check. The Tilawa benchmark figures come from its own repo notes, so re-verify them before quoting them. Tilawa's default model is under a non-commercial licence, so check that against your plans. The doc also ends with open questions for teachers and scholars, including whether the tier defaults are acceptable and whether the similar-verse data has been scholar-reviewed.