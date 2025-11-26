#!/usr/bin/env python3
"""
Test the build script with sample data to verify functionality
"""

import json
import os
import yaml
from build_site import (
    markdown_to_html,
    format_readme_sections,
    generate_index_html,
    generate_catalog_html,
    get_language_name,
    get_first_json_path,
    get_json_files_with_labels,
    generate_nav_files,
    get_catalog_resources,
    get_bible_book_name,
    is_roman_script_language,
    transform_label
)

# Sample README content
SAMPLE_README = """# Aquifer Bible Resources
Access trustworthy and openly-licensed Bible content

## About the Project

This is an initiative to provide _high-quality_ Bible resources to the [global church](https://example.com).

## Available Resources

We have multiple translation guides and study resources available.

## Get Involved

Check out our `documentation` for more information."""

# Sample resource data
# Note: JSON file path formats vary by resource type to match actual repository structures:
# - Study notes/Bible resources use 2-digit format: json/01.content.json
# - Dictionary resources use 3-digit format: json/001.content.json
# Labels are transformed based on resource_metadata/order:
# - canonical: Bible book codes -> full names (GEN -> Genesis)
# - alphabetical: lower-case -> UPPER-CASE for Roman script languages
# - monograph: path stripped of 'json/' prefix
SAMPLE_RESOURCES = {
    'UWTranslationNotes': {
        'name': 'UWTranslationNotes',
        'title': 'Translation Notes (unfoldingWord)',
        'description': 'Translation helps for Bible translators',
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
                    {'path': 'json/01.content.json', 'label': 'Genesis'},
                    {'path': 'json/02.content.json', 'label': 'Exodus'},
                    {'path': 'json/03.content.json', 'label': 'Leviticus'}
                ],
                'citation': {
                    'title': 'unfoldingWord® Translation Notes',
                    'copyright_dates': '2022',
                    'copyright_holder': 'unfoldingWord',
                    'license_name': 'CC BY-SA 4.0 license',
                    'adaptation_notice': 'This resource has been adapted from the original English version.'
                },
                'has_json': True,
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
                    {'path': 'json/01.content.json', 'label': 'Genesis'},
                    {'path': 'json/02.content.json', 'label': 'Exodus'}
                ],
                'citation': {
                    'title': 'unfoldingWord® Translation Notes',
                    'copyright_dates': '2022',
                    'copyright_holder': 'unfoldingWord',
                    'license_name': 'CC BY-SA 4.0 license'
                },
                'has_json': True,
                'has_pdf': True,
                'has_docx': True
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
                    {'path': 'json/001.content.json', 'label': 'A'},
                    {'path': 'json/002.content.json', 'label': 'B'},
                    {'path': 'json/003.content.json', 'label': 'C'}
                ],
                'citation': {
                    'title': 'Open Bible Dictionary',
                    'copyright_dates': '2023',
                    'copyright_holder': 'BibleAquifer',
                    'license_name': 'CC BY 4.0'
                },
                'has_json': True,
                'has_pdf': False,
                'has_docx': False
            }
        }
    },
    'TestResourceSpanishFirst': {
        'name': 'TestResourceSpanishFirst',
        'title': 'English Title Here',
        'description': 'Test resource with Spanish before English',
        'url': 'https://github.com/BibleAquifer/TestResourceSpanishFirst',
        'languages': {
            'spa': {
                'code': 'spa',
                'name': 'Spanish',
                'title': 'Título en Español',
                'version': '1.0.0',
                'resource_type': 'Test',
                'content_type': 'Html',
                'language': 'spa',
                'first_json_path': None,
                'json_files': [],
                'citation': {
                    'title': 'Título en Español',
                    'copyright_dates': '2024',
                    'copyright_holder': 'Test Org',
                    'license_name': 'CC BY 4.0'
                },
                'has_json': False,
                'has_pdf': False,
                'has_docx': False
            },
            'eng': {
                'code': 'eng',
                'name': 'English',
                'title': 'English Title Here',
                'version': '1.0.0',
                'resource_type': 'Test',
                'content_type': 'Html',
                'language': 'eng',
                'first_json_path': None,
                'json_files': [],
                'citation': {
                    'title': 'English Title Here',
                    'copyright_dates': '2024',
                    'copyright_holder': 'Test Org',
                    'license_name': 'CC BY 4.0'
                },
                'has_json': False,
                'has_pdf': False,
                'has_docx': False
            }
        }
    },
    'IndianRevisedVersion': {
        'name': 'IndianRevisedVersion',
        'title': 'Indian Revised Version',
        'description': 'Hindi Bible translation',
        'url': 'https://github.com/BibleAquifer/IndianRevisedVersion',
        'languages': {
            'hin': {
                'code': 'hin',
                'name': 'Hindi',
                'title': 'Indian Revised Version',
                'version': '1.0.2',
                'resource_type': 'Bible',
                'content_type': 'Bible',
                'language': 'hin',
                'first_json_path': 'json/01.content.json',
                'json_files': [
                    {'path': 'json/01.content.json', 'label': 'Genesis'}
                ],
                'citation': {
                    'title': 'Hindi Indian Revised Version',
                    'copyright_dates': '2019',
                    'copyright_holder': 'Bridge Connectivity Solutions',
                    'license_name': 'CC BY-SA 4.0 license'
                },
                'has_json': True,
                'has_pdf': True,
                'has_docx': True
            }
        }
    }
}


