# Where this stands, 25 August 2026

Written so this work can be picked up with no memory of the conversation that
produced it.

## The goal

Automate NJMC Insights articles the way LNJC's are automated: a writer produces
an English and Arabic article on a schedule, it passes content gates, and it
publishes itself. Cadence chosen by Majid: **weekly**.

## Why NJMC could not simply copy LNJC

LNJC's blog is a **GitHub Pages** repository, so a push is a deploy. NJMC's site
is hand written static HTML on **Hostinger**, and a push reaches nothing on its
own. A deploy bridge is required, and that bridge is the only unfinished piece.

There was also **no working copy of the site anywhere** before this. It existed
only on Hostinger. `public_html/` here is a crawl of the live site.

## Done and pushed

Remote: `https://github.com/Qaria007/njmc-site-public` (public, branch `main`).

- The full site under `public_html/`, 42 files.
  **Verified 25 August 2026:** all 39 files this pipeline did not write were
  byte for byte identical to what the server was serving.
- The writing pipeline under `.automation/`. See `.automation/README.md`.
- The first article, on API impurity profiles, English and Arabic, built,
  gate-passed, browser-checked in both directions, and wired into both Insights
  index pages and `sitemap.xml`. **Not live yet**, because the deploy bridge is
  not connected. It publishes itself on the first successful deploy.

## Not done

`DEPLOY.md` is the checklist. Two blockers, both needing Majid:

1. **The GIT page needs a GitHub OAuth grant.** hPanel's GIT page is not the
   old "repository URL plus install path" form; it is a single **Connect with
   GitHub** button. Nobody has clicked it, so what the next screen offers is
   unknown, including whether a target directory can be chosen. That answer
   decides whether this repository's layout has to change, see `DEPLOY.md`.
2. **`public_html/.htaccess` is probably on the server and is not in here.** A
   bogus URL returns the site's own `404.html`, so an `ErrorDocument` rule is
   active. It cannot be read over HTTP. It must be copied out of hPanel's File
   Manager before any deploy that could replace `public_html`.

Hostinger's File Manager opens in a **popup window outside the Chrome
extension's tab group**, so browser automation cannot reach it. Three routes
were tried and all stopped at the "Access files" chooser. Use SSH, FTP, or have
Majid copy the file by hand.

## One thing to check before acting

On 25 August 2026 at about 06:20 UTC, njmcmedicsupp.com's hPanel dashboard read
**"Hosting plan: Cloud Professional Hosting"**, and the Websites page carried
"Hosting plan will expire on 2026-09-06 and your website(s) will go offline."

That **conflicts** with the account migration record, which says
njmcmedicsupp.com was moved to the Business plan earlier the same day and that
the Cloud Professional plan is being allowed to lapse on purpose, keeping only
fallback copies. The site's DNS does not resolve to the old plan's direct IP,
which is consistent with the migration having happened.

So the expiry warning is **probably the expected lapse of the old plan and not
a threat to this site** — but the dashboard reading was not explained. Confirm
which plan njmcmedicsupp.com is actually on before treating either version as
fact, and before assuming the site survives 6 September.

## How to verify the mirror again later

```bash
cd ~/njmc-site/public_html
python3 - <<'PY'
import hashlib, os, urllib.request
ORIGIN="https://njmcmedicsupp.com"
for dp,_,fs in os.walk("."):
    for f in sorted(fs):
        rel=os.path.relpath(os.path.join(dp,f),".").replace(os.sep,"/")
        try:
            live=urllib.request.urlopen(
                urllib.request.Request(ORIGIN+"/"+rel,
                    headers={"User-Agent":"njmc-verify/1.0"}),timeout=30).read()
        except Exception as e:
            print("UNREACHABLE",rel,e); continue
        if hashlib.sha256(live).digest()!=hashlib.sha256(open(rel,"rb").read()).digest():
            print("DIFFERS",rel)
PY
```

Silence means the repository and the live site agree.

## Local extras not in this repository

- `~/.claude/launch.json` briefly held an `njmc-preview` entry for previewing
  `public_html/` on port 8788. It has since been replaced by other entries. The
  copy in `.claude/launch.json` here still works if run from this directory.
