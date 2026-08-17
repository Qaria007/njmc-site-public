# Known pre-existing issues

These were found by `gates.py` on pages that were already live before this
repository existed. They are **not** regressions from the automation, and they
are deliberately left alone: fixing them is a separate decision for the owner,
because it means editing the homepage copy.

Recorded 18 August 2026, against the site as mirrored from the live host.

## Blocking-level (gates.py exits non-zero because of these)

| Page | Issue | Where |
|------|-------|-------|
| `index.html` | 4 en dashes | `Monday – Friday, 9:00 AM – 5:00 PM` (twice, in two blocks) |
| `index-ar.html` | 2 en dashes | `الاثنين إلى الجمعة، 9:00 صباحاً – 5:00 مساءً` |
| `index.html` | AI-writing marker | "...they need to thrive in today's competitive environment" |
| `index.html` | AI-writing marker | "...empowers medical institutions with tailored solutions and support" and a "Tailored solutions for medical institutions' needs" heading |
| `index.html` | AI-writing marker | "trusted partner" |
| `index.html` | AI-writing marker | "...purchasing decisions in a competitive healthcare landscape" |

Suggested fix for the dashes, if the owner wants it: replace ` – ` with ` to `
in the business-hours lines, English and Arabic.

## Non-blocking notes

- Six live Insights articles point their language toggle at the site home
  (`/index-ar.html`) rather than at the article's own translation. New articles
  written by this pipeline point at the twin, which is better for readers and
  consistent with the hreflang tags.
- `nav-brand href="#hero"` on every article page is a dead anchor: `id="hero"`
  exists only on `index.html`. Clicking the logo on an article does nothing.
  New articles use `href="/"` (English) and `href="/index-ar.html"` (Arabic).
- Arabic article footers carry `<a href="index.html">English</a>`, which
  resolves to `/ar/index.html` and 404s. New Arabic articles link to `/`.
- Several meta descriptions are outside the 140 to 165 character target;
  `verification.html` (209) and `index.html` (200) are the furthest out.
- `TODO-OWNER: verify` comments already appear on several live pages, so the
  convention predates this pipeline. They are invisible to readers.