def test_markdown_conversion():
    """Test markdown to HTML conversion"""
    print("Testing markdown conversion...")
    html = markdown_to_html(SAMPLE_README)
    assert '<h2>' in html
    assert '<em>' in html
    assert '<a href=' in html
    assert '<code>' in html
    print("✓ Markdown conversion works")


def test_readme_sections():
    """Test README section formatting"""
    print("Testing README section formatting...")
    html = markdown_to_html(SAMPLE_README)
    formatted = format_readme_sections(html)
    assert 'content-section' in formatted
    print("✓ README section formatting works")


def test_index_generation():
    """Test index.html generation"""
    print("Testing index.html generation...")
    html = markdown_to_html(SAMPLE_README)
    formatted = format_readme_sections(html)
    index_html = generate_index_html(formatted)
    
    assert '<!DOCTYPE html>' in index_html
    assert 'Aquifer Bible Resources' in index_html
    assert 'content-section' in index_html
    assert 'catalog.html' in index_html
    print("✓ index.html generation works")


def test_catalog_generation():
    """Test catalog.html generation"""
    print("Testing catalog.html generation...")
    catalog_html = generate_catalog_html(SAMPLE_RESOURCES)
    
    assert '<!DOCTYPE html>' in catalog_html
    assert 'Unified Catalog' in catalog_html
    assert 'Translation Notes (unfoldingWord)' in catalog_html
    assert 'Open Bible Dictionary' in catalog_html
    assert 'RESOURCES_DATA' in catalog_html
    assert 'Spanish' in catalog_html
    print("✓ catalog.html generation works")


def test_yaml_compatibility():
    """Test that resource data can be saved as YAML"""
    print("Testing YAML compatibility...")
    yaml_str = yaml.dump(SAMPLE_RESOURCES, default_flow_style=False, sort_keys=False)
    assert 'UWTranslationNotes' in yaml_str
    assert 'English' in yaml_str
    print("✓ YAML export works")


def test_language_name():
    """Test language name conversion"""
    print("Testing language name conversion...")
    assert get_language_name('eng') == 'English'
    assert get_language_name('spa') == 'Spanish'
    assert get_language_name('xxx') == 'XXX'
    print("✓ Language name conversion works")


def test_english_title_priority():
    """Test that English title is used in dropdown even when not first language"""
    print("Testing English title priority...")
    catalog_html = generate_catalog_html(SAMPLE_RESOURCES)
    
    # The dropdown should show "English Title Here" not "Título en Español"
    assert 'English Title Here' in catalog_html
    
    # Extract the dropdown section and verify Spanish title is not there
    dropdown_start = catalog_html.find('<select id="resource-select">')
    dropdown_end = catalog_html.find('</select>', dropdown_start)
    dropdown_section = catalog_html[dropdown_start:dropdown_end]
    
    # Verify Spanish title is NOT in the dropdown options
    assert 'Título en Español' not in dropdown_section
    print("✓ English title priority works")


