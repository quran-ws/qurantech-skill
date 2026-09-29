### FILE design.md
# Hifz App — Design Document

Mobile app (iOS/Android) for Quran memorization, built around the teacher–student relationship rather than replacing it.

## 1. Principles

1. **The teacher is the authority.** Traditional hifz is transmitted (talaqqi) and certified (ijazah) by a person. The app supports that relationship; it never issues "you have memorized X" on its own authority.
2. **Automation assists, humans judge.** Automated checks are triage and practice aids, with stated confidence and limits (see §5).
3. **Text fidelity is non-negotiable.** Use a single verified Mushaf text source, pinned by version. No user-editable Quran text.
4. **Works offline.** Memorization happens on commutes and in mosques. Text, audio, and reviews must work without a network; sync is eventual.
5. **Privacy by default.** Recitations are voice data, often from children. Minimize retention and processing off-device.

## 2. Users and roles

| Role | Needs |
|---|---|
| Student (adult or minor) | Daily plan, practice, review scheduling, feedback, progress |
| Teacher | Assign portions, hear/review recordings, grade, see class overview |
| Guardian (for minors) | Consent, visibility into progress, no access to other students |
| Institution admin (optional, v2) | Manage classes/teachers |

A student can work solo (self-guided mode) but the product is designed for the teacher-linked flow. Solo mode uses the same features with automated feedback only, and labels it as such.

## 3. Core features

### 3.1 Mushaf reader
- Page-faithful rendering of a chosen riwaya/print (default: Hafs, Madinah Mushaf 15-line pagination; the layout matters because many huffaz memorize by page position).
- Modes: full text, **hidden-word/hidden-ayah** (cover text to test recall), first-letter hints.
- Reciter audio per ayah with word-level highlighting, repeat ranges, speed control.
- Translation/tafsir optional, off by default in memorization mode.

### 3.2 Memorization plan
- Unit hierarchy: sabaq (new lesson), sabqi (recent revision), manzil (long-term revision) — the standard three-part structure, configurable.
- Teacher assigns a range (ayah start–end) with due date; student may also self-plan with a target (e.g. 1 page/week).
- Plan adapts: missed days shift the schedule; teacher can override.

### 3.3 Practice loop for new lessons (sabaq)
1. Listen (reciter) → 2. Read along → 3. Repeat N times with text → 4. Repeat with text hidden → 5. Record recitation → 6. Automated pre-check → 7. Submit to teacher.
Progress through steps is tracked per ayah range.

### 3.4 Revision scheduling (spaced repetition)
- Each ayah (or small chunk) carries a strength estimate; review is scheduled by a spaced-repetition algorithm (e.g. FSRS-style or SM-2 variant).
- Chunking: schedule at the level of *pages/rubʿ segments* for manzil rather than single ayahs, plus finer tracking of ayahs the user repeatedly fails.
- Special handling of **mutashabihat** (similar verses): flag pairs/groups, add targeted drills ("which surah does this ending belong to?").
- Grades: Teacher grade overrides self/automated grade for scheduling.

### 3.5 Recitation check (see §5)
Record → on-device analysis → feedback shown to student → optionally sent to teacher.

### 3.6 Teacher tools
- Class/student list with due, overdue, and struggling indicators.
- Review queue: listen to submitted recordings (variable speed, jump to flagged spots), mark mistakes at ayah/word level with categories, give a grade and voice/text comment.
- Live session mode: teacher and student on the same Mushaf position; teacher taps words to mark errors during in-person or video lesson; auto-saves as a review record.
- Assign next portion, adjust revision load, certify a portion as "passed" (teacher sign-off).

### 3.7 Progress and motivation
- Coverage map (30 juz / 604 pages) colored by state: not started, learning, teacher-passed, needs review, weak.
- Streaks with grace days; avoid punitive framing.
- Milestones tied to teacher-certified progress only.

### 3.8 Communication
- Per-assignment comment thread with audio notes. No general chat with minors in v1 (safeguarding).

### 3.9 Settings
- Riwaya/script, reciter, tajweed color-coding, notifications/reminders (prayer-time-aware optional), language.

## 4. Data model

Relational core (PostgreSQL server; SQLite on device). IDs are UUIDs generated client-side to allow offline creation.

### 4.1 Quran reference data (read-only, versioned, bundled)
```
mushaf_edition(id, name, riwaya, script, pages, version_hash)
surah(id 1..114, name_ar, name_en, ayah_count)
ayah(id, surah_id, number, edition_id, text_uthmani, text_simple, page, juz, hizb_quarter)
word(id, ayah_id, position, text, page, line, audio_start_ms, audio_end_ms)
mutashabih_group(id) ; mutashabih_member(group_id, ayah_id, note)
reciter(id, name, riwaya); reciter_audio(reciter_id, ayah_id, uri, duration_ms)
```
`word` supports word-level errors, highlighting, and alignment. Text is keyed to `edition_id`; all user data references `ayah_id`/`word_id` from a specific edition version so pagination changes never silently shift records.

