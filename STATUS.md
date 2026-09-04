# Where this stands, 4 September 2026

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

## LIVE, as of 4 September 2026

The cutover happened at 06:00 UTC on 4 September. Hostinger's root directory
is `public_html` (blank subfolder), auto-deployment is on, and every push to
`main` now publishes. Verified from outside immediately afterwards:

- both article pages 200 at the real root
- `drqaria.njmcmedicsupp.com` and `/drqaria/` both 200, so the subdomain survived
- `.automation/`, `DEPLOY.md`, `README.md`, `STATUS.md`, `.gitignore` all 403
- `gittest/` gone (404), the custom 404 page intact, http and www still 301
- all 51 servable committed files byte for byte identical to the live server

**The weekly writer is scheduled.** Cloud routine "NJMC weekly Insights
article", id `trig_01FLNWL7NqGoxUm46g3KtUxo`, cron `0 1 * * 2` (Tuesday 01:00
UTC, 09:00 Asia/Shanghai), model claude-sonnet-5, repo
`Qaria007/njmc-site-public`, tools Bash/Read/Write/Edit/Glob/Grep only, no
connectors, no web. Manage at
https://claude.ai/code/routines/trig_01FLNWL7NqGoxUm46g3KtUxo. The prompt is
`.automation/routine-prompt.md` verbatim (plus a two-sentence preamble saying
the repo is the live web root and a push is a publish). Change the file, then
paste the new text into the routine; the routine does not read the file.

**Every article is written for search, answer and generative engines.** The
answer box is a question H2 with a 40 to 60 word answer that is also FAQ item
0; one canonical NJMC sentence appears in every article and its schema; each
topic carries a registered query; each new article gets a backlink from an
older one. All enforced by `gates.py`. Details in `.automation/README.md`.

**What the writer deliberately does not do:** score topics from live data,
check what ranks, submit for indexing. That is the weekly review from the Mac
(growth-engine skill, weekly cycle), which reorders `.automation/topics.md`.

## What was true before the cutover (kept for the record)

`DEPLOY.md` is the checklist, now much further along. As of 26 August 2026:

- **The GitHub connection is done.** Hostinger's GitHub App is installed,
  scoped to only `njmc-site-public` (not "all repositories"), and the GIT page
  shows it connected with auto-deployment on.
- **The deploy mechanism is now fully understood, by testing it against a
  throwaway path.** Hostinger's git deploy copies the ENTIRE repository into
  `public_html/<chosen directory>` — there is no way to pick a source folder
  inside the repo, only the destination. Tested by deploying to
  `public_html/gittest` and fetching the result: the real site landed one
  level too deep at `gittest/public_html/index.html`, while `.automation/`,
  `DEPLOY.md`, `README.md` and `STATUS.md` were all directly and publicly
  fetchable at the top of that test path. Deploying to the real root as the
  repository is laid out today would break the site and expose the tooling.
- **The fix is understood and written up in `DEPLOY.md`, not yet executed.**
  Flatten the repository so site files sit at the top level, move the
  `.automation/*.py` path assumptions to match, add real `.htaccess` deny
  rules for the docs and tooling (robots.txt is not enough, it does not stop
  a direct fetch), then change the GIT page's root directory from
  `public_html/gittest` to blank. That last step is the actual cutover, since
  auto-deployment is already on. **It needs Majid's go-ahead before it
  happens**, same as any other live-site change.
- **`public_html/.htaccess` is still not rescued.** Still needed both to
  preserve what it already does (it drives the site's custom 404 page) and as
  the place the new deny rules get added.
- **The `gittest` test deployment is still live** at
  `njmcmedicsupp.com/gittest/...` and exposes `.automation/` and the project
  docs at an unlinked but guessable path. Not secret, but should be deleted.

Hostinger's File Manager still cannot be reached by this session's browser
automation — it opens in a popup outside the extension's tab group. The
GitHub OAuth popup had the same problem but was worked around by capturing the
`window.open` target URL and navigating a normal tab to it directly; that
trick has not been tried against File Manager. Use SSH, FTP, or have Majid
copy the file by hand.

## The hosting-plan question is resolved

The 25 August dashboard reading that worried about a 6 September expiry was
the old Cloud Professional plan, not this site. Confirmed 26 August by
searching for njmcmedicsupp.com directly in hPanel's Websites page: it now
lists under a **Business** plan card, "Plan expires on 2030-08-23". The 6
September warning belongs to the old plan's other, now-abandoned sites, exactly
as the account migration record describes.

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