def test_adaptation_notice_display():
    """Test that adaptation notice is included in citation"""
    print("Testing adaptation notice display...")
    catalog_html = generate_catalog_html(SAMPLE_RESOURCES)
    
    # Check that the adaptation notice is included in the generated HTML
    assert 'adaptation_notice' in catalog_html
    assert 'This resource has been adapted from the original English version.' in catalog_html
    print("✓ Adaptation notice display works")


def test_get_first_json_path():
    """Test extraction of first JSON file path from metadata"""
    print("Testing get_first_json_path...")
    
    # Test with valid metadata containing JSON ingredient
    metadata_with_json = {
        'scripture_burrito': {
            'ingredients': {
                'json/001.content.json': {
                    'mimeType': 'text/json',
                    'size': 1904110
                },
                'json/002.content.json': {
                    'mimeType': 'text/json',
                    'size': 500000
                }
            }
        }
    }
    result = get_first_json_path(metadata_with_json)
    assert result == 'json/001.content.json', f"Expected 'json/001.content.json', got '{result}'"
    
    # Test with metadata without JSON ingredient
    metadata_without_json = {
        'scripture_burrito': {
            'ingredients': {
                'usfm/01-GEN.usfm': {
                    'mimeType': 'text/x-usfm',
                    'size': 100000
                }
            }
        }
    }
    result = get_first_json_path(metadata_without_json)
    assert result is None, f"Expected None, got '{result}'"
    
    # Test with empty metadata
    result = get_first_json_path({})
    assert result is None
    
    # Test with None
    result = get_first_json_path(None)
    assert result is None
    
    print("✓ get_first_json_path works")


def test_preview_tab_in_catalog():
    """Test that preview tab is generated in catalog HTML"""
    print("Testing preview tab in catalog...")
    catalog_html = generate_catalog_html(SAMPLE_RESOURCES)
    
    # Check for tab structure
    assert 'class="tabs"' in catalog_html
    assert 'data-tab="details"' in catalog_html
    assert 'data-tab="preview"' in catalog_html
    assert 'Resource Details' in catalog_html
    assert 'Resource Preview' in catalog_html
    
    # Check for preview-related elements
    assert 'id="tab-details"' in catalog_html
    assert 'id="tab-preview"' in catalog_html
    assert 'id="preview-display"' in catalog_html
    
    # Check for preview loading JavaScript
    assert 'loadPreview' in catalog_html
    assert 'first_json_path' in catalog_html
    
    print("✓ Preview tab in catalog works")


def test_preview_navigation_in_catalog():
    """Test that preview navigation controls are generated in catalog HTML"""
    print("Testing preview navigation in catalog...")
    catalog_html = generate_catalog_html(SAMPLE_RESOURCES)
    
    # Check for navigation HTML elements
    assert 'class="preview-navigation"' in catalog_html
    assert 'id="prev-article-btn"' in catalog_html
    assert 'id="next-article-btn"' in catalog_html
    assert 'id="article-position"' in catalog_html
    assert 'Previous' in catalog_html
    assert 'Next' in catalog_html
    
    # Check for navigation JavaScript state variables
    assert 'currentArticleIndex' in catalog_html
    assert 'currentArticles' in catalog_html
    
    # Check for navigation JavaScript functions
    assert 'displayArticle' in catalog_html
    assert 'updateNavigationState' in catalog_html
    assert 'resetArticleState' in catalog_html
    assert 'hideNavigation' in catalog_html
    
    # Check for button event listeners
    assert 'prevArticleBtn.addEventListener' in catalog_html
    assert 'nextArticleBtn.addEventListener' in catalog_html
    
    print("✓ Preview navigation in catalog works")


def test_rtl_language_support():
    """Test that RTL language support is included in catalog HTML"""
    print("Testing RTL language support...")
    catalog_html = generate_catalog_html(SAMPLE_RESOURCES)
    
    # Check for RTL language codes array
    assert 'RTL_LANGUAGES' in catalog_html
    assert "'arb'" in catalog_html  # Arabic
    assert "'apd'" in catalog_html  # Sudanese Arabic
    assert "'heb'" in catalog_html  # Hebrew
    
    # Check for isRtlLanguage helper function
    assert 'isRtlLanguage' in catalog_html
    assert 'RTL_LANGUAGES.includes(langCode)' in catalog_html
    
    # Check that displayArticle uses RTL direction
    assert 'dir="rtl"' in catalog_html
    assert 'isRtlLanguage(selectedLanguage)' in catalog_html
    
    print("✓ RTL language support works")