### 4.2 Users and relationships
```
user(id, role_default, display_name, dob_year?, locale, created_at)
teacher_student_link(id, teacher_id, student_id, status[pending|active|ended],
                     guardian_consent_at?, started_at, ended_at)
guardian_link(guardian_id, student_id, consent_at)
group(id, teacher_id, name) ; group_member(group_id, student_id)
```
A student may have several teachers (e.g. hifz teacher + tajweed teacher); each link has a `scope` (hifz | tajweed).

### 4.3 Plan and assignments
```
memorization_plan(id, student_id, created_by, daily_new_ayahs?, weekly_target_pages?, active)
assignment(id, student_id, teacher_id?, type[sabaq|sabqi|manzil|tajweed],
           start_ayah_id, end_ayah_id, due_at, status[open|submitted|reviewed|passed|redo],
           created_at)
```

### 4.4 Memorization state and scheduling
```
memory_item(id, student_id, unit_type[ayah|chunk|page], start_ayah_id, end_ayah_id,
            stage[learning|review|mature|lapsed], stability, difficulty,
            due_at, last_reviewed_at, lapses, teacher_passed_at?)
review_event(id, memory_item_id, student_id, occurred_at, source[self|auto|teacher],
             grade[again|hard|good|easy], duration_s, submission_id?)
```
`review_event` is append-only; `memory_item` is derived and can be rebuilt by replaying events (good for sync conflicts and algorithm changes).

### 4.5 Recitation submissions and feedback
```
submission(id, student_id, assignment_id?, start_ayah_id, end_ayah_id,
           audio_uri, audio_duration_ms, recorded_at, device_info,
           retention_until, status[local|uploaded|auto_checked|teacher_reviewed])
auto_check_result(id, submission_id, engine_version, ran_on[device|server],
                  overall_status[match|uncertain|mismatch|unusable_audio],
                  audio_quality_score, created_at)
auto_check_flag(id, auto_check_result_id, word_id_start, word_id_end,
                kind[missing|extra|substituted|out_of_order|low_confidence],
                confidence, heard_text?, audio_start_ms, audio_end_ms)
teacher_review(id, submission_id, teacher_id, grade, comment_text?, comment_audio_uri?,
               reviewed_at)
teacher_mark(id, teacher_review_id, word_id_start, word_id_end,
             category[wrong_word|skipped|added|prompted|hesitation|
                      tajweed_madd|tajweed_ghunna|tajweed_qalqalah|tajweed_other|
                      makharij|waqf_ibtida|other],
             note?)
```
Two separate tables for machine flags and human marks is intentional: they never merge, and comparing them yields precision/recall data for improving the engine (§5.6).

### 4.6 Progress and misc
```
progress_snapshot(student_id, date, pages_learning, pages_passed, pages_due)  -- derived
notification_pref(user_id, ...) ; sync_state(device_id, cursor)
consent_record(user_id, type, version, granted_at, revoked_at)
```

### 4.7 Sync
Offline-first with an event log: client writes append-only events (`review_event`, `submission`, `teacher_mark`); server assigns order; derived tables recompute. Assignments and plans are last-writer-wins with teacher precedence over student.

## 5. Automatic recitation checking

### 5.1 Pipeline
```
mic → audio capture (16 kHz mono, noise/clipping/level check)
    → voice-activity detection
    → ASR tuned for Quranic Arabic (streaming or post-hoc)
    → constrained alignment against the expected text (assigned range)
    → diff at word level → flags with confidence
    → student-facing feedback + optional teacher packet
```
Key design choice: **the expected text is known** (the assigned range), so this is *forced alignment + verification*, not open-vocabulary transcription. That is far more reliable than general ASR. For an unprompted "continue from here" test, use a small language model/lattice restricted to the Quran text (ayah-position search) to identify where the student is.

### 5.2 Models
- Base: fine-tuned Arabic/Quran ASR (e.g. Whisper-family or wav2vec2/conformer fine-tuned on Quran recitation corpora), quantized for on-device (~tens–hundreds MB); larger server model as optional fallback for uncertain cases when the user opts in.
- Decoding constrained by the assigned range plus neighboring ayahs (to catch "jumped to the similar verse" errors).
- Text normalization: compare on a diacritic-aware but tolerant basis (see §5.3 tiers).

### 5.3 What is checked, in tiers of reliability

