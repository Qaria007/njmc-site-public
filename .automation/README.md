# NJMC Insights automation

This repository's top level IS the njmcmedicsupp.com web root: Hostinger's git
deploy copies the entire repository as-is into the server's `public_html/`, with
no way to choose a source folder inside the repo, so site files must live at the
repository root. `.automation/` holds the tooling that writes and checks a new
Insights article; it is blocked from being served by `.htaccess` (see DEPLOY.md),
not by being outside the deployed tree.

## The pipeline

```
topic from .automation/topics.md
        |
        v
draft JSON in .automation/drafts/<slug>.json      (the writer produces this)
        |
        v
python3 .automation/new-article.py  <draft>       builds EN + AR pages
python3 .automation/gates.py        <pages>       refuses to pass on a rule break
python3 .automation/index-and-sitemap.py <draft>  cards + sitemap, idempotent
        |
        v
git commit + push  ->  the site updates
```

Every step is idempotent, so a retried run cannot double-publish.

## Why a scaffolder instead of writing HTML directly

The page chrome (nav, footer, author box, head links, author and publisher
schema) is copied verbatim from an existing live article every time. A writer
that hand-writes HTML will eventually invent a CSS class the site does not have,
and the page renders unstyled while still looking fine in the source. That has
already happened once, in the August 2026 impurity-profiles handoff, which used
`container`, `btn`, `related-pages` and `site-footer`, none of which exist in
`assets/njmc-pages.css`. The scaffolder makes that failure impossible.

## The gates

`gates.py` is the publish decision. Exit code 0 means publish, anything else
means stop. It enforces:

- no em dashes, en dashes or horizontal bars
- no AI-writing markers (moreover, leverage, seamless, landscape, not just, ...)
- no claim that NJMC manufactures anything; it sources, trades and consults
- no regulatory figure stated as fact (a number next to threshold or limit wording)
- one `<title>`, one `<h1>`, a meta description, a correct canonical
- all three hreflang links present, x-default matching the English page
- every JSON-LD block parses, and FAQ schema questions match the on-page
  `<summary>` text exactly
- an answer box near the top of every article
- every internal link resolving to a file that exists in the repository

Run it over the whole site at any time:

```bash
python3 .automation/gates.py
```

Six pre-existing failures on pages this pipeline did not write are known and
listed in `known-issues.md`. They are not regressions.

## Search, answer engines and generative engines

Every article the pipeline writes is built for all three at once, and the
gates refuse to publish one that is not:

- **AEO**: the answer box is a question-phrased H2 followed by a 40 to 60 word
  direct answer that stands on its own; the same pair is item 0 of the FAQPage
  schema, so an assistant can quote it; at least three further FAQ pairs.
- **GEO**: one canonical sentence describing NJMC, identical in every article
  and in the Article schema's publisher, so every engine sees the same entity
  described the same way. It lives as `BOILERPLATE` in `new-article.py` and
  `gates.py`; change it in both or the gate fails.
- **SEO**: title 60 characters or fewer carrying the registered target query,
  description 140 to 165, a registered query per topic in `topics.md`, at least
  two internal links out, and a backlink in from an older article
  (`backlink_from`), added by `index-and-sitemap.py`.

What the cloud writer cannot do, and must not pretend to: score topics from
live search data, check what currently ranks, or submit for indexing. Those
belong to the weekly review run from the Mac (the growth-engine skill's weekly
cycle), which reorders `topics.md` from Search Console and closes the loop.

## Content guardrails, in full

1. **Invent nothing about NJMC.** No clients, numbers, years, certifications,
   awards, team size or case studies that are not already live on the site.
2. **NJMC does not manufacture.** CE, FDA, SFDA and GMP belong to products and
   to the factories that make them, never to NJMC.
3. **No em dashes**, English or Arabic, body or metadata.
4. **No AI-writing markers.**
5. **No regulatory figures.** Not thresholds, fees, timelines or classification
   tiers. Where a figure would go, tell the reader to verify the current
   guideline for their market, and leave a `TODO-OWNER: verify` HTML comment.
6. **Both languages or neither.** Every article ships an English and an Arabic
   page, cross-linked, with reciprocal hreflang.

## Refilling the queue

`topics.md` is the backlog. The writer takes the first topic whose slug has no
matching file at the repository root, so publishing a topic retires it automatically.
When fewer than four unused topics remain, add more. This is the only recurring
human task in the pipeline.

## Pausing

Create a file named `PAUSED` in this directory. The writer checks for it first
and stops without doing anything.

## Undoing a publish

```bash
git revert HEAD && git push
```
