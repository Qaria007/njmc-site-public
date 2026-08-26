# Connecting Hostinger to this repository

Status as of 26 August 2026: **connected, deploying to a throwaway test path,
NOT yet cut over to the real site.** The mechanism is now fully understood.
One restructuring decision remains before the real cutover.

## What is done

- Hostinger's GitHub App is installed on `Qaria007`'s account, scoped to
  **only** `njmc-site-public` (chose "Only select repositories" over "All
  repositories" during setup, deliberately, since the default grant is
  broader than needed).
- The GIT page (`/websites/njmcmedicsupp.com/advanced/git`) shows the
  connection live: repository `njmc-site-public`, branch `main`,
  **auto-deployment ON**.
- A real deployment was run, targeted at the **custom directory
  `public_html/gittest`** (a throwaway path, not the live web root) to observe
  exactly what Hostinger's deploy does before pointing it at the real site.

## What that test proved, definitively

Hostinger's git deploy **clones the full repository and copies the entire
working tree** (everything git tracks, `.git/` itself excluded) into
`public_html/<the configured directory>`. There is **no way to choose a
source folder inside the repository** — the "Change root directory" dialog
only lets you pick or extend the **destination** path under `public_html/`.
The fixed prefix in that dialog (`public_html/`) is the server's web root, not
something inside the repo.

Verified by fetching the live result after the test deploy:

| URL | Result |
|---|---|
| `njmcmedicsupp.com/gittest/README.md` | 200 |
| `njmcmedicsupp.com/gittest/DEPLOY.md` | 200 |
| `njmcmedicsupp.com/gittest/STATUS.md` | 200 |
| `njmcmedicsupp.com/gittest/.automation/gates.py` | 200 |
| `njmcmedicsupp.com/gittest/.automation/topics.md` | 200 |
| `njmcmedicsupp.com/gittest/.gitignore` | 200 |
| `njmcmedicsupp.com/gittest/public_html/index.html` | 200, the real site, nested **one level deeper** |
| `njmcmedicsupp.com/gittest/.git/HEAD` | 403, `.git/` itself is blocked |

So with this repository's current layout, deploying to the real root would:
put `.automation/` (the writer, the gates, the topic backlog, the routine
prompt) directly on the public site; scatter `DEPLOY.md`, `README.md`,
`STATUS.md` across the live web root; and leave the **real site nested at
`public_html/public_html/`**, one level too deep, meaning none of the actual
pages the site needs would land where they are served from. **This is not
survivable as-is. Do not change the root directory to blank without fixing
the layout first.**

## The fix: flatten the repository

Everything currently under `public_html/` needs to move to the repository's
top level, so that the repo root **is** what the server should show at
`public_html/`. `.automation/`, `DEPLOY.md`, `README.md`, `STATUS.md` stay in
the repository (a future writer routine still needs them) but must be
**blocked from being served** once they sit alongside the site files, because
Hostinger will copy them there regardless. An `.htaccess` rule is what blocks
that, not `robots.txt` — `robots.txt` only asks crawlers not to index a path,
it does not stop a direct fetch, and the test above shows Hostinger will
serve them by default.

Concretely, in order:

1. `git mv public_html/* public_html/.[a-zA-Z]* .` (careful with dotfiles) to
   bring every site file up to the repository root, then remove the empty
   `public_html/` directory.
2. Every path assumption in `.automation/*.py` that currently reads
   `ROOT = "../public_html"` needs updating to the new relative position.
   Same for path references inside `DEPLOY.md`, `README.md`, `STATUS.md`.
3. Rescue the real `public_html/.htaccess` from the live server (see the
   section below, still outstanding) and add to it:
   ```apache
   <FilesMatch "^(DEPLOY|README|STATUS)\.md$">
       Require all denied
   </FilesMatch>
   <IfModule mod_alias.c>
       RedirectMatch 404 ^/\.automation/
   </IfModule>
   ```
   (or the older `Deny from all` syntax if the server is pre-2.4 Apache;
   confirm which the rescued file already uses and match it).
