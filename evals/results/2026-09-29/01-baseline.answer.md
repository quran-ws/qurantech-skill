### FILE answer.md
# Quran verses + tap-for-tafsir in WordPress (no backend, no plugin to maintain)

## The idea

- Use the **free public Quran.com API** (`api.quran.com`). It serves both the Uthmani verse text and several Arabic tafsirs, and it allows browser requests (CORS).
- Add **one small JavaScript snippet** and **one CSS snippet** to your site, once.
- In a post you only type a marker, e.g. `{{2:255}}` or `{{2:255-257}}`, in a normal paragraph.
- The script replaces each marker with the verse in a nice Arabic font. Tapping the verse opens its tafsir underneath, on the same page.

No server, no custom plugin, no shortcodes, and nothing to update when you write new posts.

> I couldn't run the code against the live API from where I wrote this, so do the 2-minute check in Step 0 before relying on it.

---

## Step 0 – Check the API and pick your tafsirs (2 min)

Open these in your browser:

1. List Arabic tafsirs and their IDs: `https://api.quran.com/api/v4/resources/tafsirs?language=ar`
2. Test a verse: `https://api.quran.com/api/v4/quran/verses/uthmani?verse_key=2:255`
3. Test a tafsir (replace 16 with an ID from the list): `https://api.quran.com/api/v4/tafsirs/16/by_ayah/2:255`

Each should return JSON. From memory, the IDs are roughly: `16` Al-Muyassar, `14` Ibn Kathir, `15` Al-Tabari, `90` Al-Qurtubi, `91` Al-Sa'di, `94` Al-Baghawi. **Trust the list in item 1, not my memory.** Then edit the `TAFSIRS` list in the script below.

## Step 1 – Add the CSS

WordPress admin → **Appearance → Customize → Additional CSS** (block themes: **Appearance → Editor → Styles → ⋮ → Additional CSS**). Paste:

```css
@import url('https://fonts.googleapis.com/css2?family=Amiri+Quran&family=Amiri&display=swap');

.ayah-block {
  margin: 1.5em 0;
  border-right: 4px solid #2e7d5b;
  background: #f6faf8;
  border-radius: 8px;
  overflow: hidden;
  direction: rtl;
}
.ayah-verse {
  display: block;
  width: 100%;
  padding: 1em 1.2em;
  font-family: 'Amiri Quran', 'Amiri', serif;
  font-size: 1.6em;
  line-height: 2.2;
  text-align: right;
  background: none;
  border: 0;
  color: inherit;
  cursor: pointer;
}
.ayah-verse:hover, .ayah-verse:focus-visible { background: #eaf3ef; }
.ayah-num {
  font-family: 'Amiri', serif;
  font-size: .6em;
  color: #2e7d5b;
  margin-inline-start: .4em;
  white-space: nowrap;
}
.ayah-hint { font-size: .55em; color: #7a8a83; font-family: sans-serif; display: block; }
.ayah-tafsir {
  display: none;
  padding: .8em 1.2em 1.2em;
  border-top: 1px dashed #b9d3c8;
  font-family: 'Amiri', serif;
  font-size: 1.15em;
  line-height: 2;
  text-align: right;
}
.ayah-block.open .ayah-tafsir { display: block; }
.ayah-tafsir select { font-family: inherit; margin-bottom: .6em; max-width: 100%; }
.ayah-tafsir-body p { margin: 0 0 .6em; }
.ayah-error { color: #a33; font-size: .9em; }
```

## Step 2 – Add the JavaScript once, site-wide

A theme has no built-in place for site-wide JS, so pick one:

- **Easiest:** install the free **WPCode – Insert Headers and Footers** plugin (maintained by others, so no upkeep for you). Go to *Code Snippets → Add Snippet → Add Your Custom Code → JavaScript Snippet*, paste the code below, set location **Site Wide Footer**, and activate.
- **No plugin:** if you use a child theme, add it in `footer.php` before `</body>` inside `<script>…</script>`.
- **Per-post only:** paste it (wrapped in `<script>…</script>`) into a *Custom HTML* block in a post. This works but you'd repeat it in every post.