def test_default_language_selection():
    """Test that default language selection falls back to first alphabetically sorted language when English is not available"""
    print("Testing default language selection...")
    catalog_html = generate_catalog_html(SAMPLE_RESOURCES)
    
    # Check that the default language logic is present
    assert "const defaultLang = hasEng ? 'eng' : (languages.length > 0 ? languages[0].code : null)" in catalog_html
    
    # Check that the code uses defaultLang for auto-selection
    assert 'if (lang.code === defaultLang)' in catalog_html
    
    # Check that the code auto-loads the default language
    assert 'if (defaultLang)' in catalog_html
    assert 'selectedLanguage = defaultLang' in catalog_html
    
    # Ensure the IndianRevisedVersion resource (Hindi only) is in the sample resources
    assert 'IndianRevisedVersion' in SAMPLE_RESOURCES
    assert 'hin' in SAMPLE_RESOURCES['IndianRevisedVersion']['languages']
    assert 'eng' not in SAMPLE_RESOURCES['IndianRevisedVersion']['languages']
    
    print("✓ Default language selection works")


def test_get_json_files_with_labels():
    """Test extraction of all JSON files with labels from metadata"""
    print("Testing get_json_files_with_labels...")
    
    # Test with valid metadata containing multiple JSON ingredients with scope
    metadata_with_json = {
        'scripture_burrito': {
            'ingredients': {
                'json/001.content.json': {
                    'mimeType': 'text/json',
                    'size': 1904110,
                    'scope': {
                        'a': ['Aaron', 'Abraham']
                    }
                },
                'json/002.content.json': {
                    'mimeType': 'text/json',
                    'size': 500000,
                    'scope': {
                        'b': ['Babel', 'Babylon']
                    }
                },
                'usfm/01-GEN.usfm': {
                    'mimeType': 'text/x-usfm',
                    'size': 100000
                },
                # Audio JSON files should be ignored
                'audio/timing/01.json': {
                    'mimeType': 'text/json',
                    'size': 5000
                }
            }
        }
    }
    result = get_json_files_with_labels(metadata_with_json)
    assert len(result) == 2, f"Expected 2 JSON files, got {len(result)}"
    assert result[0]['path'] == 'json/001.content.json'
    assert result[0]['label'] == 'a'
    assert result[1]['path'] == 'json/002.content.json'
    assert result[1]['label'] == 'b'
    
    # Test with metadata without scope (should use path as label)
    metadata_no_scope = {
        'scripture_burrito': {
            'ingredients': {
                'json/99.content.json': {
                    'mimeType': 'text/json',
                    'size': 100
                }
            }
        }
    }
    result = get_json_files_with_labels(metadata_no_scope)
    assert len(result) == 1
    assert result[0]['label'] == 'json/99.content.json'
    
    # Test that non-matching JSON files are ignored
    metadata_non_matching = {
        'scripture_burrito': {
            'ingredients': {
                'audio/timing/01.json': {
                    'mimeType': 'text/json',
                    'size': 100
                },
                'json/metadata.json': {
                    'mimeType': 'text/json',
                    'size': 200
                }
            }
        }
    }
    result = get_json_files_with_labels(metadata_non_matching)
    assert len(result) == 0, f"Expected 0 JSON files (non-matching patterns), got {len(result)}"
    
    # Test with empty metadata
    result = get_json_files_with_labels({})
    assert result == []
    
    # Test with None
    result = get_json_files_with_labels(None)
    assert result == []
    
    print("✓ get_json_files_with_labels works")


