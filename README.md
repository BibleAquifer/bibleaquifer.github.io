# Bible Aquifer - Static Site Frontend

This is the static site frontend for the Bible Aquifer organization on GitHub. It provides a user-friendly interface to browse and access biblical resources from the various BibleAquifer repositories.

## Features

- **Resource Browser**: Browse all available biblical resources in the BibleAquifer organization
- **Language Selection**: Access content in multiple languages (15+ languages supported)
- **Content Viewer**: View articles and resources in JSON and Markdown formats
- **Dynamic Loading**: Fetches data directly from GitHub repositories using the GitHub API
- **Responsive Design**: Works on desktop and mobile devices

## Live Site

The site is automatically deployed to GitHub Pages at: https://bibleaquifer.github.io

## How It Works

The site dynamically fetches data from BibleAquifer repositories:

1. **Resource Discovery**: Loads all repositories from the BibleAquifer organization (excluding `docs`, `ACAI`, and `bibleaquifer.github.io`)
2. **Language Detection**: For each resource, detects available languages by scanning for 3-letter language code directories (e.g., `eng`, `spa`, `fra`)
3. **Metadata Loading**: Loads language-specific metadata from `{language}/metadata.json`
4. **Content Browsing**: Lists all articles from the `{language}/json/` directory
5. **Article Viewing**: Displays individual article content when selected

## Repository Structure Expected

The site expects BibleAquifer data repositories to follow this structure:

```
RepositoryName/
├── README.md
├── eng/                    # 3-letter language code
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
- **CSS3**: Styling with responsive design
- **Vanilla JavaScript**: Dynamic content loading and interaction
- **GitHub API**: Fetches repository data and content

## Supported Languages

The site currently recognizes these language codes:

- `eng` - English
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
- **Study Notes**: AquiferOpenStudyNotes, BiblicaStudyNotes
- **Translation Resources**: UWTranslationNotes, UWTranslationWords, UWTranslationManual
- **Images**: FIAImages, UBSImages
- **Maps**: FIAMaps
- And many more...

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