4. Verify locally that nothing under the new top level breaks a relative
   link, then re-run `python3 .automation/gates.py` across everything.
5. Commit the restructuring as its own commit, separate from any content
   change, so it is easy to review and easy to revert in isolation.
6. On the GIT page, change the root directory from `public_html/gittest` back
   to **blank** (the dialog says "Leave blank to deploy to public_html").
   This is the actual cutover. Auto-deployment is already on, so the next
   push to `main` after this change deploys for real.
7. Confirm live: the three URLs in the "Confirming it worked" section below,
   plus that `/DEPLOY.md`, `/README.md`, `/STATUS.md`, and `/.automation/...`
   all now 404 or 403 rather than 200.
8. Delete the `gittest` test folder from the live server (see below, needs
   File Manager, which this session cannot reach).

**Steps 1 through 5 are done, as of 26 August 2026, and verified against a
second test deploy to the same `gittest` path:**

| URL | Result |
|---|---|
| `njmcmedicsupp.com/gittest/index.html` | 200, the real homepage, at the flat top level |
| `njmcmedicsupp.com/gittest/public_html/index.html` | 404, the old nested duplicate is gone |
| `njmcmedicsupp.com/gittest/ar/insights-api-impurity-profiles.html` | 200 |
| `njmcmedicsupp.com/gittest/assets/njmc-home.css` | 200 |
| `njmcmedicsupp.com/gittest/.automation/gates.py` | still 200, expected, the deny rules are not in yet |
| `njmcmedicsupp.com/gittest/README.md` | still 200, same reason |

So the layout is exactly right. **What is left is step 3, the `.htaccess`
rescue and the deny rules, then step 6, the actual cutover.** Do the deny
rules before the cutover, not after, or the live root will briefly serve
`.automation/` and the project docs publicly, which is the exact problem this
whole restructuring exists to avoid.

**Step 6 is the point of no return for the live site and needs an explicit
go-ahead.** Everything up to and including step 5 is repository work, proven
safe against a throwaway path with no effect on what Hostinger currently
serves at the real root.

## Still outstanding, independent of the restructuring

**`public_html/.htaccess` is probably on the server and is not in this
repository.** A bogus URL on the live site returns the site's own `404.html`
rather than a plain Apache error, meaning an `ErrorDocument` rule already
exists somewhere, and that file is where such a rule lives. It cannot be read
over HTTP (`.htaccess`/`.htpasswd` both return 403, Apache's blanket rule for
`.ht*` names). It needs to be copied out of hPanel's File Manager, both to
preserve whatever it already does and because the deny rules above should be
**added to it**, not replace it.

**hPanel's File Manager cannot be driven by this session's Chrome
automation.** It opens in a popup window outside the extension's tab group.
Confirmed again on 26 August: the popup a GitHub OAuth button opened was
likewise unreachable, but that one could be worked around by capturing the
target URL via a `window.open` hook and navigating a normal tab to it
directly — File Manager's popup has not been tested with that same trick and
may or may not respond the same way. Either way, for now: have Majid open it,
or use SSH/FTP.

**The `gittest` test deployment is still live and still exposes
`.automation/` and the project docs at guessable-but-unlinked URLs.** Nothing
secret is in it, but it should be deleted once File Manager is reachable,
independent of anything else in this checklist.

## Confirming it worked, once the real cutover happens

- https://njmcmedicsupp.com/insights-api-impurity-profiles.html
- https://njmcmedicsupp.com/ar/insights-api-impurity-profiles.html
- https://njmcmedicsupp.com/definitely-not-a-real-page should still show the
  NJMC 404 page, which proves `.htaccess` survived
- https://njmcmedicsupp.com/DEPLOY.md and
  https://njmcmedicsupp.com/.automation/gates.py should both fail, which
  proves the deny rules are in effect

Re-run the mirror comparison in `STATUS.md` afterwards to confirm nothing else
on the site changed.