def test_file_selector_in_catalog():
    """Test that file selector dropdown is generated in catalog HTML"""
    print("Testing file selector in catalog...")
    catalog_html = generate_catalog_html(SAMPLE_RESOURCES)
    
    # Check for file selector HTML elements
    assert 'id="file-select"' in catalog_html
    assert 'id="file-selector-group"' in catalog_html
    assert 'Select File:' in catalog_html
    
    # Check for file selector JavaScript
    assert 'fileSelect' in catalog_html
    assert 'fileSelectorGroup' in catalog_html
    assert 'handleFileChange' in catalog_html
    assert 'populateFileSelector' in catalog_html
    assert 'resetFileSelector' in catalog_html
    
    # Check that loadNavData function exists for dynamic loading
    assert 'loadNavData' in catalog_html
    assert 'navDataCache' in catalog_html
    
    # Check that selectedJsonPath state variable exists
    assert 'selectedJsonPath' in catalog_html
    
    print("✓ File selector in catalog works")


def test_file_selector_auto_switch_to_preview():
    """Test that file selector auto-switches to preview tab"""
    print("Testing file selector auto-switch to preview...")
    catalog_html = generate_catalog_html(SAMPLE_RESOURCES)
    
    # Check that handleFileChange calls switchToTab('preview')
    assert "switchToTab('preview')" in catalog_html
    
    print("✓ File selector auto-switch to preview works")


def test_nav_files_generation():
    """Test that nav files are generated correctly"""
    print("Testing nav file generation...")
    import tempfile
    import shutil
    
    # Create a temporary directory for output
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Generate nav files
        generate_nav_files(SAMPLE_RESOURCES, temp_dir)
        
        # Check that nav directory was created
        nav_dir = os.path.join(temp_dir, 'nav')
        assert os.path.exists(nav_dir), "nav directory should be created"
        
        # Check that nav files were created for resources with json_files
        expected_file = os.path.join(nav_dir, 'UWTranslationNotes_eng.json')
        assert os.path.exists(expected_file), f"Expected nav file {expected_file} to exist"
        
        # Verify content of the nav file
        with open(expected_file, 'r') as f:
            data = json.load(f)
        assert isinstance(data, list), "Nav file should contain a list"
        assert len(data) == 3, "Should have 3 JSON files"
        # Labels should be full Bible book names for canonical order resources
        assert data[0]['label'] == 'Genesis', "First file should have label Genesis"
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)
    
    print("✓ Nav file generation works")


def test_catalog_resources_without_json_files():
    """Test that get_catalog_resources removes json_files from resources"""
    print("Testing catalog resources without json_files...")
    
    catalog_resources = get_catalog_resources(SAMPLE_RESOURCES)
    
    # Check that json_files was removed from all languages
    for resource_name, resource_data in catalog_resources.items():
        for lang_code, lang_data in resource_data.get('languages', {}).items():
            assert 'json_files' not in lang_data, f"json_files should be removed from {resource_name}/{lang_code}"
    
    # Check that first_json_path is still present
    uw_eng = catalog_resources['UWTranslationNotes']['languages']['eng']
    assert 'first_json_path' in uw_eng, "first_json_path should still be present"
    
    print("✓ Catalog resources without json_files works")


def test_get_bible_book_name():
    """Test Bible book code to name conversion"""
    print("Testing get_bible_book_name...")
    
    # Test Old Testament books
    assert get_bible_book_name('GEN') == 'Genesis'
    assert get_bible_book_name('EXO') == 'Exodus'
    assert get_bible_book_name('LEV') == 'Leviticus'
    assert get_bible_book_name('PSA') == 'Psalms'
    assert get_bible_book_name('MAL') == 'Malachi'
    
    # Test numbered books
    assert get_bible_book_name('1SA') == '1 Samuel'
    assert get_bible_book_name('2SA') == '2 Samuel'
    assert get_bible_book_name('1KI') == '1 Kings'
    assert get_bible_book_name('2KI') == '2 Kings'
    assert get_bible_book_name('1CH') == '1 Chronicles'
    assert get_bible_book_name('2CH') == '2 Chronicles'
    
    # Test New Testament books
    assert get_bible_book_name('MAT') == 'Matthew'
    assert get_bible_book_name('MRK') == 'Mark'
    assert get_bible_book_name('JHN') == 'John'
    assert get_bible_book_name('ACT') == 'Acts'
    assert get_bible_book_name('REV') == 'Revelation'
    
    # Test numbered NT books
    assert get_bible_book_name('1CO') == '1 Corinthians'
    assert get_bible_book_name('2CO') == '2 Corinthians'
    assert get_bible_book_name('1TH') == '1 Thessalonians'
    assert get_bible_book_name('1PE') == '1 Peter'
    assert get_bible_book_name('1JN') == '1 John'
    assert get_bible_book_name('2JN') == '2 John'
    assert get_bible_book_name('3JN') == '3 John'
    
    # Test case insensitivity
    assert get_bible_book_name('gen') == 'Genesis'
    assert get_bible_book_name('Gen') == 'Genesis'
    
    # Test unknown codes return as-is
    assert get_bible_book_name('XXX') == 'XXX'
    assert get_bible_book_name('unknown') == 'unknown'
    
    print("✓ get_bible_book_name works")