```js
(function () {
  // ---- Settings you can edit ------------------------------------------------
  // id = Quran.com tafsir ID (see Step 0). First one is the default.
  var TAFSIRS = [
    { id: 16, name: 'التفسير الميسر' },
    { id: 14, name: 'تفسير ابن كثير' },
    { id: 91, name: 'تفسير السعدي' },
    { id: 90, name: 'تفسير القرطبي' }
  ];
  var CONTENT_SELECTOR = '.entry-content, .wp-block-post-content, .post-content';
  var MAX_VERSES_PER_MARKER = 15;
  // ---------------------------------------------------------------------------

  var API = 'https://api.quran.com/api/v4';
  var MARKER = /\{\{\s*([0-9٠-٩]+)\s*:\s*([0-9٠-٩]+)(?:\s*[-–—]\s*([0-9٠-٩]+))?\s*\}\}/g;

  function toInt(s) {
    return parseInt(String(s).replace(/[٠-٩]/g, function (d) {
      return d.charCodeAt(0) - 1632;
    }), 10);
  }
  function arNum(n) {
    return String(n).replace(/[0-9]/g, function (d) { return '٠١٢٣٤٥٦٧٨٩'[d]; });
  }

  // Small cached fetch (localStorage) so each verse/tafsir is downloaded once per reader.
  function getJSON(url) {
    var key = 'ayah:' + url;
    try {
      var c = localStorage.getItem(key);
      if (c) return Promise.resolve(JSON.parse(c));
    } catch (e) {}
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    }).then(function (j) {
      try { localStorage.setItem(key, JSON.stringify(j)); } catch (e) {}
      return j;
    });
  }

  // Strip anything dangerous from third-party HTML before inserting it.
  function sanitize(html) {
    var doc = new DOMParser().parseFromString(html || '', 'text/html');
    doc.querySelectorAll('script,style,iframe,object,embed,link,meta,form').forEach(function (n) { n.remove(); });
    doc.querySelectorAll('*').forEach(function (el) {
      Array.prototype.slice.call(el.attributes).forEach(function (a) {
        if (/^on/i.test(a.name) || /^\s*javascript:/i.test(a.value)) el.removeAttribute(a.name);
      });
    });
    return doc.body.innerHTML;
  }

  function buildVerse(surah, ayah) {
    var key = surah + ':' + ayah;
    var block = document.createElement('div');
    block.className = 'ayah-block';
    block.lang = 'ar';

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'ayah-verse';
    btn.setAttribute('aria-expanded', 'false');
    btn.textContent = '…';

    var panel = document.createElement('div');
    panel.className = 'ayah-tafsir';

    var select = document.createElement('select');
    TAFSIRS.forEach(function (t) {
      var o = document.createElement('option');
      o.value = t.id; o.textContent = t.name;
      select.appendChild(o);
    });
    var body = document.createElement('div');
    body.className = 'ayah-tafsir-body';
    panel.appendChild(select);
    panel.appendChild(body);
    block.appendChild(btn);
    block.appendChild(panel);

    getJSON(API + '/quran/verses/uthmani?verse_key=' + key).then(function (j) {
      var text = j.verses && j.verses[0] && j.verses[0].text_uthmani;
      if (!text) throw new Error('no text');
      btn.innerHTML = '';
      btn.appendChild(document.createTextNode(text));
      var num = document.createElement('span');
      num.className = 'ayah-num';
      num.textContent = '﴿' + arNum(surah) + ':' + arNum(ayah) + '﴾';
      btn.appendChild(num);
      var hint = document.createElement('span');
      hint.className = 'ayah-hint';
      hint.textContent = 'اضغط لعرض التفسير';
      btn.appendChild(hint);
    }).catch(function () {
      btn.textContent = 'تعذّر تحميل الآية ' + key;
    });

    function loadTafsir() {
      body.textContent = 'جارٍ التحميل…';
      getJSON(API + '/tafsirs/' + select.value + '/by_ayah/' + key).then(function (j) {
        var html = j.tafsir && j.tafsir.text;
        if (!html) { body.innerHTML = '<span class="ayah-error">لا يوجد تفسير لهذه الآية في هذا الكتاب.</span>'; return; }
        body.innerHTML = sanitize(html);
      }).catch(function () {
        body.innerHTML = '<span class="ayah-error">تعذّر تحميل التفسير، حاول لاحقًا.</span>';
      });
    }

    var loaded = false;
    btn.addEventListener('click', function () {
      var open = block.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open && !loaded) { loaded = true; loadTafsir(); }
    });
    select.addEventListener('change', loadTafsir);
    return block;
  }

  function processElement(el) {
    if (!MARKER.test(el.textContent)) return;
    MARKER.lastIndex = 0;
    // Only handle markers that are the whole paragraph, e.g. <p>{{2:255}}</p>
    var m = /^\s*\{\{[^}]+\}\}\s*$/.test(el.textContent);
    if (!m) return;
    MARKER.lastIndex = 0;
    var parts = MARKER.exec(el.textContent);
    MARKER.lastIndex = 0;
    if (!parts) return;
    var surah = toInt(parts[1]), from = toInt(parts[2]);
    var to = parts[3] ? toInt(parts[3]) : from;
    if (to < from) to = from;
    if (to - from + 1 > MAX_VERSES_PER_MARKER) to = from + MAX_VERSES_PER_MARKER - 1;

    var wrap = document.createDocumentFragment();
    for (var a = from; a <= to; a++) wrap.appendChild(buildVerse(surah, a));
    el.replaceWith(wrap);
  }

  function init() {
    document.querySelectorAll(CONTENT_SELECTOR).forEach(function (root) {
      root.querySelectorAll('p, div.wp-block-paragraph').forEach(processElement);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
```

