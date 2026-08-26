#!/usr/bin/env python3
"""Wire a published article into insights.html, ar/insights.html and sitemap.xml.

    python3 .automation/index-and-sitemap.py .automation/drafts/<draft>.json

Idempotent: running it twice does nothing the second time, so a retried
publish cannot produce duplicate cards or duplicate sitemap entries.

The draft JSON needs, in addition to what new-article.py uses:

  "card": { "en": "one line blurb", "ar": "..." }
  "card_title": { "en": "...", "ar": "..." }   // optional, defaults to h1
"""
import json, os, re, sys, xml.dom.minidom

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BASE = "https://njmcmedicsupp.com"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def add_card(index_file, href, title, blurb):
    path = os.path.join(ROOT, index_file)
    h = open(path, encoding="utf-8").read()
    if f'href="{href}"' in h:
        print(f"{index_file}: already listed, skipped")
        return
    items = list(re.finditer(r'<div class="insight-item">.*?</div></div>', h, re.S))
    if not items:
        sys.exit(f"{index_file}: could not find the insight-item list")
    card = (f'<div class="insight-item"><h3><a href="{href}">{esc(title)}</a></h3>'
            f"<p>{esc(blurb)}</p></div>")
    end = items[-1].end()
    open(path, "w", encoding="utf-8").write(h[:end] + card + h[end:])
    print(f"{index_file}: card added")


def add_sitemap(slug, date):
    path = os.path.join(ROOT, "sitemap.xml")
    s = open(path, encoding="utf-8").read()
    if f"/{slug}.html<" in s:
        print("sitemap.xml: already listed, skipped")
        return

    def entry(loc):
        return (f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{date}</lastmod>\n"
                f'    <xhtml:link rel="alternate" hreflang="en" href="{BASE}/{slug}.html"/>\n'
                f'    <xhtml:link rel="alternate" hreflang="ar" href="{BASE}/ar/{slug}.html"/>\n'
                f'    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE}/{slug}.html"/>\n'
                "  </url>\n")

    s = s.replace("</urlset>", entry(f"{BASE}/{slug}.html") + entry(f"{BASE}/ar/{slug}.html")
                  + "</urlset>")
    open(path, "w", encoding="utf-8").write(s)
    xml.dom.minidom.parse(path)  # refuse to leave a sitemap that does not parse
    print("sitemap.xml: two urls added and the file still parses")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    slug = spec["slug"]
    titles = spec.get("card_title", {})
    add_card("insights.html", f"/{slug}.html",
             titles.get("en", spec["en"]["h1"]), spec["card"]["en"])
    add_card("ar/insights.html", f"/ar/{slug}.html",
             titles.get("ar", spec["ar"]["h1"]), spec["card"]["ar"])
    add_sitemap(slug, spec["date"])


if __name__ == "__main__":
    main()
