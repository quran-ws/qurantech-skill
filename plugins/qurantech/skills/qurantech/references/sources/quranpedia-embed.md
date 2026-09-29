# QuranPedia Embed Service & oEmbed

> **Where this fits.** QuranPedia is a hosted API and embed service that complements the Quran.ws building blocks ([../blocks.md](../blocks.md)): it adds the tafsir/translation library, i'rab, fatwas, the embed widget and delta sync (this file covers the embed widget). Use `quran-text`, `quran-svg`, `quran-tajweed` and `qiraat-ayah-map` for text, pages, tajweed spans and ayah mapping.
> Join QuranPedia data to block data through ayah keys (`number_in_hafs`); when the app's riwayah is not Hafs, convert the key with `qiraat-ayah-map` first.

## Table of Contents
- [Overview](#overview)
- [When to Use Embed vs API](#when-to-use-embed-vs-api)
- [The Embed URL](#the-embed-url)
- [embed.js: Block Mode & Link Mode](#embedjs-block-mode--link-mode)
- [oEmbed Provider](#oembed-provider)
- [Theming](#theming)
- [Use Cases](#use-cases)
- [Design Lessons](#design-lessons)

## Overview

QuranPedia provides an **embeddable ayah widget**: a stateless iframe page (cookie-free for valid requests; see [Design Lessons](#design-lessons)) at `https://quranpedia.net/embed` that renders an ayah (or range) with any of its scholarly content sections — tafsir, i'rab, qira'at, translations, similar verses, fatwas, and more — themable to match the host site. Three integration layers:

1. **Raw iframe** — point an `<iframe>` at `/embed?...`
2. **`embed.js`** — a script that turns annotated HTML into auto-resizing iframes or click-to-open modals
3. **oEmbed** — a working `/oembed` endpoint; WordPress, Discourse and similar platforms need it on their provider allowlist, because no discovery tags were found (see [oEmbed Provider](#oembed-provider))

Interactive builder: `quranpedia.net/embed-builder` · Docs: `quranpedia.net/embed-docs`

## When to Use Embed vs API

| Situation | Use |
|-----------|-----|
| A website/blog/CMS wants Quran content with **zero backend work** | Embed |
| You need styled, scholarly-complete content (tafsir + i'rab + qiraat) without building those UIs | Embed |
| You're building a native app or need raw data | [API](quranpedia-api.md) |
| Users paste ayah links into a forum/CMS | oEmbed, once the platform allowlists the provider |

The embed renders the **same content as the API and the site's own ayah modal** — all three are built from one shared data layer, so they never disagree.

## The Embed URL

```
https://quranpedia.net/embed?surah=2&ayah=255&type=tafsir&theme=dark
```

### Target selection

| Param | Values | Notes |
|-------|--------|-------|
| `surah` | 1–114 | Required (unless `ayah_ids` given); `surah` alone returns 404, `ayah` is also required |
| `ayah` | `255` or `1-5` | Single or range; ranges are silently clamped to **20 ayahs** (`1-21` renders `1-20`); inverted bounds auto-swap |
| `ayah_ids` | `123,456,789` | Explicit ayah IDs — may be **non-contiguous and cross-surah** (e.g., a topic's verse selection); up to 20 (21 ids return 404). Observed behaviour, not in the docs |
| `mushaf` | integer, default 1 (Hafs) | Render text from another riwayah's mushaf. Observed behaviour, not in the docs; an unknown id gives the 404 page |

### Content section (`type`)

12 documented types: `tafsir`, `e3rab`, `asbab`, `nasekh`, `meanings`, `notes`, `topics`, `fatwa`, `qiraat`, `translations`, `similar`, `attachments`. Five more are accepted but undocumented (observed 2026-09-29, may change): `library`, `sayings`, `tajweed`, `surah_info`, `surah_resources`.

Omit `type` to show the ayah with a card grid of available sections (filter cards with `options=tafsir,e3rab`). Any valid `type` deep-links straight into that section. An unknown `type` (e.g. `bogus`) is not an error: it returns 200 with the section grid.

### Type-specific params

| Param | Used with | Purpose |
|-------|-----------|---------|
| `book` / `tafsir_id` | `tafsir`, `library` | Preselect a specific book |
| `books` | `library` | Comma list of book IDs |
| `image=1` | book content | Show **scanned print-book pages** instead of/alongside text |
| `tab` | `e3rab`: `books`/`morphology`/`tree` · `qiraat`: `word`/`compare`/`learn`/`count` (observed, undocumented) · `similar`: `similar`/`beginning`/`ending`/`identical`/`phrases`/`scholarly` | Sub-view within a section |
| `rawi`, `rawi1`, `rawi2` | `qiraat` | Select rawi; `rawi1`+`rawi2` = side-by-side comparison. Observed behaviour, not in the docs |
| `lang`, `category`, `fatwa` | `translations`, `fatwa` | Filter/preselect |

### Behavior params

| Param | Effect |
|-------|--------|
| `lock=1` | Lock to the selected section (no navigation away) |
| `ayah_text=0` | Hide the ayah text (section content only) |
| `fonts=0` | Skip Quranic webfont loading (lighter; host provides fonts). Observed behaviour, not in the docs |
| `locale=en` | English UI chrome (content stays Arabic where applicable). Observed behaviour, not in the docs; it leaks the raw key `ayah.singular` into the page `<title>` (site bug, 2026-09-29) |
| `fragment=1` | Return a bare HTML fragment instead of a full page (for custom integrations; served with 5-min public cache + stale-while-revalidate). Observed behaviour, not in the docs |

A bad `surah`, `ayah=999`, `theme` or `mushaf` renders a friendly themed not-found page (404) — never a blank page or redirect, so a misconfigured embed degrades gracefully on the host site. Exceptions: an unknown `type` returns 200 (see above).

## embed.js: Block Mode & Link Mode

```html
<script src="https://quranpedia.net/embed.js" defer></script>
```

**Block mode** — a div becomes an auto-sized iframe:

```html
<div data-quranpedia-embed data-surah="2" data-ayah="255"
     data-type="tafsir" data-theme="dark"></div>
```

**Link mode** — a normal link opens the widget in an in-page modal (with the href as no-JS fallback):

```html
<a href="https://quranpedia.net/embed?surah=2&ayah=255"
   data-quranpedia-link data-surah="2" data-ayah="255">آية الكرسي</a>
```

Every `data-*` attribute maps mechanically to a query param (`data-ayah-text="0"` → `ayah_text=0`, `data-rawi1="2"` → `rawi1=2`), so **new URL params work through embed.js without script changes**. `data-height` sets the initial iframe height (default 420); iframes auto-resize via postMessage.

## oEmbed Provider

```
GET https://quranpedia.net/oembed?url={ayah-or-embed-url}&format=json&maxwidth=600&maxheight=500
```

Returns `{version: "1.0", type: "rich", provider_name, provider_url, title, html, width, height}` with a ready iframe in `html`; there are no `author_*`, `cache_age` or thumbnail fields. JSON only: `format=xml` returns 501, and an unsupported URL returns 404 `{"error": "Unsupported or invalid url"}`.

The endpoint works, but no oEmbed discovery `<link>` tags were found on `/`, `/embed`, `/embed-docs` or `/tafsir/...`, and there is no `Link` header. So auto-embed on paste is unsourced: WordPress and Discourse need QuranPedia on their provider allowlist (or a discovery mechanism) before pasted links embed.

## Theming

| Param | Values | Effect |
|-------|--------|--------|
| `theme` | `light` (default) / `dark` / `sepia` | Base palette |
| `primary` | 6-digit hex (no `#`) | Accent color — a full derived shade palette is computed server-side |
| `bg` | 6-digit hex or `transparent` | Background (transparent blends into the host page) |
| `size` | 80–130 | Text scale (%) |
| `radius` | `none` / `sm` / `default` | Corner rounding |

Match the host site with e.g. `?theme=dark&primary=0ea5e9&bg=transparent&radius=none`.

## Use Cases

- **Blog/article citing an ayah** — link mode: the ayah reference in the text opens a modal with full text + tafsir; readers never leave the page.
- **Islamic forum or community (Discourse/WordPress)** — add the `/oembed` endpoint to the platform's provider allowlist, then pasted QuranPedia links can embed.
- **Educational sites** — embed a qira'at word comparison (`type=qiraat&tab=compare&rawi1=2&rawi2=10`) or an i'rab dependency tree (`type=e3rab&tab=tree`) inside lesson pages.
- **Fatwa/Q&A portals** — embed the cited ayah with `type=fatwa` or `lock=1` on the relevant tafsir.
- **Newsletters / LMS / documentation** — block mode with fixed `type`, themed to the brand.
- **Apps that render their own ayah text** but want scholarly content on tap — `ayah_text=0&fragment=1` fragments inside a WebView or custom modal.

## Design Lessons

If you're building your own embed service for Quranic content, copy these decisions:

- **Stateless and cookie-free for valid `/embed` requests** — no sessions, no consent banners on host sites. The 404 pages and `/oembed` 404s do set `XSRF-TOKEN` and `quranpedia_session` cookies, so it is not cookie-free on errors; framable anywhere (`frame-ancestors *`), CORS enabled on `/embed` and `/oembed` (v1 JSON endpoints currently allow any origin too, undocumented).
- **One data layer, three surfaces** — the site modal, the embed, and the API render from the same service classes, so content parity is by construction, not by testing.
- **Every data-attribute forwards to a query param** — the loader script never needs updating when the embed gains features.
- **Errors are themed, friendly pages** — an embed that breaks on someone else's site must still look intentional.
- **Adab still applies** ([adab.md](../concepts/adab.md)): the widget shows complete ayahs, proper Quranic fonts (with `fonts=0` opt-out only for hosts that provide them), and labeled translations.
