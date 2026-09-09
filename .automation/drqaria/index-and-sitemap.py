#!/usr/bin/env python3
"""Rebuild the Writing index pages and the drqaria sitemap from what exists.

    python3 .automation/drqaria/index-and-sitemap.py

Reads every draft in drafts/ whose built pages exist, newest first, and writes
drqaria/writing.html and drqaria/writing-ar.html plus drqaria/sitemap.xml. The
drafts are the source of truth for card text, so a card can never drift from
the page it points at. Idempotent: running it twice changes nothing.
"""
import json, os, re, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SITE = os.path.join(ROOT, "drqaria")
HOST = "https://drqaria.njmcmedicsupp.com"

HEAD = """<!DOCTYPE html>
<html lang="{lang}"{rtl}>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <link rel="canonical" href="{canonical}" />
  <meta name="robots" content="index, follow" />
  <meta name="author" content="{author}" />
  <link rel="alternate" hreflang="en" href="{HOST}/writing.html" />
  <link rel="alternate" hreflang="ar" href="{HOST}/writing-ar.html" />
  <link rel="alternate" hreflang="x-default" href="{HOST}/writing.html" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <script type="application/ld+json">
{blog_ld}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="{fonts}" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/writing.css?v=1" />
  <link rel="icon" href="/favicon.ico" />
</head>
<body{bodyrtl}>

<nav>
  <div class="nav-inner">
    <a class="nav-brand" href="{home}">{brand}</a>
    <ul class="nav-links">
      <li><a href="{home}#about">{n_about}</a></li>
      <li><a href="{home}#business">{n_business}</a></li>
      <li><a href="{home}#research">{n_research}</a></li>
      <li><a href="{self_url}">{n_writing}</a></li>
      <li><a href="{other_url}" class="lang-toggle">{n_lang}</a></li>
      <li><a href="{home}#contact" class="nav-cta">{n_contact}</a></li>
    </ul>
  </div>
</nav>

<header class="page-head">
  <div class="page-head-inner">
    <div class="breadcrumb"><a href="{home}">{n_home}</a></div>
    <h1>{h1}</h1>
    <p class="standfirst">{standfirst}</p>
  </div>
</header>

<section class="post-list">
{cards}
</section>

<footer>
  <div class="footer-links">
    <a href="{self_url}">{n_writing}</a>
    <a href="https://njmcmedicsupp.com" target="_blank" rel="noopener">NJMC Medical</a>
    <a href="https://pharmatrust.tech" target="_blank" rel="noopener">PharmaTrust.tech</a>
    <a href="https://blog.landcarenj.com" target="_blank" rel="noopener">LNJC</a>
    <a href="https://scholar.google.com/citations?user=iSkqQgUAAAAJ&amp;hl=en" target="_blank" rel="noopener">Google Scholar</a>
    <a href="https://www.linkedin.com/in/drqaria" target="_blank" rel="noopener">LinkedIn</a>
    <a href="{other_url}">{n_lang}</a>
  </div>
  <p>{copyright}</p>
</footer>

</body>
</html>
"""

TEXT = {
    "en": dict(
        lang="en", rtl="", bodyrtl="", home="/", brand='Dr. <span>Qaria</span>',
        n_about="About", n_business="Business", n_research="Research",
        n_writing="Writing", n_lang="العربية", n_contact="Contact", n_home="Home",
        self_url="/writing.html", other_url="/writing-ar.html",
        author="Dr. Majjid A. Qaria",
        title="Writing | Dr. Majjid A. Qaria, PhD",
        description="Essays on pharmaceutical quality, sourcing and the science behind them, by a dual-PhD biomedical scientist who buys medicine for a living.",
        h1="Writing",
        standfirst="Notes from the space between the laboratory and the loading bay: what the science says, what the paperwork says, and what happens when they disagree.",
        canonical=HOST + "/writing.html",
        fonts="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap",
        copyright="© 2026 Dr. Majjid A. Qaria, PhD &nbsp;·&nbsp; Nanjing, China",
        empty="The first piece is on its way.",
    ),
    "ar": dict(
        lang="ar", rtl=' dir="rtl"', bodyrtl=' dir="rtl"', home="/index-ar.html",
        brand='د. <span>قارية</span>',
        n_about="نبذة عني", n_business="الأعمال", n_research="الأبحاث",
        n_writing="مقالات", n_lang="English", n_contact="تواصل معي", n_home="الرئيسية",
        self_url="/writing-ar.html", other_url="/writing.html",
        author="د. ماجد قارية",
        title="مقالات | د. ماجد أحمد قارية",
        description="مقالات في جودة الدواء والتوريد والعلم الذي يقف خلفهما، بقلم عالم أحياء طبية يحمل دكتوراتين ويشتري الدواء مهنةً.",
        h1="مقالات",
        standfirst="ملاحظات من المساحة الواقعة بين المختبر ورصيف الشحن: ما يقوله العلم، وما تقوله الأوراق، وما يحدث حين يختلفان.",
        canonical=HOST + "/writing-ar.html",
        fonts="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&family=Amiri:wght@400;700&display=swap",
        copyright="© 2026 د. ماجد أحمد قارية &nbsp;·&nbsp; نانجينغ، الصين",
        empty="المقالة الأولى في الطريق.",
    ),
}


