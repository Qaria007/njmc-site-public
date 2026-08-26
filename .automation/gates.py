#!/usr/bin/env python3
"""Pre-publish gates for njmcmedicsupp.com pages.

Usage:
    python3 .automation/gates.py                 # check every page on the site
    python3 .automation/gates.py <file> [file..] # check specific pages

Exit code 0 means every gate passed. Anything else means do not publish.
The rules encode the NJMC content guardrails: no invented regulatory figures,
no manufacturer claim, no em dashes, no AI-writing markers, valid structured
data, and every internal link resolving to a file that actually exists.
"""
import json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ROOT = os.path.normpath(ROOT)

# 1. Dashes. Em dash, en dash, and the horizontal bar.
DASHES = {"—": "em dash", "–": "en dash", "―": "horizontal bar"}

# 2. AI-writing markers, as regexes so a legitimate use does not trip the gate.
#    "the leverage to change supplier" is ordinary English; "we leverage our network"
#    is the marker. Same for "not just the offer" versus "not just X but Y".
BANNED_PATTERNS = [
    (r"(?<![\w-])moreover(?![\w-])", "moreover"),
    (r"(?<![\w-])furthermore(?![\w-])", "furthermore"),
    (r"(?<![\w-])additionally(?![\w-])", "additionally"),
    (r"in today's", "in today's"),
    (r"it is important to note", "it is important to note"),
    # leverage as a verb only
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
    # landscape only in the figurative sense, next to an adjective
    (r"(?:competitive|evolving|changing|regulatory|current|global|business|healthcare|market)\s+"
     r"landscape(?![\w-])", "landscape (figurative)"),
    (r"not just\b[^.<]{0,80}?\bbut\b", "not just X but Y"),
    (r"testament to", "testament to"),
    (r"navigating the", "navigating the"),
    (r"ever[- ]evolving", "ever-evolving"),
    (r"dive into", "dive into"),
]

# 3. Claims NJMC must never make. It sources, trades and consults; it does not manufacture.
MANUFACTURER_CLAIMS = [
    r"\bwe manufacture\b", r"\bwe produce\b", r"\bour factory\b", r"\bour factories\b",
    r"\bour manufacturing (?:site|plant|facility)\b", r"\bNJMC manufactures\b",
    r"\bour GMP certificate\b", r"\bwe are (?:GMP|CE|FDA|SFDA)[- ]", r"\bNJMC is (?:GMP|CE|FDA)",
    r"نحن نصنع", r"مصنعنا", r"ننتج في مصانعنا",
]

# 4. Regulatory figures stated as fact. Percentages and ppm next to threshold language
#    are the shape of an invented limit.
FIGURE_NEAR_THRESHOLD = re.compile(
    r"(?:threshold|limit|not more than|nmt|must not exceed|حد|عتبة)[^.<]{0,60}?"
    r"\d+(?:\.\d+)?\s*(?:%|ppm|ppb|mg|µg|ug)\b", re.I)

SELF_CLOSING_OK = {"/", "#"}

problems = []
notes = []


def fail(f, msg):
    problems.append(f"{os.path.relpath(f, ROOT)}: {msg}")


def note(f, msg):
    notes.append(f"{os.path.relpath(f, ROOT)}: {msg}")


def visible_text(html):
    """Strip script, style and tags so vocabulary gates do not fire on markup."""
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return t


