#!/usr/bin/env python3
"""
Static site generator for BibleAquifer
Generates index.html and catalog.html from GitHub API data
"""

import json
import os
import re
import requests
import time
import yaml
from typing import Dict, List, Any, Optional
from jinja2 import Template

# Configuration
GITHUB_API = 'https://api.github.com'
ORG_NAME = 'BibleAquifer'
ORG_REPO_NAME = '.github'
README_PATH = 'profile/README.md'
EXCLUDED_REPOS = ['docs', 'ACAI', 'bibleaquifer.github.io', '.github']

# GitHub token from environment (optional)
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

def get_headers():
    """Get headers for GitHub API requests"""
    headers = {}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    return headers

# Language code to name mapping
LANGUAGE_MAP = {
    'eng': 'English',
    'spa': 'Spanish',
    'fra': 'French',
    'por': 'Portuguese',
    'rus': 'Russian',
    'arb': 'Arabic',
    'hin': 'Hindi',
    'jpn': 'Japanese',
    'zht': 'Chinese (Traditional)',
    'ind': 'Indonesian',
    'nld': 'Dutch',
    'swh': 'Swahili',
    'nep': 'Nepali',
    'tpi': 'Tok Pisin',
    'apd': 'Sudanese Arabic'
}


def get_language_name(code: str) -> str:
    """Convert 3-letter language code to full name"""
    return LANGUAGE_MAP.get(code, code.upper())


def fetch_readme() -> str:
    """Fetch README.md from organization profile"""
    url = f'https://raw.githubusercontent.com/{ORG_NAME}/{ORG_REPO_NAME}/main/{README_PATH}'
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.text


def markdown_to_html(markdown: str) -> str:
    """Convert markdown to HTML"""
    html = markdown
    
    # Remove the first H1 header and its following line (subtitle) if present
    html = re.sub(r'^# [^\n]+\n[^\n]+\n\n', '', html, flags=re.MULTILINE)
    
    # Convert headers (## Header)
    html = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    
    # Store links temporarily to avoid underscore conflicts
    links = []
    link_index = 0
    
    # Extract and replace links with placeholders
    def replace_link_with_em(match):
        nonlocal link_index
        text = match.group(1)
        url = match.group(2)
        placeholder = f'{{{{LINK{link_index}}}}}'
        links.append({
            'placeholder': placeholder,
            'html': f'<a href="{url}" target="_blank"><em>{text}</em></a>'
        })
        link_index += 1
        return placeholder
    
    def replace_link(match):
        nonlocal link_index
        text = match.group(1)
        url = match.group(2)
        placeholder = f'{{{{LINK{link_index}}}}}'
        links.append({
            'placeholder': placeholder,
            'html': f'<a href="{url}" target="_blank">{text}</a>'
        })
        link_index += 1
        return placeholder
    
    html = re.sub(r'\[_([^_]+)_\]\(([^)]+)\)', replace_link_with_em, html)
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, html)
    
    # Convert bold/italic _text_
    html = re.sub(r'_([^_]+)_', r'<em>\1</em>', html)
    
    # Restore links
    for link in links:
        html = html.replace(link['placeholder'], link['html'])
    
    # Convert code `code`
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Split into paragraphs and wrap in <p> tags
    lines = html.split('\n')
    result = ''
    in_paragraph = False
    
    for line in lines:
        line = line.strip()
        
        if not line:
            if in_paragraph:
                result += '</p>\n'
                in_paragraph = False
            continue
        
        # Headers don't need paragraph wrapping
        if line.startswith('<h2>'):
            if in_paragraph:
                result += '</p>\n'
                in_paragraph = False
            result += line + '\n'
        else:
            # Regular text - wrap in paragraph
            if not in_paragraph:
                result += '<p>'
                in_paragraph = True
            else:
                result += ' '
            result += line
    
    # Close any open paragraph
    if in_paragraph:
        result += '</p>\n'
    
    return result


def format_readme_sections(html: str) -> str:
    """Wrap each section in content-section div"""
    sections = html.split('<h2>')
    formatted_content = ''
    
    for i, section in enumerate(sections):
        section = section.strip()
        if section:
            if i == 0:
                # First section doesn't have an h2
                if section:
                    formatted_content += f'<section class="content-section">{section}</section>'
            else:
                # Add h2 back
                formatted_content += f'<section class="content-section"><h2>{section}</section>'
    
    return formatted_content