| Tier | Check | Expected reliability | Presented as |
|---|---|---|---|
| A | Skipped/added words, wrong ayah, jumped to a similar verse, order errors | Good with clean audio; the core use case | "Possible mistake at…" |
| B | Wrong word substitution where consonantal skeleton differs | Good; degrades with accent/noise | "Possible mistake at…" |
| C | Harakat (vowel) errors, e.g. fatha vs damma, that change grammar but not skeleton | Moderate; ASR often ignores or hallucinates vowels | Low-confidence hint, never a firm error |
| D | Tajweed rules: madd length, ghunna, qalqalah, idgham, ikhfa, makharij (letter articulation), sifat | Poor to research-grade; some rules (madd duration, qalqalah presence) are partially detectable acoustically; makharij and subtle rules are not reliably detectable | "Not assessed" by default; experimental hints opt-in, clearly labeled |
| E | Waqf/ibtida choices, riwaya-specific variants, maqam/melody, overall beauty and *khushu'* | Not assessed | Teacher only |

### 5.4 Confidence handling
- Every flag has a confidence; below threshold it becomes "uncertain – please re-record or ask your teacher," never "wrong."
- Bias thresholds toward **fewer false accusations**: falsely telling a student that correct recitation is wrong is worse (undermines trust, reinforces a wrong "correction") than missing a subtle error.
- Overall result is never a bare pass/fail. Statuses: `match` (no flags found), `uncertain`, `mismatch`, `unusable_audio`. Even `match` is shown as "No word-level differences detected," not "Correct."

### 5.5 Honest limits — what automation cannot do

