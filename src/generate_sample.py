#!/usr/bin/env python3
"""
Generate static HTML files using sample data
This can be used when the GitHub API is unavailable
"""

import os
import sys

# Add current directory to path to import build_site
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_site import generate_index_html, generate_catalog_html, markdown_to_html, format_readme_sections, generate_nav_files

# Sample README (based on actual BibleAquifer profile)
SAMPLE_README = """# Aquifer Bible Resources
Access trustworthy and openly-licensed Bible content in multiple languages

## About Aquifer

Aquifer provides _high-quality_ and _trustworthy_ Bible resources to the global Church. We focus on making these resources available in a structured, machine-readable format that can be easily accessed and integrated into various applications.

## Resource Organization

Resources are organized by [resource type](https://github.com/BibleAquifer/docs) (dictionaries, study notes, translation guides, etc.) and language. Each resource follows a consistent structure for easy access.

## Available Resources

The Aquifer collection includes:
- Bible dictionaries and encyclopedias
- Study notes and commentaries
- Translation guides and helps
- Key terms and glossaries
- Images and maps
- And more...

## Documentation

For detailed information about resource schemas and data structures, see the [documentation repository](https://github.com/BibleAquifer/docs).

## Get Involved

All resources are openly licensed. Visit our [GitHub organization](https://github.com/BibleAquifer) to explore the resources and contribute."""