def check(path):
    html = open(path, encoding="utf-8").read()
    text = visible_text(html)
    rel = os.path.relpath(path, ROOT)
    # The 404 page is deliberately noindex and carries no canonical or schema.
    if rel == "404.html":
        return
    is_ar = rel.startswith("ar/") or '<html lang="ar"' in html

    # --- leftover scaffolding -------------------------------------------------
    for marker in ("REPLACE BEFORE UPLOAD", "TODO-OWNER", "Lorem ipsum"):
        if marker in html:
            if marker == "TODO-OWNER":
                note(path, "carries a TODO-OWNER comment (intentional, invisible to readers)")
            else:
                fail(path, f"contains leftover marker {marker!r}")

    # --- dashes ---------------------------------------------------------------
    for ch, name in DASHES.items():
        n = html.count(ch)
        if n:
            fail(path, f"{n} {name}(s) present")

    # --- AI-writing markers ---------------------------------------------------
    low = text.lower()
    for pat, label in BANNED_PATTERNS:
        m = re.search(pat, low)
        if m:
            fail(path, f"AI-writing marker {label!r} in {m.group(0).strip()!r}")

    # --- manufacturer claims --------------------------------------------------
    for pat in MANUFACTURER_CLAIMS:
        if re.search(pat, text, re.I):
            fail(path, f"reads as a manufacturer claim: {pat!r}")

    # --- regulatory figures ---------------------------------------------------
    for m in FIGURE_NEAR_THRESHOLD.finditer(text):
        fail(path, f"regulatory figure stated as fact: {m.group(0).strip()!r}")

    # --- head essentials ------------------------------------------------------
    titles = re.findall(r"<title>(.*?)</title>", html, re.S)
    if len(titles) != 1:
        fail(path, f"{len(titles)} <title> tags, expected 1")
    elif len(titles[0]) > 62:
        note(path, f"title is {len(titles[0])} chars (over the 62 target)")

    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    if len(h1s) != 1:
        fail(path, f"{len(h1s)} <h1> tags, expected 1")

    desc = re.search(r'<meta name="description" content="([^"]*)"', html)
    if not desc:
        fail(path, "no meta description")
    elif not 140 <= len(desc.group(1)) <= 165:
        note(path, f"meta description is {len(desc.group(1))} chars (target 140 to 165)")

    canon = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    if not canon:
        fail(path, "no canonical link")
    else:
        # The homepage canonicalises to the bare origin, which is correct.
        expect = {"index.html"}
        if rel == "index.html":
            expect = {"https://njmcmedicsupp.com/", "https://njmcmedicsupp.com/index.html"}
        else:
            expect = {"https://njmcmedicsupp.com/" + rel}
        if canon.group(1) not in expect:
            fail(path, f"canonical is {canon.group(1)}, expected {' or '.join(sorted(expect))}")

    # --- hreflang -------------------------------------------------------------
    if "insights" in rel:
        langs = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', html))
        for want in ("en", "ar", "x-default"):
            if want not in langs:
                fail(path, f"missing hreflang {want}")
        if langs.get("x-default") and langs.get("en") and langs["x-default"] != langs["en"]:
            fail(path, "x-default does not match the English alternate")

    # --- structured data ------------------------------------------------------
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if not blocks:
        fail(path, "no JSON-LD block")
    faq_names = []
    for i, b in enumerate(blocks):
        try:
            data = json.loads(b)
        except json.JSONDecodeError as e:
            fail(path, f"JSON-LD block {i + 1} does not parse: {e}")
            continue
        if data.get("@type") == "FAQPage":
            faq_names = [q["name"] for q in data.get("mainEntity", [])]

    # FAQ schema questions must match the on-page <summary> text exactly.
    if faq_names:
        summaries = [re.sub(r"\s+", " ", visible_text(s)).strip()
                     for s in re.findall(r"<summary>(.*?)</summary>", html, re.S)]
        norm = [re.sub(r"\s+", " ", n).replace("&quot;", '"').strip() for n in faq_names]
        summaries = [s.replace("&quot;", '"') for s in summaries]
        if norm != summaries:
            fail(path, f"FAQ schema questions do not match <summary> text\n"
                       f"      schema:  {norm}\n      summary: {summaries}")

    # --- answer box -----------------------------------------------------------
    if "insights-" in rel and 'class="answer-box"' not in html:
        fail(path, "no answer box near the top of the article")

    # --- internal links resolve ----------------------------------------------
    for href in re.findall(r'href="(/[^"#?]*)"', html):
        if href in SELF_CLOSING_OK:
            continue
        target = os.path.join(ROOT, href.lstrip("/"))
        if href.endswith("/"):
            target = os.path.join(target, "index.html")
        if not os.path.exists(target):
            fail(path, f"internal link does not resolve: {href}")

    # --- language switch points at the twin -----------------------------------
    if "insights-" in rel:
        toggle = re.search(r'class="lang-toggle" href="([^"]+)"', html)
        if toggle:
            want = ("/" + rel[3:]) if is_ar else ("/ar/" + rel)
            if toggle.group(1) != want:
                note(path, f"language toggle points at {toggle.group(1)}, twin is {want}")


targets = sys.argv[1:]
if not targets:
    targets = [os.path.join(dp, f) for dp, _, fs in os.walk(ROOT)
               for f in fs if f.endswith(".html")]

for t in sorted(targets):
    check(os.path.abspath(t))

if notes:
    print("NOTES (not blocking)")
    for n in notes:
        print("  -", n)
    print()

if problems:
    print(f"FAILED {len(problems)} gate(s)")
    for p in problems:
        print("  x", p)
    sys.exit(1)

print(f"All gates passed across {len(targets)} page(s).")
