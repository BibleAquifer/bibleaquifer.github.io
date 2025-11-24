# Bible Aquifer - Static Site Frontend

This is the static site frontend for the Bible Aquifer organization on GitHub. It provides a user-friendly interface to browse and access biblical resources from the various BibleAquifer repositories.

## Live Site

The site is automatically deployed to GitHub Pages at: https://bibleaquifer.github.io

## Site Structure

The site consists of two statically-generated pages:

### Landing Page (`index.html`)
An informational page that introduces Aquifer Bible Resources with content from the BibleAquifer organization profile. Features:
- Overview of open source Bible resources for the global church
- Information about resource-level organization
- Available openly-licensed resources
- Documentation and schemas
- Call-to-action button to access the Unified Catalog
- **Static Content**: README content is embedded during build time (no dynamic loading)

### Unified Catalog (`catalog.html`)
An interactive catalog for browsing resources by type and language. Features:
- **Resource Selection**: Dropdown listing all available BibleAquifer data repositories using proper resource titles from metadata (e.g., "Translation Notes (unfoldingWord)" instead of "UWTranslationNotes")
- **Language Selection**: Dropdown showing available languages for the selected resource
- **Default to English**: Automatically selects and loads English ("eng") language when available
- **Citation Display**: Shows proper citation from resource metadata including title, copyright, and license information
- **Resource Information**: Displays metadata including language, version, type, and content type
- **Download Links**: Direct access to browse JSON, Markdown, PDF, and DOCX files (when available)
- **Static Generation**: All resource data is embedded in the HTML during build time
- **Clean UI**: Empty sections remain hidden until populated with data

## Features

- **Static Site Generation**: Pages are pre-built using a Python script
- **Two-Page Design**: Informational landing page and interactive catalog
- **Header Navigation**: Quick access to Unified Catalog, Home, and GitHub Organization
- **Fast Loading**: All data is embedded in HTML, no API calls needed at runtime
- **Proper Resource Titles**: Uses actual resource names from metadata instead of repository names
- **Responsive Design**: Works on desktop and mobile devices
- **No Runtime Dependencies**: Pure vanilla JavaScript, HTML5, and CSS3

## How It Works

The site is built using `src/build_site.py`, which:

1. **Fetches Organization README**: Retrieves content from `BibleAquifer/.github/profile/README.md`
2. **Discovers Resources**: Queries GitHub API for all repositories (excluding `docs`, `ACAI`, `.github`, and `bibleaquifer.github.io`)
3. **Detects Languages**: Scans each repository for 3-letter ISO 639-3 language code directories (e.g., `eng`, `spa`, `fra`)
4. **Fetches Metadata**: Downloads `metadata.json` for each language to extract:
   - Resource title from `resource_metadata.title` or `resource_metadata.license_info.title`
   - Version, type, content type
   - Citation information (title, copyright, license)
5. **Checks Formats**: Verifies existence of `pdf` and `docx` directories
6. **Generates HTML**: Creates `index.html` and `catalog.html` with all data embedded

At runtime, the catalog uses vanilla JavaScript to:
- Populate dropdowns from embedded data
- Display resource information when selections change
- Show download links for available formats

## Building the Site

See [BUILD.md](BUILD.md) for detailed instructions on:
- Setting up the Python environment with Poetry
- Running the build script
- Testing with sample data
- Deploying updates

Quick start:
```bash
# Install dependencies
pip install poetry
poetry install

# Build the site (requires GitHub API access)
export GITHUB_TOKEN=your_token_here
poetry run python src/build_site.py

# Test the build script (no API access needed)
poetry run python src/test_build.py

# Generate with sample data
poetry run python src/generate_sample.py
```

## Repository Structure Expected

The site expects BibleAquifer data repositories to follow this structure:

```
RepositoryName/
├── README.md
├── eng/                    # 3-letter ISO 639-3 language code
│   ├── metadata.json       # Language-level metadata
│   ├── json/              # JSON format articles
│   │   ├── article1.json
│   │   └── article2.json
│   └── md/                # Markdown format articles
│       ├── article1.md
│       └── article2.md
├── spa/                    # Another language
│   ├── metadata.json
│   ├── json/
│   └── md/
└── ...
```

## Local Development

To work on the site locally:

1. Clone this repository:
   ```bash
   git clone https://github.com/BibleAquifer/bibleaquifer.github.io.git
   cd bibleaquifer.github.io
   ```

2. Build the site (see [BUILD.md](BUILD.md) for details):
   ```bash
   poetry install
   poetry run python src/build_site.py
   ```

3. Start a local web server:
   ```bash
   python3 -m http.server 8080
   ```

4. Open your browser to `http://localhost:8080`

The generated HTML files are committed to the repository and served by GitHub Pages.

## Technologies Used

- **Python 3.9+**: Build script and site generator
- **Poetry**: Python dependency management
- **Jinja2**: HTML template engine
- **PyYAML**: YAML data export
- **Requests**: HTTP library for GitHub API
- **HTML5**: Structure and semantic markup
- **CSS3**: Styling with responsive design including flexbox layouts
- **Vanilla JavaScript**: Interactive catalog (no external libraries)
- **GitHub API**: Source of repository and metadata information

## Supported Languages

The site currently recognizes these ISO 639-3 language codes:

- `eng` - English (default)
- `spa` - Spanish
- `fra` - French
- `por` - Portuguese
- `rus` - Russian
- `arb` - Arabic
- `hin` - Hindi
- `jpn` - Japanese
- `zht` - Chinese (Traditional)
- `ind` - Indonesian
- `nld` - Dutch
- `swh` - Swahili
- `nep` - Nepali
- `tpi` - Tok Pisin
- `apd` - Sudanese Arabic

## Resources Available

Examples of resources available through this interface:

- **Bible Dictionaries**: AquiferOpenBibleDictionary, VideoBibleDictionary
- **Study Notes**: AquiferOpenStudyNotes, BiblicaStudyNotes, BiblicaStudyNotesKeyTerms
- **Translation Resources**: UWTranslationNotes, UWTranslationWords, UWTranslationManual, UWTranslationQuestions
- **Translation Guides**: FIATranslationGuide
- **Images**: FIAImages, UBSImages
- **Maps**: FIAMaps
- **Key Terms**: FIAKeyTerms
- And many more...

## File Structure

```
bibleaquifer.github.io/
├── src/
│   ├── build_site.py       # Site generation script
│   ├── generate_sample.py  # Sample data generator
│   └── test_build.py       # Test script with sample data
├── index.html              # Landing page (generated)
├── catalog.html            # Unified catalog page (generated)
├── styles.css              # Shared CSS styles
├── pyproject.toml          # Poetry configuration
├── BUILD.md                # Build instructions
├── README.md               # This file
├── LICENSE                 # License information
└── .gitignore              # Git ignore rules
```

Note: `index.js`, `catalog.js`, and `app.js` are no longer used as the site is now statically generated.

## Contributing

Contributions are welcome! To contribute:

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

See the [LICENSE](LICENSE) file for details.

## Links

- [BibleAquifer Organization](https://github.com/BibleAquifer)
- [Documentation](https://github.com/BibleAquifer/docs)
- [ACAI Data](https://github.com/BibleAquifer/ACAI)
