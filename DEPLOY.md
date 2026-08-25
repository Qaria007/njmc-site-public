# Connecting Hostinger to this repository

Status as of 25 August 2026: **not connected yet.** Two blockers, both needing
Majid. Everything else is done and pushed.

## Blocker 0, and it outranks the rest: the hosting plan is expiring

hPanel shows, on the Websites page and on the njmcmedicsupp.com dashboard:

> Hosting plan will expire on 2026-09-06 and your website(s) will go offline.

njmcmedicsupp.com is still sitting on the **Cloud Professional** plan. That is
worth checking against the account migration that was supposed to have moved
every site onto the newer Business plan, because this one looks like it was
left behind. Automating a weekly article onto a site that goes dark on 6
September is not worth doing until this is settled.

## What the GIT page actually looks like

hPanel, njmcmedicsupp.com, Advanced, GIT
(`https://hpanel.hostinger.com/websites/njmcmedicsupp.com/advanced/git`).

It is **not** the older "paste a repository URL and an install path" form that
most guides describe. As of 25 August 2026 it shows a single empty state:

> **Deploy from GitHub**
> Connect your GitHub account via OAuth to deploy from your repositories.
> [ Connect with GitHub ]

So the first step is an OAuth grant from Majid's GitHub account to Hostinger.
It is reversible afterwards from GitHub, Settings, Applications.

**What happens past that screen is unknown**, because nobody has clicked it.
Specifically, whether Hostinger lets you choose the directory it deploys into.
That one answer decides the repository layout, see the next section.

## The layout question that hangs on it

This repository currently keeps the site inside a `public_html/` folder, with
the `.automation/` tooling beside it:

```
njmc-site-public/
  public_html/      <- the site
  .automation/      <- tooling, not meant to be served
  DEPLOY.md, README.md, STATUS.md
```

That layout is right **if** Hostinger lets you deploy into the folder that
contains `public_html`, which keeps the tooling out of the web root.

If Hostinger instead deploys the repository root straight into `public_html`,
this layout produces `public_html/public_html/index.html` and the site serves
nothing. In that case the fix is to move the site files to the top level of the
repository and add `Disallow: /.automation/` to `robots.txt`. It is a small
change, but it has to be made **before** the first deploy, not after.

## The .htaccess that is not in this repository

Requesting a URL that does not exist returns the site's own `404.html` rather
than a plain Apache error, which means an `ErrorDocument` rule is active
somewhere, and `public_html/.htaccess` is where such a rule lives. A crawl
cannot read it: Apache returns 403 for any `.ht*` name whether the file exists
or not, and `.htpasswd` returns 403 too, which shows the 403 is a blanket rule
rather than evidence.

So the repository is a faithful copy of the site **except possibly for this one
file**, and if a deploy ever replaces `public_html`, the custom 404 page and
anything else in that file go with it.

To close the gap: hPanel, Files, File Manager, `public_html`, enable hidden
files, open `.htaccess`, copy the contents into the repository at
`public_html/.htaccess`.

Note for whoever picks this up with browser automation: Hostinger's File
Manager opens in a **separate popup window** that falls outside the Chrome
extension's tab group, so it cannot be driven that way. Three routes were tried
on 25 August 2026 and all reached the "Access files" chooser and stopped there.
Either Majid copies the file out by hand, or use SSH or FTP instead.

## Safe order of work, once the plan is renewed

1. Renew or migrate the hosting so the site is not going offline.
2. Take a file backup: hPanel, Files, Backups. Everything after this is
   recoverable.
3. Rescue `public_html/.htaccess` into the repository, as above.
4. Click **Connect with GitHub** on the GIT page and read what the next screen
   offers, in particular whether a target directory can be chosen.
5. Decide the repository layout from that answer, and restructure **before**
   deploying if the root is forced.
6. If a target directory can be chosen, point the first attempt at a throwaway
   folder such as `gittest` rather than the live web root, confirm where the
   files land, then reconfigure. If no such choice exists, rely on the backup
   from step 2.
7. Turn on auto deployment, remove the test folder.

## Confirming it worked

The impurity-profiles article is already committed, so the first successful
deploy publishes it:

- https://njmcmedicsupp.com/insights-api-impurity-profiles.html
- https://njmcmedicsupp.com/ar/insights-api-impurity-profiles.html
- https://njmcmedicsupp.com/definitely-not-a-real-page should still show the
  NJMC 404 page, which proves `.htaccess` survived

Re-run the mirror comparison in `STATUS.md` afterwards to confirm nothing else
on the site changed.
