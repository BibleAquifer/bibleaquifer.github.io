# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BibleAquifer static site — a GitHub Pages site (bibleaquifer.github.io) that catalogs 40+ Bible resources across 15+ languages. A Python build script fetches data from the GitHub API and generates fully static HTML with all resource data embedded as JSON. There are zero runtime API calls.

## Build Commands

```bash
# Install dependencies (requires Python 3.9+, Poetry)
poetry install

# Build site with live GitHub data (requires API token)
export manage-aquifer=<token>   # or GITHUB_AQUIFER_API_KEY
poetry run python src/build_site.py

# Build with sample data (no token needed)
poetry run python src/generate_sample.py

# Build with debug mode (sample data via flag)
DEBUG_MODE=true poetry run python src/build_site.py

# Run tests (uses sample data, outputs to src/test_*.html)
poetry run python src/test_build.py

# Local preview
python3 -m http.server 8080
```

## Architecture

**Build-time (Python):** `src/build_site.py` is the core of the project (~1400 lines). It:
1. Fetches the org README from `BibleAquifer/.github/profile/README.md`
2. Discovers all BibleAquifer repos via GitHub API (excludes `docs`, `ACAI`, `.github`, `bibleaquifer.github.io`)
3. Scans each repo for 3-letter ISO 639-3 language directories
4. Downloads `metadata.json` per language to extract titles, citations, formats, content lists
5. Generates `index.html` (landing page) and `catalog.html` (interactive catalog) using Jinja2 templates embedded in the script
6. Exports `resources_data.yaml` as a reference file (not used by the site)

**Runtime (browser):** Pure vanilla JavaScript embedded in `catalog.html`. No frameworks. The entire `RESOURCES_DATA` object is embedded as a `<script>` block. JS populates dropdowns and displays metadata/content from this object.

**Navigation files:** `nav/` contains JSON files (`{ResourceName}_{langCode}.json`) with `path`/`label` arrays for content navigation within each resource.

## Key Files

- `src/build_site.py` — Main build script (templates, API calls, data processing)
- `src/test_build.py` — Test suite (custom, no pytest)
- `src/generate_sample.py` — Sample data generator for local dev
- `styles.css` — All site styling
- `.github/workflows/build-site.yml` — CI workflow: builds site and deploys to `gh-pages` branch
- `index.html`, `catalog.html`, `nav/*.json` — **Generated output** (gitignored; built by CI, deployed to `gh-pages`)

## Important Patterns

- **Generated files are gitignored.** `index.html`, `catalog.html`, `resources_data.yaml`, and `nav/*.json` are build outputs deployed to the `gh-pages` branch by CI. They are not tracked on `main`.
- **Jinja2 templates live inside `build_site.py`**, not as separate template files.
- **Content label transforms** depend on `resource_metadata/order`: `canonical` maps Bible book codes to names (e.g., GEN → Genesis), `alphabetical` uppercases for Roman scripts, `monograph` strips path prefixes.
- **`LANGUAGE_MAP`** in `build_site.py` maps 3-letter ISO codes to display names. Add new languages there.
- **GitHub API retry strategy:** Exponential backoff with 7 retries, plus rate-limit-aware waiting.