def test_is_roman_script_language():
    """Test Roman script language detection"""
    print("Testing is_roman_script_language...")
    
    # Test Roman script languages
    assert is_roman_script_language('eng') == True
    assert is_roman_script_language('fra') == True
    assert is_roman_script_language('por') == True
    assert is_roman_script_language('swh') == True
    assert is_roman_script_language('ind') == True
    assert is_roman_script_language('nld') == True
    
    # Test non-Roman script languages
    assert is_roman_script_language('arb') == False
    assert is_roman_script_language('hin') == False
    assert is_roman_script_language('rus') == False
    assert is_roman_script_language('zht') == False
    assert is_roman_script_language('apd') == False
    
    print("✓ is_roman_script_language works")


def test_transform_label():
    """Test label transformation based on order type"""
    print("Testing transform_label...")
    
    # Test canonical order - Bible book codes to full names
    assert transform_label('GEN', 'canonical', 'eng') == 'Genesis'
    assert transform_label('EXO', 'canonical', 'eng') == 'Exodus'
    assert transform_label('1SA', 'canonical', 'eng') == '1 Samuel'
    assert transform_label('REV', 'canonical', 'eng') == 'Revelation'
    
    # Test alphabetical order - upper-case for Roman script languages
    assert transform_label('a', 'alphabetical', 'eng') == 'A'
    assert transform_label('b', 'alphabetical', 'fra') == 'B'
    assert transform_label('z', 'alphabetical', 'por') == 'Z'
    assert transform_label('a', 'alphabetical', 'swh') == 'A'
    
    # Test alphabetical order - no change for non-Roman script languages
    assert transform_label('a', 'alphabetical', 'arb') == 'a'
    assert transform_label('ב', 'alphabetical', 'heb') == 'ב'
    assert transform_label('а', 'alphabetical', 'rus') == 'а'
    
    # Test monograph order - strip json/ prefix
    assert transform_label('json/001.content.json', 'monograph', 'eng') == '001.content.json'
    assert transform_label('json/050.content.json', 'monograph', 'eng') == '050.content.json'
    assert transform_label('filename.json', 'monograph', 'eng') == 'filename.json'
    
    # Test unknown order - return as-is
    assert transform_label('GEN', 'unknown', 'eng') == 'GEN'
    assert transform_label('a', '', 'eng') == 'a'
    
    print("✓ transform_label works")


def test_get_json_files_with_labels_canonical():
    """Test get_json_files_with_labels with canonical order"""
    print("Testing get_json_files_with_labels with canonical order...")
    
    metadata_canonical = {
        'resource_metadata': {
            'order': 'canonical'
        },
        'scripture_burrito': {
            'ingredients': {
                'json/01.content.json': {
                    'mimeType': 'text/json',
                    'size': 1000,
                    'scope': {'GEN': []}
                },
                'json/02.content.json': {
                    'mimeType': 'text/json',
                    'size': 2000,
                    'scope': {'EXO': []}
                },
                'json/09.content.json': {
                    'mimeType': 'text/json',
                    'size': 3000,
                    'scope': {'1SA': []}
                }
            }
        }
    }
    
    result = get_json_files_with_labels(metadata_canonical, lang_code='eng')
    assert len(result) == 3
    assert result[0]['label'] == 'Genesis'
    assert result[1]['label'] == 'Exodus'
    assert result[2]['label'] == '1 Samuel'
    
    print("✓ get_json_files_with_labels with canonical order works")


