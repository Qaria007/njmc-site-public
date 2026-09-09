"""Break each drqaria gate once, on a copy, and confirm it fires.

A gate that has never failed is not known to work. This writes a temporary
corrupted copy of a real page, runs gates.py on it, and checks the expected
message appears. Nothing in the repo is modified.
"""
import os, re, shutil, subprocess, sys, tempfile

REPO = "/Users/zhula/njmc-site"
SITE = os.path.join(REPO, "drqaria")
GATES = os.path.join(REPO, ".automation", "drqaria", "gates.py")
SRC = os.path.join(SITE, "writing-antibiotic-resistance-supply-chain.html")

CASES = [
    ("en dash", lambda h: h.replace("<p>My doctoral", "<p>2015 – 2018. My doctoral"), "en dash"),
    ("AI marker", lambda h: h.replace("<p>My doctoral", "<p>Moreover, my doctoral"), "moreover"),
    ("PharmaTrust word", lambda h: h.replace("built <a href=\"https://pharmatrust.tech\"",
                                             "built compliance software, <a href=\"https://pharmatrust.tech\""),
     "PharmaTrust"),
    ("threshold figure", lambda h: h.replace("<p>My doctoral",
                                             "<p>The limit is not more than 0.5 %. My doctoral"), "threshold"),
    ("broken JSON-LD", lambda h: h.replace('"@type": "BlogPosting"', '"@type" "BlogPosting"', 1), "JSON-LD"),
    ("bad canonical", lambda h: h.replace('rel="canonical" href="https://drqaria.njmcmedicsupp.com/writing-antibiotic-resistance-supply-chain.html"',
                                          'rel="canonical" href="https://example.com/wrong.html"'), "canonical"),
    ("dead internal link", lambda h: h.replace('href="/writing.html"', 'href="/does-not-exist.html"'), "404"),
    ("answer box gone", lambda h: re.sub(r'<div class="answer-box">.*?</div>', "", h, flags=re.S), "answer box"),
]

failed = []
for label, corrupt, expect in CASES:
    tmp = os.path.join(SITE, "writing-gateproof-tmp.html")
    twin = os.path.join(SITE, "writing-gateproof-tmp-ar.html")
    try:
        html = open(SRC, encoding="utf-8").read()
        broken = corrupt(html)
        if broken == html:
            failed.append(f"{label}: the corruption changed nothing, test is invalid")
            continue
        broken = broken.replace("writing-antibiotic-resistance-supply-chain",
                                "writing-gateproof-tmp")
        open(tmp, "w", encoding="utf-8").write(broken)
        shutil.copy(SRC, twin)
        out = subprocess.run([sys.executable, GATES, tmp],
                             capture_output=True, text=True).stdout
        hit = expect.lower() in out.lower() and "problem" in out.lower()
        print(("PASS " if hit else "MISS ") + label)
        if not hit:
            failed.append(f"{label}: gate did not fire. output was:\n{out}")
    finally:
        for f in (tmp, twin):
            if os.path.exists(f):
                os.remove(f)

print()
if failed:
    print("GATES THAT DID NOT BITE:")
    for f in failed:
        print(" -", f)
    sys.exit(1)
print("Every gate fired when broken.")
