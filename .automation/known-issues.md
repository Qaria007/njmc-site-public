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

## Search and answer-engine backfill (recorded 4 September 2026)

- The six older Insights articles predate the answer-engine format: their
  answer box label is "In short", not a question H2, and their answer is not
  the first FAQ item. `gates.py` reports this as a note, not a failure. Backfill
  is a weekly-cycle task: give each a question H2 and a 40 to 60 word answer,
  which most already nearly have (40 to 59 words, DMF is 71).
- The site describes NJMC four different ways in one sentence (`about.html`,
  `index.html`, `contact.html` meta descriptions, and the Organization schema).
  The pipeline now deploys ONE canonical sentence in every article. Aligning the
  four older descriptions to it is a small owner-visible edit, not done here.


## drqaria/ (recorded 4 September 2026)

`drqaria/` is Dr. Qaria's profile site, served at `drqaria.njmcmedicsupp.com`
and kept in this repository only so the deploy does not delete it. `gates.py`
skips it: its canonical is its own subdomain (correct, not a defect), and the
NJMC content rules are not its rules. For the record, both its pages carry en
dashes (11 EN, 10 AR); that is that site's own backlog, not this pipeline's.
\n