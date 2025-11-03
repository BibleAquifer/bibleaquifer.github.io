# Bible Aquifer - Static Site Frontend

This is the static site frontend for the Bible Aquifer organization on GitHub. It provides a user-friendly interface to browse and access biblical resources from the various BibleAquifer repositories.

## Live Site

The site is automatically deployed to GitHub Pages at: https://bibleaquifer.github.io

## Site Structure

The site consists of two pages:

### Landing Page (`index.html`)
An informational page that introduces Aquifer Bible Resources with content from the BibleAquifer organization profile. Includes:
- Overview of open source Bible resources for the global church
- Information about resource-level organization
- Available openly-licensed resources
- Documentation and schemas
- Call-to-action button to access the Unified Catalog

### Unified Catalog (`catalog.html`)
An interactive catalog for browsing resources by type and language. Features:
- **Resource Selection**: Dropdown listing all available BibleAquifer data repositories (displayed using unformatted repository names)
- **Language Selection**: Dropdown showing available languages for the selected resource
- **Default to English**: Automatically selects and loads English ("eng") language when available
- **Citation Display**: Shows proper citation from resource metadata including title, copyright, and license information
- **Resource Information**: Displays metadata including language, version, type, and content type
- **Download Links**: Direct access to browse JSON files, Markdown files, and download the latest release
- **Clean UI**: Empty sections remain hidden until populated with data

## Features

- **Two-Page Design**: Informational landing page and interactive catalog
- **Header Navigation**: Quick access to Unified Catalog, Home, and GitHub Organization
- **Fast Resource Loading**: Uses repository names directly for instant dropdown population
- **Dynamic Content**: Fetches data directly from GitHub repositories using the GitHub API
- **Responsive Design**: Works on desktop and mobile devices
- **No Dependencies**: Pure vanilla JavaScript, HTML5, and CSS3

## How It Works

The site dynamically fetches data from BibleAquifer repositories:

1. **Resource Discovery**: Loads all repositories from the BibleAquifer organization (excluding `docs`, `ACAI`, `.github`, and `bibleaquifer.github.io`)
2. **Language Detection**: For each resource, detects available languages by scanning for 3-letter ISO 639-3 language code directories (e.g., `eng`, `spa`, `fra`)
3. **Auto-Selection**: Automatically selects "eng" (English) language if available
4. **Metadata Loading**: Loads language-specific metadata from `{language}/metadata.json`
5. **Citation Extraction**: Pulls citation information from `resource_metadata.license_info` including title, copyright holder, and license
6. **Resource Access**: Provides links to browse JSON/MD folders and download latest release

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

To test the site locally:

1. Clone this repository:
   ```bash
   git clone https://github.com/BibleAquifer/bibleaquifer.github.io.git
   cd bibleaquifer.github.io
   ```

2. Start a local web server:
   ```bash
   python3 -m http.server 8080
   ```
   Or use any other static file server.

3. Open your browser to `http://localhost:8080`

**Note**: When running locally, you may encounter CORS (Cross-Origin Resource Sharing) restrictions from the GitHub API. The site will work properly when deployed to GitHub Pages at https://bibleaquifer.github.io

## Technologies Used

- **HTML5**: Structure and semantic markup
- **CSS3**: Styling with responsive design including flexbox layouts
- **Vanilla JavaScript**: Dynamic content loading and interaction (no external libraries)
- **GitHub API**: Fetches repository data and raw content files

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
├── index.html          # Landing page with informational content
├── catalog.html        # Unified catalog page
├── styles.css          # Shared CSS styles
├── catalog.js          # JavaScript for catalog functionality
├── README.md           # This file
├── LICENSE             # License information
└── .gitignore          # Git ignore rules
```

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