1. **Cannot certify correct recitation.** Absence of detected errors ≠ correct. Tajweed, makharij, and subtle vowel accuracy remain unverified. The app does not grant ijazah-type claims, and UI text avoids "perfect," "verified," or "correct" language for automated results.
2. **Cannot replace transmission (talaqqi).** Recitation is learned by hearing and being corrected by a qualified person in an unbroken chain of transmission. An app can't hold that authority.
3. **Accuracy varies by voice and conditions.** Models trained mostly on adult male professional reciters perform worse on children, women, non-native/accented speakers, dialects, and noisy rooms. This creates a fairness risk: the users who most need help get the noisiest feedback. Mitigation: evaluate by demographic slice, include diverse data, surface audio-quality warnings, report uncertainty rather than guess.
4. **Fast, elided, or whispered recitation** (hadr, tadwir styles; memorization murmuring) degrades alignment.
5. **Different valid readings (qira'at).** A student learning Warsh or Qalun against a Hafs-trained model will be flagged wrongly. Riwaya must be a per-user setting, and unsupported riwayat disable auto-check rather than run it.
6. **Prompting and hesitation.** The engine can detect long pauses and restarts but can't tell a teacher prompting from silence; it can't verify the student recited unaided.
7. **Cannot verify identity or honesty.** A student could play a recording; anti-spoofing is out of scope. Teacher review is the integrity check.
8. **Cannot assess understanding, intent, or spiritual quality.** Out of scope by design.
9. **Sacred-text sensitivity.** Machine "corrections" of Quran recitation carry religious weight; a confident wrong correction is worse than in ordinary language learning. Hence the conservative thresholds and the mandatory human path.

Communication to users: a short onboarding screen and a persistent line in the results UI: *"Automatic check is a practice aid. It can miss mistakes, especially in tajweed, and can be wrong. Your teacher's review is what counts."*

### 5.6 Measuring and improving
- Offline benchmark: held-out recordings labeled by qualified teachers (mark-level), sliced by age, gender, accent, device, noise, riwaya, and recitation speed. Report precision and recall per tier; release gates on Tier A/B precision (e.g. ≥ 95% precision at chosen operating point; target values to be set after pilot data).
- Online: compare `auto_check_flag` vs `teacher_mark` on submissions that get both; track flag acceptance ("teacher agreed"), dismissal, and missed errors. Teachers can mark a flag as "false alarm" with one tap; those become training/eval data (with consent).
- Version everything: `engine_version` on each result so old results remain interpretable.

### 5.7 How it fits the workflow
- **Student, before submitting:** immediate feedback; can re-record; only flagged-and-uncertain spots highlighted with the expected text revealed on demand (so it works as a test, not a crutch).
- **Teacher:** sees the submission with machine flags overlaid as *suggestions* on the waveform/text, can jump to them, and marks their own. Teacher can hide machine flags to avoid anchoring bias. Submissions with no flags are still sampled by the teacher; the app never lets automation auto-pass a portion.
- **Solo students:** get the same feedback with a stronger disclaimer, and passing status is limited to "practiced," not "passed"; app encourages finding a teacher (optional directory, v2).
- **Scheduling grades:** auto results feed the spaced-repetition grade with lower weight than self or teacher grades; teacher grade always overrides.

### 5.8 Privacy of recitation audio
- On-device processing by default; upload only on submit-to-teacher or explicit opt-in for server fallback.
- Retention limits (`retention_until`), e.g. auto-delete after teacher review + 30 days unless teacher/student keeps it; user-initiated deletion; encryption in transit and at rest.
- Minors: guardian consent before any upload; training use of audio is a separate opt-in, never bundled.
- Teachers only see students they are actively linked to; link end revokes access.

## 6. Key flows

**Daily student flow:** Open → today's list (sabaq, sabqi, manzil due) → do each → record → auto pre-check → submit sabaq to teacher; revision items graded locally.
**Teacher review flow:** Queue → open submission → play with flags as suggestions → mark/grade/comment → decide `passed` or `redo` → next assignment.
**Passing a portion:** Only a teacher action sets `teacher_passed_at` and moves items to the review schedule at `mature` entry level; auto or self grading cannot.

## 7. Architecture (brief)

- Client: cross-platform (Flutter or React Native) with native audio modules; SQLite; on-device inference (Core ML / TFLite / ONNX Runtime).
- Backend: REST/GraphQL API, Postgres, object storage for audio (short-lived signed URLs), push notifications, job queue for optional server-side ASR.
- Reference Quran data and models shipped as versioned, signed bundles.

## 8. Scope and phasing

**MVP:** Mushaf reader with hide modes, audio, teacher–student link, assignments, recording + submission, teacher review with marks/grades, spaced-repetition revision, progress map. Auto-check Tier A only, Hafs only, flagged beta.
**v1.x:** Tier B, mutashabihat drills, live session mode, guardian view, more reciters.
**Later:** Tier C hints, experimental tajweed (madd/qalqalah) opt-in, other riwayat, institution admin, teacher directory.

## 9. Risks and open questions

| Risk / question | Handling |
|---|---|
| Users over-trust automation | Conservative language, uncertainty states, no auto-pass |
| Model bias against children/women/accents | Sliced evaluation, diverse data, quality warnings, kill-switch per slice |
| Text errors in Quran data | Single verified source, checksum, scholarly review of release |
| Child safety | Guardian consent, no open chat, teacher verification, audit log |
| Which riwayat to support | Start Hafs; gate others |
| Teacher adoption/workload | Fast review UI, machine flags as optional aid, batch actions |
| Data for training | Consented, teacher-labeled pilot; need scholarly and community input on acceptable use |
| Scholarly/religious review | Engage qualified scholars/qurra' on UI wording, certification semantics, and the tajweed feature scope before launch |


### FINAL MESSAGE
I've written the design doc to `/tmp/eval2-baseline-n_6diqkw/design.md`. I haven't built or tested anything, and the accuracy expectations in it are design targets, not measured results.

**Teacher's role.** The teacher is the authority. Only a teacher action can mark a portion as passed. Automated and self-graded results never certify a portion.

**Core features.**
- A Mushaf reader with hide-text modes and word-highlighted audio.
- The traditional sabaq/sabqi/manzil structure (new lesson, recent revision, long-term revision), with a plan the teacher can override.
- Spaced-repetition revision, plus drills for similar verses (mutashabihat).
- A teacher review queue and live-lesson marking.
- A progress map.

**Data model.** It covers:
- Versioned Quran reference data, down to the word level.
- Teacher–student links.
- Assignments.
- An append-only review log, so state can be rebuilt after sync conflicts.
- Machine flags and teacher marks kept in separate tables, so I can compare them and measure how accurate the engine is.

**Automatic checking.** The expected text is known, so the check is forced alignment against the assigned range, not open transcription. That is much more reliable. The doc rates each kind of check by how reliable it is:

| What is checked | Expected reliability |
|---|---|
| Skipped, added or wrong words | Good |
| Wrong vowels | Moderate; shown only as a low-confidence hint |
| Tajweed | Weak; off by default and labelled experimental |
| Melody, beauty, choice of stopping points | Teacher only |

**What automation can't do.** The doc says plainly that it can't certify correct recitation, replace transmission from a teacher, or be trusted equally across voices. Accuracy is likely to be worse for children, women, accented speakers and noisy rooms. Other recitation traditions (riwayat) than Hafs will be flagged wrongly, so the app disables auto-check for them. The design also errs toward "uncertain" over falsely calling correct recitation wrong.

The doc also covers privacy (on-device by default, guardian consent for minors), a phased scope, and risks. It flags that qualified scholars should review the wording and the tajweed scope before launch.