def test_get_json_files_with_labels_alphabetical():
    """Test get_json_files_with_labels with alphabetical order"""
    print("Testing get_json_files_with_labels with alphabetical order...")
    
    metadata_alphabetical = {
        'resource_metadata': {
            'order': 'alphabetical'
        },
        'scripture_burrito': {
            'ingredients': {
                'json/001.content.json': {
                    'mimeType': 'text/json',
                    'size': 1000,
                    'scope': {'a': ['Aaron', 'Abraham']}
                },
                'json/002.content.json': {
                    'mimeType': 'text/json',
                    'size': 2000,
                    'scope': {'b': ['Babel', 'Babylon']}
                }
            }
        }
    }
    
    # Test with Roman script language - should upper-case
    result = get_json_files_with_labels(metadata_alphabetical, lang_code='eng')
    assert len(result) == 2
    assert result[0]['label'] == 'A'
    assert result[1]['label'] == 'B'
    
    # Test with non-Roman script language - should not upper-case
    result_arb = get_json_files_with_labels(metadata_alphabetical, lang_code='arb')
    assert result_arb[0]['label'] == 'a'
    assert result_arb[1]['label'] == 'b'
    
    print("✓ get_json_files_with_labels with alphabetical order works")


def test_get_json_files_with_labels_monograph():
    """Test get_json_files_with_labels with monograph order"""
    print("Testing get_json_files_with_labels with monograph order...")
    
    metadata_monograph = {
        'resource_metadata': {
            'order': 'monograph'
        },
        'scripture_burrito': {
            'ingredients': {
                'json/000001.content.json': {
                    'mimeType': 'text/json',
                    'size': 1000,
                    'scope': {}
                },
                'json/000002.content.json': {
                    'mimeType': 'text/json',
                    'size': 2000,
                    'scope': {}
                }
            }
        }
    }
    
    result = get_json_files_with_labels(metadata_monograph, lang_code='eng')
    assert len(result) == 2
    # Monograph with empty scope falls back to path, then transforms
    # Since scope is empty, label becomes the path, then transform_label strips json/
    assert result[0]['label'] == '000001.content.json'
    assert result[1]['label'] == '000002.content.json'
    
    print("✓ get_json_files_with_labels with monograph order works")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Running Build Script Tests")
    print("=" * 60)
    print()
    
    try:
        test_markdown_conversion()
        test_readme_sections()
        test_index_generation()
        test_catalog_generation()
        test_yaml_compatibility()
        test_language_name()
        test_english_title_priority()
        test_adaptation_notice_display()
        test_get_first_json_path()
        test_preview_tab_in_catalog()
        test_preview_navigation_in_catalog()
        test_rtl_language_support()
        test_default_language_selection()
        test_get_json_files_with_labels()
        test_file_selector_in_catalog()
        test_file_selector_auto_switch_to_preview()
        test_nav_files_generation()
        test_catalog_resources_without_json_files()
        test_get_bible_book_name()
        test_is_roman_script_language()
        test_transform_label()
        test_get_json_files_with_labels_canonical()
        test_get_json_files_with_labels_alphabetical()
        test_get_json_files_with_labels_monograph()
        
        print()
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        
        # Generate sample output files for inspection
        print("\nGenerating sample output files...")
        
        html = markdown_to_html(SAMPLE_README)
        formatted = format_readme_sections(html)
        index_html = generate_index_html(formatted)
        
        output_dir = os.path.dirname(__file__)
        with open(os.path.join(output_dir, 'test_index.html'), 'w') as f:
            f.write(index_html)
        print("  Created: test_index.html")
        
        catalog_html = generate_catalog_html(SAMPLE_RESOURCES)
        with open(os.path.join(output_dir, 'test_catalog.html'), 'w') as f:
            f.write(catalog_html)
        print("  Created: test_catalog.html")
        
        with open(os.path.join(output_dir, 'test_resources.yaml'), 'w') as f:
            yaml.dump(SAMPLE_RESOURCES, f, default_flow_style=False, sort_keys=False)
        print("  Created: test_resources.yaml")
        
        print("\nYou can inspect these test files to verify the output format.")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