def load_posts():
    posts = []
    for path in glob.glob(os.path.join(HERE, "drafts", "*.json")):
        draft = json.load(open(path, encoding="utf-8"))
        if not os.path.exists(os.path.join(SITE, draft["slug"] + ".html")):
            continue
        posts.append(draft)
    posts.sort(key=lambda d: d["date"], reverse=True)
    return posts


def card(draft, lang):
    d = draft[lang]
    href = draft["slug"] + (".html" if lang == "en" else "-ar.html")
    return (f'  <a class="post-card" href="/{href}">\n'
            f'    <div class="badge">{draft["badge_" + lang]}</div>\n'
            f'    <h2>{d["h1"]}</h2>\n'
            f'    <p>{d["standfirst"]}</p>\n'
            f'    <div class="post-date">{d["published"]}</div>\n'
            f'  </a>')


def blog_ld(posts, lang):
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Blog",
        "@id": HOST + "/writing.html#blog",
        "name": TEXT[lang]["title"],
        "description": TEXT[lang]["description"],
        "inLanguage": lang,
        "url": TEXT[lang]["canonical"],
        "author": {"@type": "Person", "@id": HOST + "/#person",
                   "name": TEXT[lang]["author"]},
        "blogPost": [
            {"@type": "BlogPosting",
             "headline": p[lang]["h1"],
             "datePublished": p["date"],
             "url": HOST + "/" + p["slug"] + (".html" if lang == "en" else "-ar.html")}
            for p in posts
        ],
    }, ensure_ascii=False, indent=2)


def write_index(posts, lang):
    t = dict(TEXT[lang])
    cards = "\n".join(card(p, lang) for p in posts) or \
        f'  <p class="empty-note">{t["empty"]}</p>'
    html = HEAD.format(HOST=HOST, cards=cards, blog_ld=blog_ld(posts, lang), **t)
    out = os.path.join(SITE, "writing.html" if lang == "en" else "writing-ar.html")
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", os.path.relpath(out, ROOT))


def write_sitemap(posts):
    today = datetime.date.today().isoformat()
    urls = [(HOST + "/", today, "1.0"),
            (HOST + "/index-ar.html", today, "0.9"),
            (HOST + "/writing.html", today, "0.9"),
            (HOST + "/writing-ar.html", today, "0.8")]
    for p in posts:
        urls.append((HOST + "/" + p["slug"] + ".html", p["date"], "0.8"))
        urls.append((HOST + "/" + p["slug"] + "-ar.html", p["date"], "0.7"))
    body = "\n".join(
        f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{mod}</lastmod>\n"
        f"    <priority>{pri}</priority>\n  </url>" for loc, mod, pri in urls)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f"{body}\n</urlset>\n")
    out = os.path.join(SITE, "sitemap.xml")
    open(out, "w", encoding="utf-8").write(xml)
    print("wrote", os.path.relpath(out, ROOT), f"({len(urls)} urls)")


def main():
    posts = load_posts()
    for lang in ("en", "ar"):
        write_index(posts, lang)
    write_sitemap(posts)
    print(f"{len(posts)} post(s) listed")


if __name__ == "__main__":
    main()
