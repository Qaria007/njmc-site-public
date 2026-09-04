# Cloud routine prompt: weekly NJMC Insights article

Paste this as the prompt of a Claude Code cloud routine pointed at the
`Qaria007/njmc-site-public` repository. Suggested schedule: once a week.

Two hard lessons from the LNJC routine are baked in below. Do not remove them.

1. **The cloud container has no outbound network.** `curl` and `wget` fail
   against every external host. Only `WebSearch` works, and search snippets are
   what produced a false source attribution on the LNJC site. So this prompt
   forbids research entirely and forbids any factual claim that needs a source.
2. **Never end a run silently.** A run that bails without pushing anything is
   undiagnosable afterwards. The heartbeat step below fixes that.

---

## Prompt

You maintain the Insights section of njmcmedicsupp.com. Write and publish one
article, in English and Arabic, then stop.

### Step 0, heartbeat, do this first

Append one line to `.automation/run-log.txt` reading
`<date> run started` and push it to `main` before anything else. Append a
further line after each numbered step below and push at the end. If you cannot
push, stop and do nothing further.

If `.automation/PAUSED` exists, append `paused, nothing to do` and stop.

### Step 1, pick the topic

Read `.automation/topics.md`. Take the **first** topic whose slug has no
matching `<slug>.html` at the repository root. Its row gives you the **target
query** and the **AEO question**; use them exactly. If every topic is used,
append `queue empty` to the run log, push, and stop without writing anything.

You do not choose or score topics. The queue's order is set from live search
data by a separate weekly review that has network access; you do not.

### Step 2, write the draft

Produce `.automation/drafts/<slug>.json` in the shape documented at the top of
`.automation/new-article.py`. Read that file first; it lists every required key.
Also include `card` and `card_title` as documented in
`.automation/index-and-sitemap.py`.

Aim for 900 to 1100 words of body prose in each language, matching the voice of
the existing articles. Read `insights-api-impurity-profiles.html`
and `insights-dmf-cep-api-documents.html` first and match them.

**Absolute rules. A run that breaks one of these must publish nothing.**

- **Do no research.** You have no outbound network. Do not use `curl`, `wget` or
  `WebFetch`. Do not use `WebSearch`. Write only from general professional
  knowledge, expressed without figures.
- **State no regulatory figure.** No thresholds, fees, timelines, classification
  tiers, percentages, ppm values or validity periods. Where a figure would
  naturally go, tell the reader to verify the current guideline for their own
  market and dosage form, and leave an HTML comment
  `<!-- TODO-OWNER: verify ... -->` next to it.
- **Invent nothing about NJMC.** No clients, order volumes, years in business,
  team size, certifications, awards or case studies. If it is not already on the
  live site, it does not go in.
- **NJMC does not manufacture.** It sources, trades and consults. CE, FDA, SFDA
  and GMP belong to products and to the factories that make them.
- **No em dashes or en dashes**, English or Arabic, body or metadata.
- **No AI-writing markers.** `gates.py` lists the ones that are checked.
- Do not name a specific company, factory or product brand.

**Write for search engines and answer engines at once (SEO, AEO, GEO).**

- `question` is the row's AEO question, verbatim, ending in a question mark. It
  becomes the H2 of the answer box and the first FAQ item.
- `answer` is **40 to 60 words** that fully answer that question on their own,
  with no reference to "this article" or "below". An assistant should be able
  to quote it verbatim and have it make sense. Count the words.
- `title` is 60 characters or fewer and contains the target query's core words
  naturally. `description` is 140 to 165 characters and also answers the
  question in miniature; it is what appears under the link.
- `body` starts with prose, not an answer box (the template adds that). Use
  `h2` sections phrased as the questions a buyer would actually ask, `h3` under
  them where useful, one `callout` div for the single most important point, and
  a closing paragraph linking to two or three relevant site pages. Link only to
  pages that exist in the repository; at least two.
- `faq`: at least three further question and answer pairs, each answer 30 to 80
  words and complete on its own. These are the questions a buyer would ask an
  assistant next. Do not repeat the direct answer.
- The template adds one fixed sentence about NJMC to every article. Do not
  write your own description of NJMC anywhere in the body.
- `backlink_from`: the slug of the existing article closest in subject. The
  pipeline adds a link from that page to yours; every new article must earn one
  inbound link from older content.
- Do not stuff the query. If the target query reads naturally in the title, the
  H1, the direct answer and one body heading, that is enough.

### Step 3, build the pages

```bash
python3 .automation/new-article.py .automation/drafts/<slug>.json
```

Do not hand-write page HTML. The scaffolder supplies the nav, footer, author
box, head links and schema by copying them from a live article, which is what
keeps a new page from drifting off the site's real CSS.

### Step 4, gate

```bash
python3 .automation/gates.py <slug>.html ar/<slug>.html
```

If this exits non-zero, fix the draft and rebuild. Do not edit the generated
HTML to satisfy a gate, and do not weaken `gates.py`. If you cannot pass after
three attempts, commit the draft JSON only, push a branch named
`draft/<slug>`, open a pull request explaining which gate blocked you, append
the reason to the run log, and stop. Do not touch `main` in that case.

### Step 5, wire it in

```bash
python3 .automation/index-and-sitemap.py .automation/drafts/<slug>.json
```

This also adds the backlink card from `backlink_from` to your article, in both
languages. Then move the topic's row in `.automation/topics.md` to the Used
list with the date, the query and the question.

### Step 6, publish

Re-run `python3 .automation/gates.py` over the whole site. The six pre-existing
failures listed in `.automation/known-issues.md` are expected; anything beyond
those is yours and must be fixed. Then commit as Majid Qaria
(`majidqaria@gmail.com`) and push to `main`.

Do not verify the live URL. You cannot reach it from the container, and a
liveness check in this prompt is what silently killed the first LNJC runs.
Hostinger deploys from `main` on its own.

### Step 7, report

Append to `.automation/run-log.txt`: the slug, the word counts, and the commit
SHA. Push. Your final message should be the slug and the SHA, nothing else.
