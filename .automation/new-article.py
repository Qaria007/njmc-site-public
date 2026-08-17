#!/usr/bin/env python3
"""Scaffold an NJMC Insights article pair (English + Arabic) on the live template.

    python3 .automation/new-article.py draft.json

The chrome (nav, footer, author box, head links, JSON-LD author and publisher)
is lifted verbatim from an existing article, so a new page cannot drift from the
site's real markup or invent CSS classes that do not exist. The caller supplies
only the reviewed prose.

Draft JSON shape, all fields required unless marked optional:

{
  "slug": "insights-api-impurity-profiles",
  "date": "2026-08-18",
  "reference": "insights-dmf-cep-api-documents.html",   // optional, template source
  "en": {
    "title": "...",            // under 62 chars
    "description": "...",      // 140 to 165 chars
    "h1": "...",
    "summary": "...",          // hero standfirst
    "badge": "Active Pharmaceutical Ingredients",
    "published": "Published 18 August 2026",
    "body": "<div class=\"answer-box\">...</div>\n<h2>...</h2>...",
    "faq": [["question", "answer"], ...],
    "faq_heading": "Frequently asked questions",
    "related": [["/drug-apis.html", "Card title", "Card blurb"], ...]
  },
  "ar": { same keys, Arabic values }
}

Run .automation/gates.py on the output before publishing anything.
"""
import json, os, re, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public_html"))
DEFAULT_REF = "insights-dmf-cep-api-documents.html"
BASE = "https://njmcmedicsupp.com"


def read(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


def block(html, pat, what):
    m = re.search(pat, html, re.S)
    if not m:
        sys.exit(f"template block not found ({what}) in the reference article")
    return m.group(0)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def faq_ld(items, lang):
    """json.dumps owns all escaping so the schema can never be malformed."""
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": lang,
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items],
    }, ensure_ascii=False, indent=2)


def faq_html(items, heading):
    """Same raw strings as the schema, HTML escaped, so the two can never diverge."""
    body = "".join(f'<details class="faq-item"><summary>{esc(q)}</summary>'
                   f"<p>{esc(a)}</p></details>" for q, a in items)
    return f'<h2 class="faq-h">{heading}</h2><div class="faq">{body}</div>'


def related_html(items, heading):
    cards = "".join(f'<a href="{href}"><span class="t">{esc(t)}</span>'
                    f'<span class="d">{esc(d)}</span></a>' for href, t, d in items)
    return f'<h2>{heading}</h2><div class="related">{cards}</div>'


PAGE = """<!DOCTYPE html>
<html lang="{lang}"{dir}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="{BASE}/{self_path}">

<link rel="alternate" hreflang="en" href="{BASE}/{slug}.html">
<link rel="alternate" hreflang="ar" href="{BASE}/ar/{slug}.html">
<link rel="alternate" hreflang="x-default" href="{BASE}/{slug}.html">

<meta property="og:type" content="article">
<meta property="og:site_name" content="NJMC Medical Supplies Co., Ltd">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{BASE}/{self_path}">
<meta property="og:locale" content="{locale}">
<meta name="twitter:card" content="summary_large_image">
{head_chrome}
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{h1}",
  "description": "{desc}",
  "inLanguage": "{lang}",
  "datePublished": "{date}",
  "dateModified": "{date}",
  "mainEntityOfPage": "{BASE}/{self_path}",
  {author_ld}
}}
</script>
<script type="application/ld+json">
{faq_ld}
</script>
</head>
<body>
{nav}

<section class="page-hero">
<div class="hero-inner">
<div class="breadcrumb"><a href="{home}">{home_label}</a><i>/</i><a href="{insights}">{insights_label}</a></div>
<div class="hero-badge">{badge}</div>
<div class="article-meta">{published}</div>
<h1>{h1}</h1>
<p class="hero-summary">{summary}</p>
</div>
</section>

<section>
<div class="section-inner">
<div class="prose">
{body}
{faq}
</div>
{author}
</div>
</section>

<section class="alt-bg">
<div class="section-inner">
{related}
{cta}</div>
</div>
</section>

{footer}
</body>
</html>
"""

LOCALE = {"en": "en_US", "ar": "ar_AR"}
LABELS = {
    "en": dict(home="/", home_label="Home", insights="/insights.html", insights_label="Insights"),
    "ar": dict(home="/index-ar.html", home_label="الرئيسية", insights="/ar/insights.html",
               insights_label="مقالات"),
}


def build(spec, lang):
    slug = spec["slug"]
    s = spec[lang]
    ref_name = spec.get("reference", DEFAULT_REF)
    ref = read(ref_name if lang == "en" else "ar/" + ref_name)
    self_path = f"{slug}.html" if lang == "en" else f"ar/{slug}.html"
    twin = f"/ar/{slug}.html" if lang == "en" else f"/{slug}.html"

    nav = block(ref, r"<nav>.*?</nav>", "nav")
    nav = re.sub(r'class="nav-brand" href="[^"]*"',
                 'class="nav-brand" href="%s"' % LABELS[lang]["home"], nav)
    nav = re.sub(r'class="lang-toggle" href="[^"]*"',
                 f'class="lang-toggle" href="{twin}"', nav)

    footer = block(ref, r"<footer>.*?</footer>", "footer")
    footer = footer.replace('<a href="#hero">', f'<a href="{LABELS[lang]["home"]}">')
    # Arabic pages ship a relative English link that resolves under /ar/ and 404s.
    footer = footer.replace('<a href="index.html">English</a>', '<a href="/">English</a>')

    cta = block(ref, r'<div class="cta-band">.*?</div>\n</div>\n</section>', "cta band")
    cta = cta[:cta.index("</div>\n</section>")]

    return PAGE.format(
        lang=lang, dir=' dir="rtl"' if lang == "ar" else "", BASE=BASE, slug=slug,
        self_path=self_path, locale=LOCALE[lang], date=spec["date"],
        title=esc(s["title"]), desc=esc(s["description"]), h1=esc(s["h1"]),
        summary=esc(s["summary"]), badge=esc(s["badge"]), published=esc(s["published"]),
        head_chrome=block(ref, r'<link rel="icon" href="/favicon\.ico".*?njmc-pages\.css\?v=7">',
                          "head links"),
        author_ld=block(ref, r'"author": \{.*?\n  \},\n  "publisher": \{.*?\n  \}', "author schema"),
        faq_ld=faq_ld(s["faq"], lang), nav=nav, body=s["body"],
        faq=faq_html(s["faq"], s["faq_heading"]),
        author=block(ref, r'<div class="author-box">.*?\n</div>\n</div>', "author box"),
        related=related_html(s["related"],
                             "Related pages" if lang == "en" else "صفحات ذات صلة"),
        cta=cta, footer=footer, **LABELS[lang])


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    for lang in ("en", "ar"):
        out = os.path.join(ROOT, f"{spec['slug']}.html" if lang == "en"
                           else os.path.join("ar", f"{spec['slug']}.html"))
        open(out, "w", encoding="utf-8").write(build(spec, lang))
        print("wrote", os.path.relpath(out, ROOT))
    print("\nNow run: python3 .automation/gates.py "
          f"public_html/{spec['slug']}.html public_html/ar/{spec['slug']}.html")


if __name__ == "__main__":
    main()
