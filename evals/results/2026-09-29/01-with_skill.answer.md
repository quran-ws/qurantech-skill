### FILE answer.md
# آيات وتفسير داخل مقالات ووردبريس — بلا backend ولا plugin

## The easiest way: QuranPedia's embed widget

QuranPedia hosts an embed service, so you write no backend and keep no plugin. You add one `<script>` line to your site. After that, each verse in a post is a small HTML snippet that you paste into a **Custom HTML** block.

- The Quran text comes from their verified data and is drawn with proper Quranic fonts. You never type or paste the verse yourself, which is what you want for adab. A typo in a verse can't happen.
- The tafsir is in the same widget. Readers tap and read it inside the post.
- The widget can also show i'rab, qira'at, asbab al-nuzul and translations if you ever want them.
- You can match your blog's colours with URL parameters.

Two modes, and you can mix them:

| Mode | What the reader sees | Use it for |
|------|---------------------|-----------|
| **Block** | The verse is displayed in the post, with tafsir and other sections a tap away, in an auto-sized frame | The main verse you are explaining |
| **Link** | Your own words are a link. A tap opens a modal with the verse and its tafsir | A reference in the middle of a sentence, e.g. «كما في آية الكرسي» |

## Step 1: Load the script once, site-wide

Add this to every page. Do it once, not in each post.

```html
<script src="https://quranpedia.net/embed.js" defer></script>
```

Pick one way to add it:

1. **Block theme (Site Editor):** the editor can't add a global `<script>`, so use option 2 or 3.
2. **Child theme `functions.php`** (no plugin, ~5 lines):
   ```php
   add_action('wp_footer', function () {
       echo '<script src="https://quranpedia.net/embed.js" defer></script>';
   });
   ```
   Use a **child theme**, or a theme update will erase it.
3. **A header/footer snippet plugin** (WPCode, "Insert Headers and Footers", etc.), if you don't want to touch PHP. It is a plugin, but you set it once and never touch it again.

Note: on WordPress.com, custom scripts need a Business plan or higher. Self-hosted WordPress has no such limit.

## Step 2: Add a verse to a post

In the editor, add a **Custom HTML** block (`/html`) and paste one of these.

### A. Verse shown in the post, tafsir on tap (block mode)

Example: Ayat al-Kursi, surah 2, ayah 255.

```html
<div data-quranpedia-embed
     data-surah="2" data-ayah="255"
     data-theme="light" data-bg="transparent"></div>
```

With no `data-type`, the widget shows the verse and a grid of cards (tafsir, i'rab, qira'at, asbab and others). The reader taps **التفسير** and it opens inside the frame.

To show only the tafsir cards, add `data-options="tafsir"`:

```html
<div data-quranpedia-embed
     data-surah="2" data-ayah="255"
     data-options="tafsir"></div>
```

To open the tafsir directly and stop the reader from navigating away from it, use `data-type="tafsir"` and `data-lock="1"`:

```html
<div data-quranpedia-embed
     data-surah="2" data-ayah="255"
     data-type="tafsir" data-lock="1"></div>
```

### B. A range of verses

Ranges work up to **20 ayahs**. Longer ranges are silently cut to 20, so split them across several blocks.

```html
<div data-quranpedia-embed data-surah="103" data-ayah="1-3"></div>
```

### C. Inline reference that opens a modal (link mode)

```html
كما في <a href="https://quranpedia.net/embed?surah=2&ayah=255"
   data-quranpedia-link data-surah="2" data-ayah="255">آية الكرسي</a>
```

If JavaScript fails, the link still works as a normal link. Your own link text is just a reference name, so you are not retyping any verse.

## Step 3: Match your blog's look

Every `data-*` attribute is passed to the widget as a URL parameter of the same name. Underscores become dashes, so `ayah_text` is `data-ayah-text`.

| Attribute | Values | Effect |
|-----------|--------|--------|
| `data-theme` | `light`, `dark`, `sepia` | Base colours |
| `data-primary` | hex without `#`, e.g. `0ea5e9` | Accent colour |
| `data-bg` | hex without `#`, or `transparent` | Background (`transparent` blends into your page) |
| `data-size` | 80–130 | Text size, in % |
| `data-radius` | `none`, `sm`, `default` | Corner rounding |
| `data-height` | number | Starting height in px (default 420). It resizes itself afterwards. |

Example that blends with a dark theme:

```html
<div data-quranpedia-embed data-surah="2" data-ayah="255"
     data-theme="dark" data-bg="transparent" data-primary="c9a227"
     data-radius="none"></div>
```

