<div align="center">

<img src=".github/banner.svg" alt="QuranTech — Guidance, Experimental" width="820">

**Quran application knowledge and development guidance prepared for AI coding agents.**

<a href="https://quran.ws/blocks/qurantech"><img alt="See it work" src="https://img.shields.io/badge/See_it_work-15705D?style=for-the-badge&labelColor=102F29"></a>
<a href="https://quran.ws/docs/reference/qurantech"><img alt="Documentation" src="https://img.shields.io/badge/Documentation-102F29?style=for-the-badge&labelColor=102F29"></a>

</div>

Use it when working with an AI coding agent and you want it to understand riwayat, ayah counting, Quran data structures, project components, and conventions for Quran applications.

> معرفة وإرشادات مهيّأة لوكلاء البرمجة بالذكاء الاصطناعي لبناء تطبيقات القرآن والتعامل مع بياناتها ومصطلحاتها.
>
> استخدمها عندما تعمل مع وكيل برمجي أو أداة AI وتريد أن يفهم القراءات، وعدّ الآي، وبنية البيانات، ومكوّنات المشروع، والقواعد الخاصة بالتطبيقات القرآنية.

| | |
|---|---|
| **References** | 19 focused files |
| **Format** | Agent Skill |
| **Licence** | CC BY 4.0 (the content) · MIT (the tooling) |

```text
/plugin marketplace add https://github.com/quran-ws/qurantech-skill
```

## Where the documentation is

Everything about using it lives on the site. This repository is the source.

| | |
|---|---|
| **Overview and demo** | [quran.ws/blocks/qurantech](https://quran.ws/blocks/qurantech) |
| **Reference** | [quran.ws/docs/reference/qurantech](https://quran.ws/docs/reference/qurantech) |
| **Licensing in full** | [quran.ws/docs/reference/licensing](https://quran.ws/docs/reference/licensing) |

## What is in here

| | |
|---|---|
| `plugins/qurantech/` | the skill itself: the references, loaded only when the task needs them |
| `dist/` | the packaged `qurantech.skill` |
| `evals/` | the benchmark prompts and their assertions |
| `LICENSES/` | per-file licence texts |

Issues and pull requests are welcome here. Everything that is not about *changing* this repository is on the site.
