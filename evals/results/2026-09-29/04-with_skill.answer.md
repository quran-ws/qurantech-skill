### FILE answer.md
# Tajweed colouring for your Hafs reader

## Recommendation

Use **Quran.ws `quran-tajweed`**. It ships precomputed annotation spans, not coloured text. Your JSON stays untouched and you overlay colour at render time.

- A span is `[start, end, ruleIndex]`, keyed by `"surah:ayah"`.
- `start` and `end` are half-open **code-point** offsets into one specific Hafs edition.
- The data holds no Quranic text. This means you never edit, wrap or retype the text, which is also the adab rule for sacred text.

Fit: Hafs only, 6,236 ayahs, Uthmani text. If your JSON is that edition, it works with no engine at all.

## Caveats to know first

1. **Only the data packages work today.** `@quran.ws/tajwid-rules` and `@quran.ws/tajwid-annotations` (0.1.0) are fine. `@quran.ws/tajwid` (engine) and `@quran.ws/tajwid-react` were published without a built `dist/`, so importing them fails (checked 2026-09-29). The plan below uses only the data packages plus about 60 lines of your own code. If you want the official components, build them from `packages/*` in the `quran-ws/quran-tajweed` repo.
2. **Offsets only match one exact text.** They were measured against `editions/uthmani-hafs.json` in the repo, and its SHA-256 is `annotations.edition.sha256`. If your text differs by a single code point (sukoon U+06E1 vs U+0652, precomposed U+0622 vs U+0627+U+0653), the colours land on the wrong letters. Step 1 checks this.
3. **Silence does not mean "no rule applies".** Only 7 topics are covered, and there are named gaps (for example 20:1 has no spans, and the file omits it). Two rules are disputed and 12 carry `needsReview`.
4. **I did not open the package contents.** The shape of `corpus` (how a rule id maps to its topic) is from the skill notes, not from inspecting the files. Step 3 isolates that lookup in one function. Log `corpus` once and adjust it if the field names differ.

## Steps

### 1. Install the data and verify your text (build-time check)

```bash
npm i @quran.ws/tajwid-rules @quran.ws/tajwid-annotations
git clone --depth 1 https://github.com/quran-ws/quran-tajweed   # only for editions/uthmani-hafs.json
```

The edition file is not in the npm packages. The simplest safe check is to compare your JSON to the reference edition, ayah by ayah. Adjust `yours` to your file's shape.

```js
// scripts/check-edition.mjs
import fs from 'node:fs'
const ref = JSON.parse(fs.readFileSync('quran-tajweed/editions/uthmani-hafs.json', 'utf8')).ayahs
const yours = JSON.parse(fs.readFileSync('public/quran-hafs.json', 'utf8')) // -> { "1:1": "…", … }

const bad = Object.keys(ref).filter(k => yours[k] !== ref[k])
if (Object.keys(yours).length !== 6236 || bad.length) {
  console.error(`Mismatch on ${bad.length} ayahs, first: ${bad.slice(0, 5)}`)
  process.exit(1)
}
console.log('Text matches the tajweed edition')
```

If it fails, don't force the spans. Either render the tajweed edition's text for tajweed mode, or run `@quran.ws/tajwid` (`new Tajweed(corpus).analyze(text)`) over your own text once it is built. `pnpm edition:check <file>` in the repo reports exactly which characters differ. Never normalise or retype your text to make it match.

### 2. Load the spans and check versions

```js
import corpus from '@quran.ws/tajwid-rules'
import annotations from '@quran.ws/tajwid-annotations'

if (annotations.corpusVersion !== corpus.version) console.warn('rules/annotations version skew')
// annotations.spans['1:1'] -> [[8,10,52],[17,18,22],[22,25,129],[30,31,22],[33,36,131]]
// A missing key means no spans (only 20:1).
```

### 3. Map each rule to a topic, then to a colour

Colour by **topic** (7 of them), not by all 164 rule ids. That keeps it readable, and it matches the legend you must ship.

```js
// tajweed-colours.js
export const TOPIC_COLOURS = {                       // your palette; call it yours,
  'tafkheem-tarqeeq': '#7c3aed',                     // never "the mushaf's scheme"
  'letter-relations': '#0891b2',
  'noon-tanween':     '#16a34a',
  'meem-sakinah':     '#db2777',
  'mushaddadatan':    '#ea580c',
  'madd':             '#2563eb',
  'qalqalah':         '#ca8a04',
}
export const TOPIC_LABELS_EN = {                     // corpus labels are Arabic only
  'tafkheem-tarqeeq': 'Heavy / light letters',
  'letter-relations': 'Letter relations',
  'noon-tanween':     'Noon sakinah & tanween',
  'meem-sakinah':     'Meem sakinah',
  'mushaddadatan':    'Shaddah letters',
  'madd':             'Madd (prolongation)',
  'qalqalah':         'Qalqalah',
}

// The only place that touches the corpus shape. Verify against the real object.
export function topicOfRuleIndex(corpus, annotations, i) {
  const ruleId = annotations.ruleIds[i]              // e.g. "mutamathilain-idgham-kamil.23"
  return corpus.rules[ruleId]?.topicId               // <- adjust if the field names differ
}
```

