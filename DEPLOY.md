# Connecting Hostinger to this repository

Read this before touching the GIT page in hPanel. Two of the steps exist to
stop a deploy from damaging the live site, so do them in order.

## Before anything: what we know and what we do not

The repository is a faithful copy of the live site. On 18 August 2026 every one
of the 39 files that this pipeline did not write was confirmed **byte for byte
identical** to what the server was serving.

But a crawl can only see files that are linked or served. Two gaps remain:

1. **`.htaccess` is almost certainly present on the server and is not in this
   repository.** Requesting a page that does not exist returns the site's own
   `404.html` rather than the plain Apache error, which means an
   `ErrorDocument` rule is active. That rule has to live somewhere, and
   `public_html/.htaccess` is where. Requesting the file directly returns 403,
   which is Apache's blanket rule for `.ht*` names, so its contents cannot be
   read from outside.
2. Any other file that nothing links to would also have been missed.

**Step 2 below closes gap 1. Do not skip it.**

## Step 1. Take a backup

hPanel, Files, Backups, generate a new file backup for njmcmedicsupp.com, and
wait for it to finish. Everything after this is reversible if that backup
exists, and awkward if it does not.

## Step 2. Rescue the .htaccess file

hPanel, Files, File Manager, open `public_html`. Turn on hidden files if you do
not see it (the toggle is usually in the top right or the settings menu). Open
`.htaccess`, copy everything in it, and paste it back to me.

I will commit it to the repository so a deploy restores it rather than removing
it. If the file genuinely does not exist, tell me that instead and we carry on.

Do the same for any other file in `public_html` that is not in this repository.
The full list of what the repository has is in `public_html/`; anything on the
server beyond that is worth mentioning.

## Step 3. Learn where Hostinger puts things, without risking the site

hPanel, Advanced, GIT.

Create a repository with:

- **Repository address:** `https://github.com/Qaria007/njmc-site-public.git`
- **Branch:** `main`
- **Directory / install path:** `gittest`

`gittest` does not exist yet, which is the point. Hostinger will create it and
clone into it, and the live site is untouched whatever happens.

Then open File Manager and find where `gittest` landed. Tell me the full path,
for example `/home/uXXXXXXX/gittest` or
`/home/uXXXXXXX/domains/njmcmedicsupp.com/gittest`.

That one path answers the question this repository's layout depends on, which
is where `public_html` sits relative to where Hostinger installs.

## Step 4. Point it at the real location

This repository keeps the site inside a `public_html/` folder, alongside the
`.automation/` tooling. So the install path must be **the folder that contains
`public_html`**, not `public_html` itself.

Using the path you report in step 3:

- If `gittest` landed at `/home/uXXXXXXX/gittest`, then the install path is
  the home directory, usually written as `.` or left empty.
- If it landed at `/home/uXXXXXXX/domains/njmcmedicsupp.com/gittest`, then the
  install path is `domains/njmcmedicsupp.com`.

Get this wrong in the obvious direction and you get
`public_html/public_html/index.html`, and the site serves nothing. That is why
step 3 exists.

**Before you confirm this one, tell me the path and let me check it.** This is
the only step in the list that writes into the live web root.

One caveat worth knowing: some Hostinger setups refuse to clone into a folder
that is not empty, and others clone over the top. If it refuses, say so rather
than emptying anything, and we will switch to uploading over FTP from a GitHub
Action instead, which only ever touches the files an article changes.

## Step 5. Turn on auto deployment

On the same GIT page there is an auto deployment toggle, which gives you a
webhook URL. Turn it on. Hostinger then pulls every push to `main` by itself.

## Step 6. Delete the test folder

Remove `gittest` from File Manager, and remove its entry from the GIT page.

## Step 7. Confirm it worked

The impurity-profiles article is already committed, so the first successful
deploy publishes it. Check:

- https://njmcmedicsupp.com/insights-api-impurity-profiles.html
- https://njmcmedicsupp.com/ar/insights-api-impurity-profiles.html
- https://njmcmedicsupp.com/definitely-not-a-real-page still shows the NJMC
  404 page, which proves `.htaccess` survived

Tell me when it is done and I will verify all three from here.