def fetch_repositories() -> List[Dict[str, Any]]:
    """Fetch all repositories from the organization"""
    response = requests.get(f'{GITHUB_API}/orgs/{ORG_NAME}/repos?per_page=100', headers=get_headers())
    
    if response.status_code == 403:
        print("WARNING: GitHub API rate limit hit. Waiting 60 seconds...")
        time.sleep(60)
        response = requests.get(f'{GITHUB_API}/orgs/{ORG_NAME}/repos?per_page=100', headers=get_headers())
    
    response.raise_for_status()
    repos = response.json()
    
    # Filter repos that are data repositories
    return [
        {
            'name': repo['name'],
            'description': repo.get('description', ''),
            'url': repo['html_url']
        }
        for repo in repos
        if repo['name'] not in EXCLUDED_REPOS and not repo.get('archived', False)
    ]


def fetch_languages(repo_name: str) -> List[str]:
    """Fetch available languages for a repository"""
    response = requests.get(f'{GITHUB_API}/repos/{ORG_NAME}/{repo_name}/contents', headers=get_headers())
    if response.status_code != 200:
        return []
    
    contents = response.json()
    
    # Filter for directories with 3-letter codes
    languages = [
        item['name']
        for item in contents
        if item['type'] == 'dir' and len(item['name']) == 3
    ]
    
    return languages


def fetch_metadata(repo_name: str, language: str) -> Optional[Dict[str, Any]]:
    """Fetch metadata.json for a specific language"""
    url = f'https://raw.githubusercontent.com/{ORG_NAME}/{repo_name}/main/{language}/metadata.json'
    response = requests.get(url, headers=get_headers())
    
    if response.status_code != 200:
        return None
    
    return response.json()


def check_directory_exists(repo_name: str, language: str, dir_name: str) -> bool:
    """Check if a directory exists in the repository"""
    url = f'{GITHUB_API}/repos/{ORG_NAME}/{repo_name}/contents/{language}/{dir_name}'
    response = requests.get(url, headers=get_headers())
    return response.status_code == 200


def build_resource_data() -> Dict[str, Any]:
    """Build complete resource data structure"""
    print("Fetching repositories...")
    repositories = fetch_repositories()
    
    resources = {}
    
    for repo in repositories:
        repo_name = repo['name']
        print(f"Processing {repo_name}...")
        
        languages = fetch_languages(repo_name)
        if not languages:
            print(f"  No languages found for {repo_name}")
            continue
        
        resource_data = {
            'name': repo_name,
            'description': repo['description'],
            'url': repo['url'],
            'languages': {}
        }
        
        # Fetch metadata for each language
        for lang in languages:
            print(f"  Fetching metadata for {lang}...")
            metadata = fetch_metadata(repo_name, lang)
            
            if metadata:
                resource_meta = metadata.get('resource_metadata', {})
                license_meta = resource_meta.get('license_info', {})
                
                # Get the resource title
                title = license_meta.get('title') or resource_meta.get('title') or repo_name
                
                # Check for pdf and docx directories
                has_pdf = check_directory_exists(repo_name, lang, 'pdf')
                has_docx = check_directory_exists(repo_name, lang, 'docx')
                
                resource_data['languages'][lang] = {
                    'code': lang,
                    'name': get_language_name(lang),
                    'title': title,
                    'version': resource_meta.get('version'),
                    'resource_type': resource_meta.get('resource_type') or resource_meta.get('aquifer_type'),
                    'content_type': resource_meta.get('content_type'),
                    'language': resource_meta.get('language'),
                    'citation': {
                        'title': license_meta.get('title'),
                        'copyright_dates': license_meta.get('copyright', {}).get('dates'),
                        'copyright_holder': license_meta.get('copyright', {}).get('holder', {}).get('name'),
                        'license_name': None
                    },
                    'has_pdf': has_pdf,
                    'has_docx': has_docx
                }
                
                # Get license name
                licenses = license_meta.get('licenses', [])
                if licenses and isinstance(licenses, list) and len(licenses) > 0:
                    first_license = licenses[0]
                    lang_code = resource_meta.get('language', 'eng')
                    if isinstance(first_license, dict) and lang_code in first_license:
                        resource_data['languages'][lang]['citation']['license_name'] = \
                            first_license[lang_code].get('name')
                
                # Set the resource title from the first language's metadata if not set
                if 'title' not in resource_data:
                    resource_data['title'] = title
        
        # Only add resources that have at least one language with metadata
        if resource_data['languages']:
            # Default title to formatted repo name if no metadata title found
            if 'title' not in resource_data:
                # Convert camelCase to Title Case
                resource_data['title'] = re.sub(r'([A-Z])', r' \1', repo_name).strip()
            
            resources[repo_name] = resource_data
    
    return resources