## Step 3 – Use it in posts

In the editor, add a normal **Paragraph** block containing **only** the marker:

```
{{2:255}}
```

A range of verses (each verse gets its own tap-for-tafsir box):

```
{{2:255-257}}
```

Arabic digits also work: `{{٢:٢٥٥}}`. Keep the marker alone in its own paragraph, and write your own commentary in the paragraphs around it.

## Troubleshooting

- **The marker shows as plain text:** the script isn't loading. View the page source and search for `ayah-block`. Check that the snippet is active and set to *Site Wide Footer*. Caching plugins may need a cache clear.
- **"تعذّر تحميل الآية":** open the Step 0 test URL. If it fails there too, the API is down or blocked for that verse key.
- **Tafsir says none for this ayah:** some tafsirs group several verses, or omit some, so try another book in the dropdown.
- **WordPress.com free/Personal plans** don't allow custom JS. You need the Business plan, or you can move to self-hosted WordPress.
- **Reader privacy and load:** requests go straight from the reader's browser to Quran.com, and results are cached in the reader's `localStorage`. If your traffic grows a lot, be considerate of their free service. A donation or a bulk-download-based static copy is the next step, and it still needs no backend.
- **Attribution:** it's good practice to add a line in your footer, e.g. "نص القرآن والتفاسير من Quran.com".


### FINAL MESSAGE
I've written the guide to `/tmp/eval1-baseline-hjmw5rtz/answer.md`. I couldn't test it against the live Quran.com API from here, so the code is untested and the tafsir IDs in it come from my memory.

**The approach:**
- **Source:** the free Quran.com API supplies the Uthmani verse text and several Arabic tafsirs. Reader browsers call it directly, so you need no backend.
- **In your posts:** you type `{{2:255}}` or `{{2:255-257}}` on its own line in a normal paragraph. Arabic digits also work.
- **What readers see:** a script replaces each marker with the verse in the Amiri Quran font. Tapping the verse opens its tafsir below it, with a dropdown to switch between tafsir books. Results are cached in the reader's browser.
- **Setup:** paste the CSS into Appearance → Customize → Additional CSS. Add the JavaScript once, site-wide. The easiest way is the free WPCode plugin, which someone else maintains. A child theme's `footer.php` also works.

**Before you rely on it:**
- **Step 0 in the file:** it has three URLs to open in your browser. They check that the API responds and list the real Arabic tafsir IDs. Update the `TAFSIRS` list in the script from that list if my IDs are off.
- **WordPress.com plan:** custom JavaScript isn't allowed on the free and Personal plans. You'd need the Business plan or self-hosted WordPress.

The file also has a short troubleshooting section and a suggested attribution line for your footer.