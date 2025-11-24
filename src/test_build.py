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
    get_first_json_path
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
                'first_json_path': 'json/001.content.json',
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
                'first_json_path': 'json/001.content.json',
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