### 4. Turn spans into runs (the actual rendering logic)

Text is split into runs, and each run gets one colour. Three details matter, and each one is a known pitfall:

- **Index by code point**: `[...text]`, never UTF-16 `slice`.
- **Extend each boundary past combining marks**. A span ends on the letter, so without this the shadda or harakat would be left uncoloured or split off.
- **Bridge joins**. A browser shapes each element separately, so a colour change in the middle of a word breaks the Arabic joining. Add a ZWJ (U+200D) on both sides of a cut, but only where the letter before joins forward and the letter after joins back. Non-joiners are ء آ أ ؤ إ ا ة د ذ ر ز و ٱ.

```js
// tajweed-runs.js
const MARK = /\p{Mn}/u
const WAQF = c => c >= 'ۖ' && c <= 'ۜ'      // waqf signs keep the surrounding colour
const NO_FORWARD_JOIN = new Set([...'ءآأؤإادذرزوةٱ'])  // letters that never join to the next one

// Approximation of the engine's clusterEnd: move past marks that belong to the base letter.
function clusterEnd(cps, i) {
  while (i < cps.length && MARK.test(cps[i]) && !WAQF(cps[i])) i++
  return i
}

const isLetter = c => /\p{L}/u.test(c)
function baseBefore(cps, i) { for (let k = i - 1; k >= 0; k--) if (isLetter(cps[k])) return cps[k]; }
function baseAfter(cps, i)  { for (let k = i; k < cps.length; k++) if (isLetter(cps[k])) return cps[k]; }

/** -> [{ text, topic|null, joinStart, joinEnd }] covering the whole ayah, text unchanged. */
export function toRuns(text, spans, topicOf) {
  const cps = [...text]
  // Flat colouring: the first span covering a position wins.
  // Overlaps are normal (1:6 has eleven spans).
  const topicAt = new Array(cps.length).fill(null)
  for (const [s, e, r] of spans) {
    const end = clusterEnd(cps, e)
    for (let i = s; i < end; i++) topicAt[i] ??= topicOf(r)
  }
  const runs = []
  let from = 0
  for (let i = 1; i <= cps.length; i++) {
    // Only break before a base letter, so marks never start a run.
    const atBoundary = i === cps.length || (isLetter(cps[i]) && topicAt[i] !== topicAt[from])
    if (!atBoundary) continue
    const prev = baseBefore(cps, i), next = baseAfter(cps, i)
    const joins = prev && next && !NO_FORWARD_JOIN.has(prev) && i < cps.length
    runs.push({ text: cps.slice(from, i).join(''), topic: topicAt[from], joinEnd: joins, joinStart: false })
    if (joins) runs.at(-1).joinEnd = true
    from = i
  }
  // The ZWJ after a cut also has to lead the next run.
  runs.forEach((r, k) => { if (k > 0 && runs[k - 1].joinEnd) r.joinStart = true })
  return runs
}
```

Overlaps are flattened above with first-wins. That is simplest for reading. For a learning mode, keep every span and show all of them in a tooltip. The engine's `resolveOverlaps` gives a principled flattening once it is built.

### 5. Render, without touching the text

Joiners are for drawing only. Keep them out of the DOM text nodes you copy from, out of offsets and out of counts. Wrap each ZWJ in an `aria-hidden` span with `user-select: none`, as below. Test in your target browsers that copying an ayah returns the original text.

```tsx
// TajweedAyah.tsx
import { toRuns } from './tajweed-runs'
import { TOPIC_COLOURS, TOPIC_LABELS_EN, topicOfRuleIndex } from './tajweed-colours'
import corpus from '@quran.ws/tajwid-rules'
import annotations from '@quran.ws/tajwid-annotations'

const ZWJ = <span aria-hidden data-zwj style={{ userSelect: 'none' }}>{'‍'}</span>

export function TajweedAyah({ ayahKey, text, tajweed }: { ayahKey: string; text: string; tajweed: boolean }) {
  if (!tajweed) return <span dir="rtl" lang="ar">{text}</span>
  const spans = annotations.spans[ayahKey] ?? []
  const runs = toRuns(text, spans, r => topicOfRuleIndex(corpus, annotations, r))
  return (
    <span dir="rtl" lang="ar">
      {runs.map((r, i) => (
        <span
          key={i}
          style={r.topic ? { color: TOPIC_COLOURS[r.topic] } : undefined}
          title={r.topic ? TOPIC_LABELS_EN[r.topic] : undefined}
          aria-label={r.topic ? `${r.text}, ${TOPIC_LABELS_EN[r.topic]}` : undefined}  /* colour is never the only signal */
        >
          {r.joinStart && ZWJ}{r.text}{r.joinEnd && ZWJ}
        </span>
      ))}
    </span>
  )
}

export function TajweedLegend() {
  return (
    <ul>
      {Object.entries(TOPIC_COLOURS).map(([id, c]) => (
        <li key={id}><span style={{ color: c }}>■</span> {TOPIC_LABELS_EN[id]}</li>
      ))}
      <li>Uncoloured: no rule from these 7 topics applies, <em>or</em> it isn't covered yet.</li>
    </ul>
  )
}
```

