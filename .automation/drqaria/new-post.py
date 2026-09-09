#!/usr/bin/env python3
"""Build one Writing post pair (English + Arabic) for drqaria.njmcmedicsupp.com.

    python3 .automation/drqaria/new-post.py .automation/drqaria/drafts/<slug>.json

The page chrome lives in template-en.html and template-ar.html beside this
script, so the writer supplies reviewed prose only and can never invent a CSS
class the site does not have. Rerunning with the same draft overwrites the same
two files, so a retried run cannot double-publish.

Draft JSON shape, every field required unless marked optional:

{
  "slug": "writing-my-topic",          // must start with "writing-"
  "date": "2026-09-09",                // ISO, the publication date
  "badge_en": "Research and practice",
  "badge_ar": "بحث وممارسة",
  "en": {
    "title":       "...",   // page <title>, aim under 62 characters
    "description": "...",   // meta description, 140 to 165 characters
    "h1":          "...",
    "standfirst":  "...",   // one or two sentences under the H1
    "question":    "...?",  // the question a reader asks, rendered as the answer-box H2
    "answer":      "...",   // 40 to 60 words, true standing alone, quotable
    "published":   "Published 9 September 2026",
    "body":        "<p>...</p>\\n<h2>...</h2>...",   // prose, no answer box
    "faq":         [["question", "answer"], ...],    // 3 to 5 pairs
    "faq_heading": "Frequently asked questions"
  },
  "ar": { same keys, Arabic values }
}

The answer box is built for you from "question" and "answer" and inserted after
the first paragraph of the body, and the same pair becomes FAQ item zero, so an
assistant quoting the page quotes a sentence that was written to be quoted.

Run gates.py on the two output files before committing anything.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SITE = os.path.join(ROOT, "drqaria")
BASE = "https://drqaria.njmcmedicsupp.com"

PERSON = {
    "en": {"name": "Dr. Majjid A. Qaria", "url": BASE + "/"},
    "ar": {"name": "د. ماجد أحمد قارية", "url": BASE + "/index-ar.html"},
}
WORDS_PER_MINUTE = 200


def die(msg):
    sys.exit("new-post: " + msg)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def esc(s):
    """Escape for an HTML attribute. Order matters: ampersand first."""
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def words(html):
    return len(re.sub(r"<[^>]+>", " ", html).split())


def read_time(html, lang):
    minutes = max(1, round(words(html) / WORDS_PER_MINUTE))
    if lang == "ar":
        return f"{minutes} دقيقة قراءة" if minutes == 1 else f"{minutes} دقائق قراءة"
    return f"{minutes} min read" if minutes == 1 else f"{minutes} min read"


def answer_box(question, answer):
    return (f'<div class="answer-box">\n  <h2>{question}</h2>\n'
            f'  <p>{answer}</p>\n</div>')


def insert_answer_box(body, question, answer):
    """Place the answer box after the opening paragraph, so a reader gets context
    first and an extraction tool still finds the answer high on the page."""
    box = answer_box(question, answer)
    m = re.search(r"</p>", body)
    if not m:
        return box + "\n" + body
    cut = m.end()
    return body[:cut] + "\n\n" + box + "\n" + body[cut:]


def faq_html(items):
    out = []
    for q, a in items:
        out.append('  <div class="faq-item">\n'
                   f'    <p class="faq-q">{q}</p>\n'
                   f'    <p class="faq-a">{a}</p>\n'
                   '  </div>')
    return "\n".join(out)


def faq_ld(items, lang):
    """json.dumps owns every escape, so this schema cannot be malformed."""
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": lang,
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items
        ],
    }, ensure_ascii=False, indent=2)


def article_ld(draft, lang, url, alt_url):
    d = draft[lang]
    person = PERSON[lang]
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "@id": url + "#article",
        "headline": d["h1"],
        "description": d["description"],
        "inLanguage": lang,
        "datePublished": draft["date"],
        "dateModified": draft["date"],
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "url": url,
        "author": {
            "@type": "Person",
            "@id": BASE + "/#person",
            "name": person["name"],
            "url": person["url"],
            "jobTitle": "Chief Executive Officer, NJMC Medical Supplies Co., Ltd",
        },
        "publisher": {
            "@type": "Person",
            "@id": BASE + "/#person",
            "name": person["name"],
            "url": person["url"],
        },
        "isPartOf": {"@type": "Blog", "@id": BASE + "/writing.html#blog"},
        "workTranslation" if lang == "en" else "translationOfWork": {
            "@type": "BlogPosting", "url": alt_url, "inLanguage": "ar" if lang == "en" else "en",
        },
    }, ensure_ascii=False, indent=2)


def build(draft, lang):
    d = draft[lang]
    slug = draft["slug"]
    url = f"{BASE}/{slug}.html" if lang == "en" else f"{BASE}/{slug}-ar.html"
    alt = f"{BASE}/{slug}-ar.html" if lang == "en" else f"{BASE}/{slug}.html"

    body = insert_answer_box(d["body"].strip(), d["question"], d["answer"])
    faq_items = [[d["question"], d["answer"]]] + [list(p) for p in d["faq"]]

    tpl = read(os.path.join(HERE, f"template-{lang}.html"))
    filled = {
        "TITLE": esc(d["title"]),
        "DESCRIPTION": esc(d["description"]),
        "SLUG": slug,
        "BADGE": draft[f"badge_{lang}"],
        "H1": d["h1"],
        "STANDFIRST": d["standfirst"],
        "PUBLISHED": d["published"],
        "READTIME": read_time(body, lang),
        "BODY": body,
        "FAQ_HEADING": d["faq_heading"],
        "FAQ_ITEMS": faq_html(faq_items),
        "ARTICLE_LD": article_ld(draft, lang, url, alt),
        "FAQ_LD": faq_ld(faq_items, lang),
    }
    for key, value in filled.items():
        tpl = tpl.replace("{{" + key + "}}", value)

    left = re.findall(r"\{\{[A-Z_]+\}\}", tpl)
    if left:
        die(f"template placeholder never filled: {sorted(set(left))}")
    return tpl, (f"{slug}.html" if lang == "en" else f"{slug}-ar.html")


def validate(draft):
    if not draft["slug"].startswith("writing-"):
        die("slug must start with 'writing-'")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", draft["date"]):
        die("date must be ISO, YYYY-MM-DD")
    for lang in ("en", "ar"):
        d = draft[lang]
        for key in ("title", "description", "h1", "standfirst", "question",
                    "answer", "published", "body", "faq", "faq_heading"):
            if key not in d or not d[key]:
                die(f"{lang}.{key} is missing or empty")
        n = len(d["answer"].split())
        if not 30 <= n <= 75:
            die(f"{lang}.answer is {n} words; it must stand alone in 40 to 60")
        if not d["question"].rstrip().endswith(("?", "؟")):
            die(f"{lang}.question must be phrased as a question")
        if not 3 <= len(d["faq"]) <= 5:
            die(f"{lang}.faq needs 3 to 5 pairs, found {len(d['faq'])}")
        if "answer-box" in d["body"]:
            die(f"{lang}.body must not contain its own answer box; it is built for you")


def main():
    if len(sys.argv) != 2:
        die("usage: new-post.py <draft.json>")
    draft = json.loads(read(sys.argv[1]))
    validate(draft)
    os.makedirs(SITE, exist_ok=True)
    for lang in ("en", "ar"):
        html, name = build(draft, lang)
        path = os.path.join(SITE, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"wrote drqaria/{name}  ({words(html)} words of markup)")


if __name__ == "__main__":
    main()
