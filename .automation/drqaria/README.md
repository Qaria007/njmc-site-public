# Writing automation for drqaria.njmcmedicsupp.com

`drqaria/` is a **separate site** that happens to live inside this repository,
because Hostinger's git deploy copies the whole repository into `public_html`
and the subdomain is served from `public_html/drqaria`. It has its own host, its
own design and its own voice, so it has its own tooling here rather than sharing
the NJMC Insights pipeline.

## The pipeline

```
topic from topics.md
        |
        v
drafts/<slug>.json                       the writer produces this, prose only
        |
        v
python3 .automation/drqaria/new-post.py <draft>          builds EN + AR pages
python3 .automation/drqaria/gates.py    <the two pages>  refuses on a rule break
python3 .automation/drqaria/index-and-sitemap.py         index pages + sitemap
        |
        v
git commit + push  ->  the site updates
```

Every step is idempotent. Rerunning a draft overwrites the same two files, and
the index is rebuilt from the drafts each time, so a retried run cannot
double-publish or leave a card pointing at nothing.

## Why a scaffolder rather than writing HTML

The homepage keeps its styles in one inline block. Article pages instead link
`drqaria/assets/writing.css`, and their chrome lives in `template-en.html` and
`template-ar.html` here. A writer who hand-wrote HTML would eventually invent a
class the stylesheet does not define, and the page would render unstyled while
looking perfectly fine in the source. That exact failure has already happened
once on the NJMC side, which is why that pipeline works the same way.

## Why these gates are not the NJMC gates

The root `.automation/gates.py` deliberately returns early on anything under
`drqaria/`. The two sites make different claims, so they need different rules.
The drqaria gates add one the NJMC gates do not have: the PharmaTrust
positioning vocabulary, checked **per sentence** and only where the sentence
names PharmaTrust, so that ordinary uses of "verified" elsewhere in a piece are
not flagged. That guardrail exists because this site had already published
"compliance technology" and "an automated pass/fail verification engine",
wording the product's own rules forbid, and nobody noticed for weeks.

## Proving the gates

A gate that has never failed is not known to work. `prove-gates.py` breaks each
rule once on a throwaway copy and checks the gate fires:

```
python3 .automation/drqaria/prove-gates.py
```

It found a real defect on its first run: the threshold-figure pattern ended in
`\b` after `%`, and since `%` and `.` are both non-word characters there is no
boundary between them, so "not more than 0.5 %." at the end of a sentence passed
silently. The same bug was present in the NJMC gates and was fixed there too.

## Files

| File | What it is |
|------|-----------|
| `template-en.html`, `template-ar.html` | page chrome with `{{PLACEHOLDER}}` slots |
| `new-post.py` | draft JSON to two finished pages |
| `gates.py` | the publish gates for this site |
| `prove-gates.py` | breaks each gate once to prove it bites |
| `index-and-sitemap.py` | rebuilds both index pages and the sitemap |
| `topics.md` | the queue, and what qualifies as a topic here |
| `routine-prompt.md` | the prompt for the scheduled writer |
| `drafts/` | one JSON per published article, the source of truth for index cards |

## Running it by hand

```
python3 .automation/drqaria/new-post.py .automation/drqaria/drafts/<slug>.json
python3 .automation/drqaria/gates.py
python3 .automation/drqaria/index-and-sitemap.py
```

Then commit and push. `git pull --rebase` first: the NJMC weekly writer pushes
to this same repository on Tuesdays.