Not React? `toRuns` is framework-free. Emit `<span style="color:…">` nodes with `textContent` (never `innerHTML`) in the same way.

### 6. Product details that should not be skipped

- **Always ship the legend** (above). Give it a toggle, with plain text as the default, so the reader can turn tajweed off.
- **Colour must not be the only signal.** The `title` and `aria-label` above carry the rule name.
- **Use your own palette and say so.** Don't present it as a printed mushaf's scheme.
- **Label it as a study aid**, not a substitute for a qualified teacher. Add a short note about the disputed and `needsReview` rules (`qalqalah-kubra.1`, `madd-lazim-harfi.1`) if you name those rulings.
- **Attribution.** The corpus, annotations and editions are CC BY 4.0, so add a credit line ("Tajweed data: Quran.ws quran-tajweed, CC BY 4.0"). The code packages are MIT.
- **Font.** Make sure your Arabic font handles the marks well (KFGQPC Hafs or Amiri Quran). Test 1:1 and a shaddah-heavy ayah and check that the joining stays unbroken across colour changes.
- **Cache.** Lazy-load `annotations` (about 1.8 MB) only when tajweed mode is on, and tie any cache key to `annotations.edition.sha256`.

### 7. Test

- Run `check-edition.mjs` in CI, so a text edit can never silently misalign colours.
- Snapshot 1:1 with `[[8,10,52],[17,18,22],[22,25,129],[30,31,22],[33,36,131]]`. Check that `runs.map(r => r.text).join('')` equals the original text, code point for code point. This is the invariant that proves the text is never altered.
- Check a word split across two colours and confirm it still looks joined.

## Not covered

- **Mushaf page images (quran-svg / quran-svg-elements).** Spans address characters, not printed shapes, and no documented mapping exists. This approach is for the text view only.
- **Other riwayat (Warsh etc.)** are unsupported.

## Later upgrade path

When a fixed `@quran.ws/tajwid` / `tajwid-react` release ships (re-check with `npm view`), swap steps 3–5 for `unpack`, `assertEdition`, `<TajweedText>` and `<TajweedLegend>`. Steps 1–2 and the palette stay as they are.


### FINAL MESSAGE
I wrote the plan and code to `/tmp/eval4-with_skill-lsg44pix/answer.md`. I haven't run any of the code, and I didn't open the packages to check the data shapes.

**Approach.** Use the Quran.ws `quran-tajweed` annotation data. It stores spans as `[start, end, ruleIndex]` per `"surah:ayah"`, so your JSON text is never edited and colour is added when the page renders.

**Steps in the file:**
1. Compare your JSON to the reference edition (`editions/uthmani-hafs.json` in the `quran-ws/quran-tajweed` repo) in a build or CI check. The spans only line up with that exact text, and a one-character difference puts colours on the wrong letters.
2. Install `@quran.ws/tajwid-rules` and `@quran.ws/tajwid-annotations`, and check their versions match.
3. Map each rule to one of the 7 topics and give each topic your own colour. The colours are a palette you choose, not a printed mushaf's scheme.
4. Turn spans into coloured runs. Index by code point and move each boundary past the letter's marks so shadda and harakat stay with their letter. Add a joiner character (ZWJ) at each cut so words stay joined across a colour change.
5. Render with a React component plus a legend. Each run carries an `aria-label` and title, so colour isn't the only signal.
6. Product details: a legend, a toggle to turn tajweed off, a CC BY 4.0 credit, and a note that this is a study aid.
7. Tests: check that the runs joined back together equal the original text, code point for code point.

**Caveats:**
- **Broken packages.** The npm engine and React packages (`@quran.ws/tajwid`, `@quran.ws/tajwid-react`) were published without built files, so importing them fails. The plan uses only the two data packages plus about 60 lines of your own code. The file describes swapping in the official components once a fixed release ships.
- **Unchecked data shape.** I didn't open the rules package, so the rule-to-topic lookup in step 3 is a guess at the field names. It sits in one function, `topicOfRuleIndex`, so it's easy to adjust.
- **Approximate helpers.** My `clusterEnd` and joiner logic approximate the official engine's versions. Test them on ayah 1:1 and on a shaddah-heavy ayah.
- **Gaps in the data.** An uncoloured word doesn't mean no rule applies. Only 7 topics are covered, and ayah 20:1 has no spans.
- **Not for page images.** Spans address characters, not printed shapes, so this doesn't work on SVG mushaf pages, and it is Hafs only.

I also renamed the React prop `ref` to `ayahKey`, because React reserves `ref`.