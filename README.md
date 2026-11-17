# bibleaquifer.github.io (retired)

> **This site has moved.** The Aquifer Catalog is now at **https://catalog.aquifer.bible**.

`bibleaquifer.github.io` now only redirects to https://catalog.aquifer.bible. It was retired on December 1, 2026.

## What this repository contains

- `redirect/`: the static pages published to GitHub Pages. `index.html`, `catalog.html` and `404.html` all redirect to the new site (meta refresh plus a JavaScript redirect), so old deep links also land there. GitHub Pages cannot send a real HTTP 301.
- `.github/workflows/build-site.yml`: deploys `redirect/` to the `gh-pages` branch when it changes. There is no scheduled build and no API token.
- `src/`, `styles.css`, `BUILD.md`, `IMPLEMENTATION_SUMMARY.md`: the retired site generator, kept for reference. It is no longer run or deployed.

Do not delete or rename this repository, or the redirect will stop working.