There is an interactive builder at `quranpedia.net/embed-builder` and docs at `quranpedia.net/embed-docs`. Use the builder to preview a look, then copy the attributes.

## Optional: a shortcode so you type less

If pasting HTML for every verse gets tedious, add this to your child theme's `functions.php`. It gives you `[ayah 2:255]` and `[ayah 103:1-3]`.

```php
add_shortcode('ayah', function ($atts) {
    $ref = isset($atts[0]) ? $atts[0] : '';
    if (!preg_match('/^(\d{1,3}):(\d{1,3}(?:-\d{1,3})?)$/', $ref, $m)) {
        return '';
    }
    return sprintf(
        '<div data-quranpedia-embed data-surah="%d" data-ayah="%s" data-bg="transparent"></div>',
        (int) $m[1],
        esc_attr($m[2])
    );
});
```

This is about 10 lines, and you don't have to maintain it. It is still optional; the Custom HTML block works without it.

## Things to know before you rely on it

1. **It depends on a third party.** If quranpedia.net is down, the frames don't load. Their bad-parameter pages are friendly and themed, so a wrong reference looks intentional and not broken. For inline references, use link mode: the plain link still works without JavaScript.
2. **Don't rely on paste-to-embed.** WordPress won't turn a pasted QuranPedia URL into an embed by itself. Their `/oembed` endpoint works, but no discovery tags were found, and WordPress would need the provider added to its allowlist. Use the snippets above.
3. **Some parameters are undocumented.** `data-lock`, `data-options`, `mushaf` and `fonts` were observed working, but the docs don't list them. They may change. I have not tested them on your site, so preview each embed once after you publish.
4. **Riwayah:** the default is Hafs. If a post is about another riwayah, ayah numbers can differ between counting systems, so check the numbers before you cite them.
5. **Keep tafsir and translation separate.** If you turn on translations, keep them labelled «ترجمة معاني القرآن», and never present them as the Quran itself. The widget does this for you; don't put your own translation text next to the verse without the label.
6. **Don't retype verses in your own text.** Quote by reference (سورة:آية). If you write a verse by hand, a missing diacritic or a wrong character can change the text.
7. **Performance:** each block loads an iframe. If a post has many verses, prefer link mode for the minor ones and block mode for the main two or three. Add `data-fonts="0"` only if your theme already loads a Quranic font; otherwise leave fonts on.
8. **Ranges over 20 ayahs** are cut to 20 without warning. Split long passages.

## Quick checklist

1. Add the script once (child theme `functions.php` or a snippet plugin).
2. In each post, add a Custom HTML block with a `data-quranpedia-embed` div (or a link with `data-quranpedia-link`).
3. Preview the post, tap the tafsir card, and check that a bad reference (e.g. `ayah="999"`) shows the friendly not-found page.
4. Adjust the theme, colour and size with `data-*` attributes.

That is everything. There is no server to run, no database and no plugin to keep updated.


### FINAL MESSAGE
I wrote the answer to `/tmp/eval1-with_skill-p6f65sxf/answer.md`. I haven't tested any of the snippets on a live WordPress site. The recommendation comes from the skill's QuranPedia reference notes, not from a run of my own.

**The approach:** use QuranPedia's hosted embed widget. It needs no backend and no plugin. The verse text comes from their verified data and is drawn with proper Quranic fonts, so you never type or paste a verse yourself.

**Setup:**
1. Add one line, `<script src="https://quranpedia.net/embed.js" defer></script>`, once for the whole site. The file shows three ways to do it. The plugin-free one is a short snippet in a child theme's `functions.php`.
2. In each post, paste a `<div data-quranpedia-embed data-surah="2" data-ayah="255"></div>` into a Custom HTML block. It shows the verse, and the reader taps a tafsir card inside the post.
3. For a reference in the middle of a sentence, use a link with `data-quranpedia-link`. Tapping it opens a modal with the verse and its tafsir, and it falls back to a normal link if JavaScript fails.

The file also covers:
- matching your blog's colours
- an optional 10-line `[ayah 2:255]` shortcode
- a checklist

**Caveats, all listed in the file:**
- It depends on a third-party site (quranpedia.net). If it is down, the frames don't load.
- Pasting a QuranPedia URL will not auto-embed in WordPress, so use the snippets instead.
- Some parameters (`data-lock`, `data-options`) work but aren't in QuranPedia's docs, so preview each embed after you publish.
- Ranges are cut to 20 ayahs.