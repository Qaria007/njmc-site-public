#!/usr/bin/env python3
"""Pre-publish gates for the drqaria.njmcmedicsupp.com Writing section.

    python3 .automation/drqaria/gates.py              # every drqaria page
    python3 .automation/drqaria/gates.py <file> ...   # named pages

Exit code 0 means publish. Anything else means do not.

These are deliberately NOT the NJMC gates. The root .automation/gates.py skips
drqaria/ because this is a separate site with a separate voice, so the rules it
needs are its own:

  1. no em dash, en dash or horizontal bar
  2. no AI-writing markers
  3. valid JSON-LD in every block
  4. every internal link resolves to a file that exists
  5. the PharmaTrust positioning vocabulary, but only in a sentence that names
     PharmaTrust, because "verified" is ordinary English elsewhere
  6. no regulatory figure stated as a threshold
  7. the English and Arabic twins point at each other, and at themselves
  8. the answer box exists, is 40 to 60 words, and matches FAQ item zero
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SITE = os.path.join(ROOT, "drqaria")
HOST = "https://drqaria.njmcmedicsupp.com"

DASHES = {"—": "em dash", "–": "en dash", "―": "horizontal bar"}

BANNED_PATTERNS = [
    (r"(?<![\w-])moreover(?![\w-])", "moreover"),
    (r"(?<![\w-])furthermore(?![\w-])", "furthermore"),
    (r"(?<![\w-])additionally(?![\w-])", "additionally"),
    (r"in today's", "in today's"),
    (r"it is important to note", "it is important to note"),
    (r"(?:\bto|\bwe|\bthey|\byou|\bit|\bcan|\bwill|\bhelps?|\ballows?|\bwhich)\s+leverages?(?![\w-])",
     "leverage (verb)"),
    (r"(?<![\w-])leveraging(?![\w-])", "leveraging"),
    (r"(?<![\w-])robust(?![\w-])", "robust"),
    (r"(?<![\w-])seamlessly?(?![\w-])", "seamless"),
    (r"(?<![\w-])delve(?![\w-])", "delve"),
    (r"(?<![\w-])unlocks?(?![\w-])", "unlock"),
    (r"(?<![\w-])elevates?(?![\w-])", "elevate"),
    (r"(?<![\w-])streamlines?(?:d)?(?![\w-])", "streamline"),
    (r"cutting[- ]edge", "cutting-edge"),
    (r"tailored solutions", "tailored solutions"),
    (r"trusted partner", "trusted partner"),
    (r"(?:competitive|evolving|changing|regulatory|current|global|business|healthcare|market)\s+"
     r"landscape(?![\w-])", "landscape (figurative)"),
    (r"not just\b[^.<]{0,80}?\bbut\b", "not just X but Y"),
    (r"testament to", "testament to"),
    (r"navigating the", "navigating the"),
    (r"ever[- ]evolving", "ever-evolving"),
    (r"dive into", "dive into"),
]

# The PharmaTrust positioning guardrail. These words are only a problem in a
# sentence that also names the product; "a verified supplier" elsewhere is fine.
PT_FORBIDDEN = [
    "certifies", "certified", "compliant", "compliance", "pharmacopoeia",
    "guarantees", "guarantee", "regulatory approval", "passes GMP",
    "pass/fail", "verifies", "verification engine",
    "امتثال", "دستور الأدوية", "يضمن", "نجاح أو فشل",
]

# The trailing \b belongs only to the alphabetic units. Applied after "%" it
# never matches at the end of a sentence, because "%" and "." are both
# non-word characters and there is no boundary between them, so "not more
# than 0.5 %." used to pass. Proved by .automation/drqaria/prove-gates.py.
FIGURE_NEAR_THRESHOLD = re.compile(
    r"(?:threshold|limit|not more than|nmt|must not exceed|حد|عتبة)[^.<]{0,60}?"
    r"\d+(?:\.\d+)?\s*(?:%|(?:ppm|ppb|mg|µg|ug)\b)", re.I)

problems, notes = [], []


def fail(f, msg):
    problems.append(f"{os.path.relpath(f, ROOT)}: {msg}")


def note(f, msg):
    notes.append(f"{os.path.relpath(f, ROOT)}: {msg}")


def visible_text(html):
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    return re.sub(r"<[^>]+>", " ", t)


def sentences(text):
    return re.split(r"(?<=[.!?؟])\s+", text)


def check(path):
    html = open(path, encoding="utf-8").read()
    text = visible_text(html)
    name = os.path.basename(path)
    # hreflang="ar" contains lang="ar", so anchor the test to the html element.
    is_ar = '<html lang="ar"' in html
    # writing.html and writing-ar.html are the section index, not posts.
    is_index = name in ("writing.html", "writing-ar.html")
    is_post = bool(re.fullmatch(r"writing-[a-z0-9-]+?(?:-ar)?\.html", name)) and not is_index

    for ch, dash_name in DASHES.items():
        if ch in text:
            fail(path, f"contains a {dash_name}")

    for pat, label in BANNED_PATTERNS:
        if re.search(pat, text, re.I):
            fail(path, f"AI-writing marker: {label}")

    for s in sentences(text):
        if "pharmatrust" not in s.lower():
            continue
        for word in PT_FORBIDDEN:
            if word.lower() in s.lower():
                fail(path, f'"{word}" used in a sentence about PharmaTrust')

    if FIGURE_NEAR_THRESHOLD.search(text):
        fail(path, "a numeric threshold is stated as fact; cite it or cut it")

    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            fail(path, f"JSON-LD does not parse: {exc}")

    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    if not canonical:
        fail(path, "no canonical link")
    else:
        # The English homepage canonicalises to the bare host, by design.
        want = HOST + "/" if name == "index.html" else HOST + "/" + name
        if canonical.group(1) != want:
            fail(path, f"canonical is {canonical.group(1)}, expected {want}")

    if is_post:
        twin = (path[:-len("-ar.html")] + ".html") if is_ar else (path[:-len(".html")] + "-ar.html")
        if not os.path.exists(twin):
            fail(path, f"language twin missing: {os.path.basename(twin)}")
        box = re.search(r'<div class="answer-box">\s*<h2>(.*?)</h2>\s*<p>(.*?)</p>', html, re.S)
        if not box:
            fail(path, "no answer box")
        else:
            q, a = box.group(1).strip(), box.group(2).strip()
            n = len(re.sub(r"<[^>]+>", " ", a).split())
            if not 30 <= n <= 75:
                fail(path, f"answer box is {n} words; it must stand alone in 40 to 60")
            first = re.search(r'<div class="faq-item">\s*<p class="faq-q">(.*?)</p>\s*'
                              r'<p class="faq-a">(.*?)</p>', html, re.S)
            if not first:
                fail(path, "no FAQ items")
            elif first.group(1).strip() != q or first.group(2).strip() != a:
                fail(path, "FAQ item one does not match the answer box")

    for href in re.findall(r'href="(/[^"#?]*)"', html):
        target = href.lstrip("/")
        if not target:
            continue
        if not os.path.exists(os.path.join(SITE, target)):
            fail(path, f"internal link 404: {href}")

    if is_post and len(text.split()) < 500:
        note(path, f"short at {len(text.split())} words")


def main():
    args = sys.argv[1:]
    if args:
        paths = [os.path.abspath(a) for a in args]
    else:
        paths = [os.path.join(SITE, f) for f in sorted(os.listdir(SITE))
                 if f.endswith(".html")]
    for p in paths:
        check(p)

    for n in notes:
        print("note:", n)
    if problems:
        print(f"\n{len(problems)} problem(s), do not publish:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print(f"All gates passed across {len(paths)} page(s).")


if __name__ == "__main__":
    main()