def generate_index_html(readme_html: str) -> str:
    """Generate index.html with embedded README content"""
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aquifer Bible Resources</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <div class="container header-content">
            <div>
                <h1>Aquifer Bible Resources</h1>
                <p class="subtitle">Access trustworthy and openly-licensed Bible content in multiple languages</p>
            </div>
            <nav class="header-nav">
                <a href="catalog.html" class="catalog-link">Unified Catalog</a>
                <a href="https://github.com/BibleAquifer" target="_blank" class="catalog-link">Github Org</a>
            </nav>
        </div>
    </header>

    <main class="container">
        <div id="dynamic-content">
{{ content }}
        </div>

        <section class="cta-section">
            <h2>Browse the Catalog</h2>
            <p>Explore available resources organized by type and language.</p>
            <a href="catalog.html" class="cta-button">View Unified Catalog</a>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 Mission Mutual. Open Biblical Resources.</p>
            <p><a href="https://github.com/BibleAquifer" target="_blank">GitHub Org</a> | <a href="https://github.com/BibleAquifer/docs" target="_blank">Documentation</a></p>
        </div>
    </footer>
</body>
</html>
"""
    
    t = Template(template)
    return t.render(content=readme_html)


def generate_catalog_html(resources: Dict[str, Any]) -> str:
    """Generate catalog.html with pre-populated resource data"""
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified Catalog - Aquifer Bible Resources</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <div class="container header-content">
            <div>
                <h1>Unified Catalog</h1>
                <p class="subtitle">Browse Aquifer Bible Resources by Type and Language</p>
            </div>
            <nav class="header-nav">
                <a href="index.html" class="catalog-link">Home</a>
                <a href="https://github.com/BibleAquifer" target="_blank" class="catalog-link">Github Org</a>
            </nav>
        </div>
    </header>

    <nav class="breadcrumb">
        <div class="container">
            <a href="index.html">Home</a> &gt; Catalog
        </div>
    </nav>

    <main class="container">
        <section id="catalog-controls">
            <div class="control-group">
                <label for="resource-select">Select Resource:</label>
                <select id="resource-select">
                    <option value="">Select a resource...</option>
{%- for resource_id, resource in resources.items() | sort(attribute='1.title') %}
                    <option value="{{ resource_id }}">{{ resource.title }}</option>
{%- endfor %}
                </select>
            </div>
            <div class="control-group">
                <label for="language-select">Select Language:</label>
                <select id="language-select">
                    <option value="">Select a resource first</option>
                </select>
            </div>
        </section>

        <section id="resource-info" class="hidden">
            <div id="resource-metadata"></div>
        </section>

        <section id="content-viewer" class="hidden">
            <h2>Resource Details</h2>
            <div id="content-display"></div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 Mission Mutual. Open Biblical Resources.</p>
            <p><a href="https://github.com/BibleAquifer" target="_blank">GitHub Org</a> | <a href="https://github.com/BibleAquifer/docs" target="_blank">Documentation</a></p>
        </div>
    </footer>

    <script>
// Resource data embedded from YAML
const RESOURCES_DATA = {{ resources_json }};
const ORG_NAME = '{{ org_name }}';

// DOM elements
const resourceSelect = document.getElementById('resource-select');
const languageSelect = document.getElementById('language-select');
const resourceMetadataDiv = document.getElementById('resource-metadata');
const contentDisplayDiv = document.getElementById('content-display');
const resourceInfoSection = document.getElementById('resource-info');
const contentViewerSection = document.getElementById('content-viewer');

// State
let selectedResource = null;
let selectedLanguage = null;

// Setup event listeners
resourceSelect.addEventListener('change', handleResourceChange);
languageSelect.addEventListener('change', handleLanguageChange);

// Handle resource selection
function handleResourceChange() {
    const resourceId = resourceSelect.value;
    
    if (!resourceId) {
        languageSelect.innerHTML = '<option value="">Select a resource first</option>';
        languageSelect.disabled = true;
        resourceMetadataDiv.innerHTML = '';
        contentDisplayDiv.innerHTML = '';
        resourceInfoSection.classList.add('hidden');
        contentViewerSection.classList.add('hidden');
        return;
    }
    
    selectedResource = RESOURCES_DATA[resourceId];
    
    // Populate language dropdown
    languageSelect.innerHTML = '<option value="">Select a language...</option>';
    
    const languages = Object.values(selectedResource.languages).sort((a, b) => 
        a.name.localeCompare(b.name)
    );
    
    const hasEng = languages.some(lang => lang.code === 'eng');
    
    languages.forEach(lang => {
        const option = document.createElement('option');
        option.value = lang.code;
        option.textContent = lang.name;
        if (lang.code === 'eng' && hasEng) {
            option.selected = true;
        }
        languageSelect.appendChild(option);
    });
    
    languageSelect.disabled = false;
    
    // Display resource info
    displayResourceInfo();
    
    // Auto-load English if available
    if (hasEng) {
        selectedLanguage = 'eng';
        displayLanguageMetadata();
    }
}

// Handle language selection
function handleLanguageChange() {
    selectedLanguage = languageSelect.value;
    
    if (!selectedLanguage) {
        contentDisplayDiv.innerHTML = '';
        contentViewerSection.classList.add('hidden');
        return;
    }
    
    displayLanguageMetadata();
}

// Display resource information
function displayResourceInfo() {
    if (!selectedResource) return;
    
    resourceMetadataDiv.innerHTML = `
        <h3>${selectedResource.title}</h3>
        <p>${selectedResource.description || 'No description available'}</p>
        <p><a href="${selectedResource.url}" target="_blank">View on GitHub</a></p>
    `;
    
    resourceInfoSection.classList.remove('hidden');
}

// Display language metadata
function displayLanguageMetadata() {
    if (!selectedResource || !selectedLanguage) return;
    
    const langData = selectedResource.languages[selectedLanguage];
    if (!langData) {
        contentDisplayDiv.innerHTML = '<p>No metadata available for this language.</p>';
        return;
    }
    
    let html = '';
    
    // Display citation if available
    if (langData.citation && langData.citation.title) {
        html += '<h3>Citation</h3>';
        html += '<p class="citation">';
        html += `<em>${langData.citation.title}</em>`;
        
        if (langData.citation.copyright_holder) {
            html += `. © ${langData.citation.copyright_dates || ''} ${langData.citation.copyright_holder}`;
        }
        
        if (langData.citation.license_name) {
            html += `. Licensed under ${langData.citation.license_name}`;
        }
        
        html += '.</p>';
        html += '<hr style="margin: 1.5rem 0;">';
    }
    
    // Display key metadata
    html += '<h3>Resource Information</h3>';
    html += '<div class="metadata-grid">';
    
    const metadataFields = [
        { label: 'Title', value: langData.title },
        { label: 'Language', value: langData.language },
        { label: 'Version', value: langData.version },
        { label: 'Type', value: langData.resource_type },
        { label: 'Content Type', value: langData.content_type }
    ];
    
    metadataFields.forEach(field => {
        if (field.value) {
            html += `
                <div class="metadata-label">${field.label}:</div>
                <div class="metadata-value">${field.value}</div>
            `;
        }
    });
    
    html += '</div>';
    
    // Add download links
    html += '<hr style="margin: 1.5rem 0;">';
    html += '<h3>Access Resource</h3>';
    html += '<p>Browse or download this resource:</p>';
    html += '<ul class="download-list">';
    html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/tree/main/${selectedLanguage}/json" target="_blank">Browse JSON files</a></li>`;
    html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/tree/main/${selectedLanguage}/md" target="_blank">Browse Markdown files</a></li>`;
    
    if (langData.has_pdf) {
        html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/tree/main/${selectedLanguage}/pdf" target="_blank">Browse PDF files</a></li>`;
    }
    
    if (langData.has_docx) {
        html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/tree/main/${selectedLanguage}/docx" target="_blank">Browse DOCX files</a></li>`;
    }
    
    html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/releases/latest" target="_blank">Download latest release</a></li>`;
    html += '</ul>';
    
    contentDisplayDiv.innerHTML = html;
    contentViewerSection.classList.remove('hidden');
}
    </script>
</body>
</html>
"""
    
    t = Template(template)
    return t.render(
        resources=resources,
        resources_json=json.dumps(resources, indent=2),
        org_name=ORG_NAME
    )


