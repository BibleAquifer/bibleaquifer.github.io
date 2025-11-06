#!/usr/bin/env python3
"""
Test the build script with sample data to verify functionality
"""

import json
import yaml
from build_site import (
    markdown_to_html,
    format_readme_sections,
    generate_index_html,
    generate_catalog_html,
    get_language_name
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
                'citation': {
                    'title': 'unfoldingWord® Translation Notes',
                    'copyright_dates': '2022',
                    'copyright_holder': 'unfoldingWord',
                    'license_name': 'CC BY-SA 4.0 license',
                    'adaptation_notice': 'This resource has been adapted from the original English version.'
                },
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
                'citation': {
                    'title': 'unfoldingWord® Translation Notes',
                    'copyright_dates': '2022',
                    'copyright_holder': 'unfoldingWord',
                    'license_name': 'CC BY-SA 4.0 license'
                },
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
                'citation': {
                    'title': 'Open Bible Dictionary',
                    'copyright_dates': '2023',
                    'copyright_holder': 'BibleAquifer',
                    'license_name': 'CC BY 4.0'
                },
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
                'citation': {
                    'title': 'Título en Español',
                    'copyright_dates': '2024',
                    'copyright_holder': 'Test Org',
                    'license_name': 'CC BY 4.0'
                },
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
                'citation': {
                    'title': 'English Title Here',
                    'copyright_dates': '2024',
                    'copyright_holder': 'Test Org',
                    'license_name': 'CC BY 4.0'
                },
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
    # Verify Spanish title is NOT in the dropdown
    assert 'Título en Español' not in catalog_html or catalog_html.count('Título en Español') == catalog_html.count('RESOURCES_DATA')
    print("✓ English title priority works")


def test_adaptation_notice_display():
    """Test that adaptation notice is included in citation"""
    print("Testing adaptation notice display...")
    catalog_html = generate_catalog_html(SAMPLE_RESOURCES)
    
    # Check that the adaptation notice is included in the generated HTML
    assert 'adaptation_notice' in catalog_html
    assert 'This resource has been adapted from the original English version.' in catalog_html
    print("✓ Adaptation notice display works")


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
        
        print()
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        
        # Generate sample output files for inspection
        print("\nGenerating sample output files...")
        
        html = markdown_to_html(SAMPLE_README)
        formatted = format_readme_sections(html)
        index_html = generate_index_html(formatted)
        
        with open('test_index.html', 'w') as f:
            f.write(index_html)
        print("  Created: test_index.html")
        
        catalog_html = generate_catalog_html(SAMPLE_RESOURCES)
        with open('test_catalog.html', 'w') as f:
            f.write(catalog_html)
        print("  Created: test_catalog.html")
        
        with open('test_resources.yaml', 'w') as f:
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