# Sample resources based on actual BibleAquifer repos
SAMPLE_RESOURCES = {
    'UWTranslationNotes': {
        'name': 'UWTranslationNotes',
        'title': 'Translation Notes (unfoldingWord)',
        'description': 'Translation notes for Bible translators',
        'url': 'https://github.com/BibleAquifer/UWTranslationNotes',
        'languages': {
            'eng': {
                'code': 'eng',
                'name': 'English',
                'title': 'unfoldingWord® Translation Notes',
                'version': '1.0.0',
                'resource_type': 'Translation Guide',
                'content_type': 'Html',
                'language': 'eng',
                'first_json_path': 'json/01.content.json',
                'json_files': [
                    {'path': 'json/01.content.json', 'label': 'GEN'},
                    {'path': 'json/02.content.json', 'label': 'EXO'},
                    {'path': 'json/03.content.json', 'label': 'LEV'}
                ],
                'citation': {
                    'title': 'unfoldingWord® Translation Notes',
                    'copyright_dates': '2022',
                    'copyright_holder': 'unfoldingWord',
                    'license_name': 'CC BY-SA 4.0 license'
                },
                'has_json': True,
                'has_md': True,
                'has_pdf': False,
                'has_docx': False
            },
            'spa': {
                'code': 'spa',
                'name': 'Spanish',
                'title': 'unfoldingWord® Translation Notes',
                'version': '1.0.0',
                'resource_type': 'Translation Guide',
                'content_type': 'Html',
                'language': 'spa',
                'first_json_path': 'json/01.content.json',
                'json_files': [
                    {'path': 'json/01.content.json', 'label': 'GEN'},
                    {'path': 'json/02.content.json', 'label': 'EXO'}
                ],
                'citation': {
                    'title': 'unfoldingWord® Translation Notes',
                    'copyright_dates': '2022',
                    'copyright_holder': 'unfoldingWord',
                    'license_name': 'CC BY-SA 4.0 license'
                },
                'has_json': True,
                'has_md': True,
                'has_pdf': False,
                'has_docx': False
            }
        }
    },
    'AquiferOpenBibleDictionary': {
        'name': 'AquiferOpenBibleDictionary',
        'title': 'Open Bible Dictionary',
        'description': 'Comprehensive Bible dictionary',
        'url': 'https://github.com/BibleAquifer/AquiferOpenBibleDictionary',
        'languages': {
            'eng': {
                'code': 'eng',
                'name': 'English',
                'title': 'Open Bible Dictionary',
                'version': '2.0.0',
                'resource_type': 'Dictionary',
                'content_type': 'Html',
                'language': 'eng',
                'first_json_path': 'json/001.content.json',
                'json_files': [
                    {'path': 'json/001.content.json', 'label': 'a'},
                    {'path': 'json/002.content.json', 'label': 'b'},
                    {'path': 'json/003.content.json', 'label': 'c'}
                ],
                'citation': {
                    'title': 'Open Bible Dictionary',
                    'copyright_dates': '2023',
                    'copyright_holder': 'BibleAquifer',
                    'license_name': 'CC BY 4.0'
                },
                'has_json': True,
                'has_md': True,
                'has_pdf': False,
                'has_docx': False
            }
        }
    },
    'UWTranslationWords': {
        'name': 'UWTranslationWords',
        'title': 'Translation Words (unfoldingWord)',
        'description': 'Key biblical terms with definitions',
        'url': 'https://github.com/BibleAquifer/UWTranslationWords',
        'languages': {
            'eng': {
                'code': 'eng',
                'name': 'English',
                'title': 'unfoldingWord® Translation Words',
                'version': '1.0.0',
                'resource_type': 'Key Terms',
                'content_type': 'Html',
                'language': 'eng',
                'first_json_path': 'json/001.content.json',
                'json_files': [
                    {'path': 'json/001.content.json', 'label': 'kt'}
                ],
                'citation': {
                    'title': 'unfoldingWord® Translation Words',
                    'copyright_dates': '2022',
                    'copyright_holder': 'unfoldingWord',
                    'license_name': 'CC BY-SA 4.0 license'
                },
                'has_json': True,
                'has_md': True,
                'has_pdf': False,
                'has_docx': False
            }
        }
    },
    'BiblicaStudyNotes': {
        'name': 'BiblicaStudyNotes',
        'title': 'Study Notes (Biblica)',
        'description': 'Study notes from Biblica',
        'url': 'https://github.com/BibleAquifer/BiblicaStudyNotes',
        'languages': {
            'eng': {
                'code': 'eng',
                'name': 'English',
                'title': 'Study Notes (Biblica)',
                'version': '1.0.0',
                'resource_type': 'Study Notes',
                'content_type': 'Html',
                'language': 'eng',
                'first_json_path': 'json/01.content.json',
                'json_files': [
                    {'path': 'json/01.content.json', 'label': 'GEN'},
                    {'path': 'json/02.content.json', 'label': 'EXO'}
                ],
                'citation': {
                    'title': 'Study Notes (Biblica)',
                    'copyright_dates': '2024',
                    'copyright_holder': 'Biblica',
                    'license_name': 'CC BY-SA 4.0'
                },
                'has_json': True,
                'has_md': True,
                'has_pdf': True,
                'has_docx': True
            }
        }
    },
    'BereanStandardBible': {
        'name': 'BereanStandardBible',
        'title': 'Berean Standard Bible',
        'description': 'A modern English Bible translation',
        'url': 'https://github.com/BibleAquifer/BereanStandardBible',
        'languages': {
            'eng': {
                'code': 'eng',
                'name': 'English',
                'title': 'Berean Standard Bible',
                'version': '1.1.0',
                'resource_type': 'Bible',
                'content_type': 'Bible',
                'language': 'eng',
                'first_json_path': 'json/01.content.json',
                'json_files': [
                    {
                        'path': 'json/01.content.json',
                        'label': 'Genesis',
                        'formats': {
                            'json': 'json/01.content.json',
                            'pdf': 'pdf/01.content.pdf',
                            'docx': 'docx/01.content.docx',
                            'usfm': 'usfm/01GENBSB.SFM',
                            'usx': 'usx/01GENBSB.usx',
                            'audio': 'audio/01GENBSB.timing.json',
                            'alignments': 'alignments/01.alignment.json'
                        }
                    },
                    {
                        'path': 'json/02.content.json',
                        'label': 'Exodus',
                        'formats': {
                            'json': 'json/02.content.json',
                            'pdf': 'pdf/02.content.pdf',
                            'docx': 'docx/02.content.docx',
                            'usfm': 'usfm/02EXOBSB.SFM',
                            'usx': 'usx/02EXOBSB.usx',
                            'audio': 'audio/02EXOBSB.timing.json',
                            'alignments': 'alignments/02.alignment.json'
                        }
                    },
                    {
                        'path': 'json/40.content.json',
                        'label': 'Matthew',
                        'formats': {
                            'json': 'json/40.content.json',
                            'pdf': 'pdf/40.content.pdf',
                            'docx': 'docx/40.content.docx',
                            'usfm': 'usfm/40MATBSB.SFM',
                            'usx': 'usx/40MATBSB.usx',
                            'audio': 'audio/40MATBSB.timing.json',
                            'alignments': 'alignments/40.alignment.json'
                        }
                    }
                ],
                'citation': {
                    'title': 'Berean Standard Bible',
                    'copyright_dates': None,
                    'copyright_holder': 'Berean Standard Bible',
                    'license_name': 'Public Domain CC0'
                },
                'has_json': True,
                'has_md': False,
                'has_pdf': True,
                'has_docx': True,
                'has_usfm': True,
                'has_usx': True,
                'has_audio': True,
                'has_alignments': True
            }
        }
    }
}


def main():
    """Generate HTML files with sample data"""
    print("=" * 60)
    print("Generating Static Site with Sample Data")
    print("=" * 60)
    
    print("\n1. Processing README...")
    readme_html = markdown_to_html(SAMPLE_README)
    readme_formatted = format_readme_sections(readme_html)
    
    print("2. Generating index.html...")
    index_html = generate_index_html(readme_formatted)
    output_dir = os.path.join(os.path.dirname(__file__), '..')
    with open(os.path.join(output_dir, 'index.html'), 'w') as f:
        f.write(index_html)
    print("   ✓ Created index.html")
    
    print("3. Generating catalog.html...")
    catalog_html = generate_catalog_html(SAMPLE_RESOURCES)
    with open(os.path.join(output_dir, 'catalog.html'), 'w') as f:
        f.write(catalog_html)
    print("   ✓ Created catalog.html")

    print("4. Generating nav files...")
    generate_nav_files(SAMPLE_RESOURCES, output_dir)

    print("\n" + "=" * 60)
    print("Generation complete!")
    print("=" * 60)
    print("Generated files:")
    print("  - index.html")
    print("  - catalog.html")
    print("  - nav/*.json")
    print("\nNote: These files use sample data.")
    print("To generate with real data, run: poetry run python src/build_site.py")
    print()


if __name__ == '__main__':
    main()
