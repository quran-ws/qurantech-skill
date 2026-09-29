### FILE answer.md
# Tajweed colouring for a Hafs JSON Quran reader

(Your working directory was empty, so I couldn't see your code. Adapt names to your app.)

## Recommendation: stand-off annotations + a small renderer

Keep your text JSON untouched. Add a second file that says, per ayah, "characters
`start`–`end` follow rule X". At render time, split the ayah into spans and give each
span a CSS class. Colours live only in CSS.

Why this beats the alternatives:

| Option | Problem |
|---|---|
| Write tajweed rules yourself | Ghunnah, ikhfa, idgham, qalqalah, madd lengths and stop-dependent rules are hard to get right. Don't do it unless you have to. |
| Pre-tagged HTML (e.g. Quran.com's `text_uthmani_tajweed`) | Replaces your text with theirs, mixes markup into data, and is awkward to re-style. |
| Colour-tajweed fonts (QPC / COLR) | Needs their page-specific glyph text, not your JSON. |
| **Stand-off annotations** | Text stays yours, colours are pure CSS, and the data is replaceable. |

## Step 1: get annotation data

Use an existing open dataset rather than generating one. A good candidate is
`cpfair/quran-tajweed` on GitHub. It ships per-ayah annotations shaped roughly like:

```json
{ "surah": 1, "ayah": 1,
  "annotations": [ { "rule": "madd_2", "start": 9, "end": 10 } ] }
```

Check the repo's README for the exact schema, licence, and rule names. I'm going from
memory, so verify them.

**Critical caveat:** offsets index into *that dataset's* text (Tanzil Uthmani, I believe).
If your JSON uses a different encoding (different diacritic order, extra marks, a
different Alef Wasla or small-mark convention), the offsets will drift. Before trusting it:

1. Compare each ayah in your file with the dataset's text.
2. If they are identical, use the offsets directly.
3. If not, either switch your reader's text to the dataset's text, or write a one-time
   script that maps offsets between the two by aligning on base letters.

Also confirm whether offsets are Unicode code points or UTF-16 units. The code below
assumes code points. Arabic marks are all in the BMP, so both are usually the same, but check.

Save the data as `tajweed.json` and index it by key:

```js
// tajweed.json: array of {surah, ayah, annotations:[{rule,start,end}]}
const tajweed = new Map();
for (const a of await (await fetch('/tajweed.json')).json()) {
  tajweed.set(`${a.surah}:${a.ayah}`, a.annotations);
}
```

## Step 2: renderer

`end` is treated as exclusive here. Verify this against your dataset and adjust if it is inclusive.

```js
function escapeHtml(s) {
  return s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

// Returns a DocumentFragment so no innerHTML is needed.
function renderAyah(text, annotations = []) {
  const chars = Array.from(text);            // code points
  // Per-character rule; later annotations win on overlap.
  const ruleAt = new Array(chars.length).fill(null);
  for (const { rule, start, end } of annotations) {
    for (let i = start; i < Math.min(end, chars.length); i++) ruleAt[i] = rule;
  }

  const frag = document.createDocumentFragment();
  let i = 0;
  while (i < chars.length) {
    let j = i + 1;
    while (j < chars.length && ruleAt[j] === ruleAt[i]) j++;
    const chunk = chars.slice(i, j).join('');
    if (ruleAt[i]) {
      const span = document.createElement('span');
      span.className = `tj tj-${ruleAt[i]}`;
      span.textContent = chunk;
      frag.append(span);
    } else {
      frag.append(chunk);
    }
    i = j;
  }
  return frag;
}
```

Usage inside your existing render loop:

```js
ayahEl.replaceChildren(renderAyah(ayah.text, tajweed.get(`${surah}:${ayah.number}`)));
```

Use one span per run of characters. Don't wrap each letter separately, because that can
break Arabic joining/shaping in some browsers. Even with runs, a span boundary that falls
mid-word can occasionally interrupt shaping. If you see that, check that the boundary is
between letter+marks clusters rather than between a letter and its diacritic.

## Step 3: CSS (single source of truth for colours)

Rule names must match your dataset. These are typical:

```css
:root {
  --tj-ghunnah: #ff7e1e;
  --tj-ikhfa: #9400a8;
  --tj-idgham: #169200;
  --tj-iqlab: #26bffd;
  --tj-qalqalah: #dd0008;
  --tj-madd: #d500b7;
  --tj-silent: #aaaaaa;
}
.tj-ghunnah                 { color: var(--tj-ghunnah); }
.tj-ikhfa, .tj-ikhfa_shafawi { color: var(--tj-ikhfa); }
.tj-idgham_ghunnah, .tj-idgham_wo_ghunnah,
.tj-idgham_mutajanisayn, .tj-idgham_mutaqaribayn,
.tj-idgham_shafawi          { color: var(--tj-idgham); }
.tj-iqlab                   { color: var(--tj-iqlab); }
.tj-qalqalah                { color: var(--tj-qalqalah); }
.tj-madd_2, .tj-madd_246, .tj-madd_45, .tj-madd_6,
.tj-madd_munfasil, .tj-madd_muttasil { color: var(--tj-madd); }
.tj-ham_wasl, .tj-slnt, .tj-laam_shamsiyah { color: var(--tj-silent); }

@media (prefers-color-scheme: dark) {
  :root { --tj-silent: #777; }   /* tune each colour for contrast on dark */
}
.tajweed-off .tj { color: inherit; }   /* toggle */
```

## Step 4: toggle and legend

```html
<label><input type="checkbox" id="tj-toggle" checked> Tajweed colours</label>
```
```js
document.getElementById('tj-toggle').addEventListener('change', e =>
  document.body.classList.toggle('tajweed-off', !e.target.checked));
```

Because the toggle is just a class on `<body>`, switching it costs nothing and needs no re-render.
Build the legend from the same CSS variables so it can't drift out of sync.

## Step 5: sanity checks

- Test Al-Fatihah 1:1 and a few ayat with known rules (e.g. 2:1 for madd, 112:1 for qalqalah).
- Assert on load that every annotation's `end <= Array.from(text).length`. A mismatch means the text differs from the dataset's, so stop and fix the alignment (Step 1).
- Make sure you don't rely on colour alone: keep a legend, and consider a mode that underlines rules, for colour-blind readers.

## If you can't find a dataset that fits

Write a rule engine only for the few rules that are mechanical (noon sakinah/tanween
before letter groups, meem sakinah, qalqalah letters with sukun, laam shamsiyah, ham wasl).
Output the same `{rule,start,end}` shape, so the renderer and CSS stay identical. Leave the
madd lengths and stop-dependent rules to a dataset.


### FINAL MESSAGE
I wrote the answer to `answer.md`. Your working directory was empty, so I couldn't see your reader's code and the snippets use placeholder names. I haven't run any of the code or checked the external dataset. Its schema, offset convention and licence are from memory and need checking.

**Recommendation:** keep your Hafs JSON as it is and add a separate file of per-ayah annotations. Each annotation is `{rule, start, end}`, and the renderer splits the ayah into `<span class="tj tj-RULE">` runs. All colours live in CSS variables, so a dark theme, a legend and an on/off toggle (a class on `<body>`) need no re-render.

I'd take the annotation data from an existing open dataset such as `cpfair/quran-tajweed` rather than writing tajweed rules yourself. Most rules are hard to get right, especially madd lengths and stop-dependent rules.

**Caveat:** the offsets only line up if your text is character-for-character the same as the text the dataset was built from. The answer includes a check to run first, and a one-time alignment script if your text differs.

`answer.md` covers:
1. Getting the data and verifying alignment.
2. The renderer, in about 25 lines of vanilla JS that build DOM nodes rather than HTML strings.
3. The CSS, toggle and legend.
4. Sanity checks.
5. A fallback: a small rule engine for only the mechanical rules, producing the same annotation shape.

If you share your repo layout or the JSON schema, I can adapt the code to it.