def main():
    """Main build process"""
    print("=" * 60)
    print("Building BibleAquifer Static Site")
    print("=" * 60)
    
    # Fetch and process README
    print("\n1. Fetching README from organization profile...")
    readme_md = fetch_readme()
    readme_html = markdown_to_html(readme_md)
    readme_formatted = format_readme_sections(readme_html)
    
    # Build resource data
    print("\n2. Building resource data...")
    resources = build_resource_data()
    
    print(f"\nFound {len(resources)} resources with metadata")
    
    # Save resource data to YAML for reference
    print("\n3. Saving resource data to YAML...")
    with open('resources_data.yaml', 'w') as f:
        yaml.dump(resources, f, default_flow_style=False, sort_keys=False)
    
    # Generate HTML files
    print("\n4. Generating index.html...")
    index_html = generate_index_html(readme_formatted)
    with open('index.html', 'w') as f:
        f.write(index_html)
    
    print("5. Generating catalog.html...")
    catalog_html = generate_catalog_html(resources)
    with open('catalog.html', 'w') as f:
        f.write(catalog_html)
    
    print("\n" + "=" * 60)
    print("Build complete!")
    print("=" * 60)
    print(f"Generated files:")
    print("  - index.html")
    print("  - catalog.html")
    print("  - resources_data.yaml")
    print()


if __name__ == '__main__':
    main()
