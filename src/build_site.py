#!/usr/bin/env python3
"""
Static site generator for BibleAquifer
Generates index.html and catalog.html from GitHub API data
"""

import json
import os
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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
# get set up to do retries on requests
# Define retry strategy
retry_strategy = Retry(
    total=7,                  # total retry attempts
    backoff_factor=1,         # sleep between retries: {backoff factor} * (2 ** retry count)
    status_forcelist=[429, 500, 502, 503, 504],  # retry on these statuses
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]  # methods to retry
)

# Mount to session
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)

# Debug/test mode flag
# DEBUG_MODE = os.environ.get('DEBUG_MODE', '').lower() in ('true', '1', 'yes')
DEBUG_MODE = False

# GitHub token from environment - try manage-aquifer first, then GITHUB_AQUIFER_API_KEY
GITHUB_TOKEN = os.environ.get('manage-aquifer', '') or os.environ.get('GITHUB_AQUIFER_API_KEY', '')

def get_headers():
    """Get headers for GitHub API requests"""
    headers = {}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    return headers


def check_rate_limit():
    """Check GitHub API rate limit status"""
    try:
        response = session.get(f'{GITHUB_API}/rate_limit', headers=get_headers())
        response.raise_for_status()
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
        print(f"Error checking rate limit: {e}")
        
    if response.status_code == 200:
        data = response.json()
        core = data.get('resources', {}).get('core', {})
        remaining = core.get('remaining', 0)
        reset_time = core.get('reset', 0)
        if remaining < 10:
            import time
            wait_time = max(0, reset_time - time.time())
            print(f"WARNING: Only {remaining} API calls remaining. Rate limit resets in {wait_time:.0f} seconds.")
            if wait_time > 0 and wait_time < 3600:  # Only wait if less than 1 hour
                print(f"Waiting {wait_time:.0f} seconds for rate limit reset...")
                time.sleep(wait_time + 5)  # Add 5 second buffer
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
    try:
        response = session.get(url, headers=get_headers())
        response.raise_for_status()
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
        print(f"Error fetching README.md: {e}")
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
    
    # standardize emdashes
    html = re.sub(r'—', r'&mdash;', html)
    
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
    all_repos = []
    page = 1
    per_page = 100
    
    while True:
        try:
            response = session.get(
                f'{GITHUB_API}/orgs/{ORG_NAME}/repos?per_page={per_page}&page={page}',
                headers=get_headers()
            )
            response.raise_for_status()
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
            print(f"Error retrieving repositories: {e}")
        
        if response.status_code == 403:
            # Check if it's a rate limit issue
            check_rate_limit()
            response = requests.get(
                f'{GITHUB_API}/orgs/{ORG_NAME}/repos?per_page={per_page}&page={page}',
                headers=get_headers()
            )
        
        response.raise_for_status()
        repos = response.json()
        
        if not repos:
            break  # No more pages
        
        all_repos.extend(repos)
        
        # Check if there are more pages
        if len(repos) < per_page:
            break
        
        page += 1
    
    # Filter repos that are data repositories
    return [
        {
            'name': repo['name'],
            'description': repo.get('description', ''),
            'url': repo['html_url']
        }
        for repo in all_repos
        if repo['name'] not in EXCLUDED_REPOS and not repo.get('archived', False)
    ]


def fetch_languages(repo_name: str) -> List[str]:
    """Fetch available languages for a repository"""
    try:
        response = session.get(f'{GITHUB_API}/repos/{ORG_NAME}/{repo_name}/contents', headers=get_headers())
        response.raise_for_status()
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
        print(f"Error retrieving repository languages: {e}")

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
    try:
        response = session.get(url, headers=get_headers())
        response.raise_for_status()
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
        print(f"Error retrieving `{repo_name}/{language}/metadata.json`")
    
    if response.status_code != 200:
        return None
    
    return response.json()


def check_directory_exists(repo_name: str, language: str, dir_name: str) -> bool:
    """Check if a directory exists in the repository"""
    url = f'{GITHUB_API}/repos/{ORG_NAME}/{repo_name}/contents/{language}/{dir_name}'
    try:
        response = session.get(url, headers=get_headers())
        response.raise_for_status()
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
        print(f"Skipping `{language}/{dir_name}` (does not exist)")
        
    return response.status_code == 200


def get_first_json_path(metadata: Dict[str, Any]) -> Optional[str]:
    """Extract the first JSON file path from metadata's scripture_burrito/ingredients.
    
    Returns the path to the first ingredient with mimeType 'text/json', or None if not found.
    """
    if not metadata:
        return None
    
    scripture_burrito = metadata.get('scripture_burrito', {})
    ingredients = scripture_burrito.get('ingredients', {})
    
    for path, info in ingredients.items():
        if isinstance(info, dict) and info.get('mimeType') == 'text/json':
            return path
    
    return None


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
        # for metadata that may be missing outside of English versions (e.g. adaptation_notice)
        english_metadata = fetch_metadata(repo_name, "eng")

        
        # Fetch metadata for each language
        for lang in languages:
            print(f"  Fetching metadata for {lang}...")
            metadata = fetch_metadata(repo_name, lang)
            
            if metadata:
                resource_meta = metadata.get('resource_metadata', {})
                license_meta = resource_meta.get('license_info', {})
                
                # Get the resource title - only use resource_metadata/title
                if lang == "eng":
                    title = resource_meta.get('title') or repo_name
                else:
                    title = resource_meta.get('aquifer_name') or resource_meta.get('title')
                
                # Get adaptation notice if available
                adaptation_notice = resource_meta.get('adaptation_notice')
                # if empty and there is English metadata, then get the English
                if (adaptation_notice == "") and (english_metadata is not None):
                    adaptation_notice = english_metadata["resource_metadata"].get('adaptation_notice')
                
                # Check for all format directories generically
                format_checks = {}
                for format_name in ['json', 'md', 'pdf', 'docx', 'usx', 'usfm', 'audio']:
                    format_checks[f'has_{format_name}'] = check_directory_exists(repo_name, lang, format_name)
                
                # Get first JSON file path for preview
                first_json_path = get_first_json_path(metadata)
                
                resource_data['languages'][lang] = {
                    'code': lang,
                    'name': get_language_name(lang),
                    'title': title,
                    'version': resource_meta.get('version'),
                    'resource_type': resource_meta.get('resource_type') or resource_meta.get('aquifer_type'),
                    'content_type': resource_meta.get('content_type'),
                    'language': resource_meta.get('language'),
                    'first_json_path': first_json_path,
                    'citation': {
                        'title': license_meta.get('title'),
                        'copyright_dates': license_meta.get('copyright', {}).get('dates'),
                        'copyright_holder': license_meta.get('copyright', {}).get('holder', {}).get('name'),
                        'license_name': None,
                        'adaptation_notice': adaptation_notice
                    },
                    **format_checks  # Add all format availability flags
                }
                
                # Get license name
                licenses = license_meta.get('licenses', [])
                if licenses and isinstance(licenses, list) and len(licenses) > 0:
                    first_license = licenses[0]
                    lang_code = resource_meta.get('language', 'eng')
                    if isinstance(first_license, dict) and lang_code in first_license:
                        resource_data['languages'][lang]['citation']['license_name'] = \
                            first_license[lang_code].get('name')
                    elif isinstance(first_license, dict) and "eng" in first_license:
                        resource_data['languages'][lang]['citation']['license_name'] = \
                            first_license["eng"].get('name')
                
                # Set the resource title from English metadata if available, otherwise use first language
                if 'title' not in resource_data:
                    if lang == 'eng':
                        # Prioritize English title
                        resource_data['title'] = title
                    else:
                        # Temporarily store title from non-English language
                        resource_data['_temp_title'] = title
        
        # Only add resources that have at least one language with metadata
        if resource_data['languages']:
            # If we didn't find English title, use the temporary title from first language
            if 'title' not in resource_data:
                if '_temp_title' in resource_data:
                    resource_data['title'] = resource_data['_temp_title']
                    del resource_data['_temp_title']
                else:
                    # Default title to formatted repo name if no metadata title found
                    # Convert camelCase to Title Case
                    resource_data['title'] = re.sub(r'([A-Z])', r' \1', repo_name).strip()
            # Clean up temporary title if it exists
            elif '_temp_title' in resource_data:
                del resource_data['_temp_title']
            
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
<!--
    <nav class="breadcrumb">
        <div class="container">
            <a href="index.html">Home</a> &gt; Catalog
        </div>
    </nav>
 -->
    <main class="catalog-layout">
        <aside class="catalog-sidebar">
            <section id="catalog-controls">
                <h2>Filters</h2>
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
        </aside>

        <div class="catalog-content">
            <section id="content-viewer" class="hidden">
                <div class="tabs">
                    <button class="tab-btn active" data-tab="details">Resource Details</button>
                    <button class="tab-btn" data-tab="preview">Resource Preview</button>
                </div>
                <div id="tab-details" class="tab-content active">
                    <div id="content-display"></div>
                </div>
                <div id="tab-preview" class="tab-content">
                    <div class="preview-navigation">
                        <button id="prev-article-btn" class="nav-btn" disabled>
                            <span class="nav-arrow">←</span> Previous
                        </button>
                        <span id="article-position" class="article-position"></span>
                        <button id="next-article-btn" class="nav-btn" disabled>
                            Next <span class="nav-arrow">→</span>
                        </button>
                    </div>
                    <div id="preview-display">
                        <p class="loading-message">Select a resource to see a preview.</p>
                    </div>
                </div>
            </section>
        </div>
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
const contentDisplayDiv = document.getElementById('content-display');
const contentViewerSection = document.getElementById('content-viewer');
const previewDisplayDiv = document.getElementById('preview-display');
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const prevArticleBtn = document.getElementById('prev-article-btn');
const nextArticleBtn = document.getElementById('next-article-btn');
const articlePositionSpan = document.getElementById('article-position');

// State
let selectedResource = null;
let selectedLanguage = null;
let previewLoaded = false;
let previewCache = {};
let currentArticleIndex = 0;
let currentArticles = [];

// Setup event listeners
resourceSelect.addEventListener('change', handleResourceChange);
languageSelect.addEventListener('change', handleLanguageChange);

// Navigation button event listeners
prevArticleBtn.addEventListener('click', () => {
    if (currentArticleIndex > 0) {
        currentArticleIndex--;
        displayArticle();
    }
});

nextArticleBtn.addEventListener('click', () => {
    if (currentArticleIndex < currentArticles.length - 1) {
        currentArticleIndex++;
        displayArticle();
    }
});

// Tab switching
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;
        switchToTab(tabId);
    });
});

// Switch to a specific tab
function switchToTab(tabId) {
    // Update active states
    tabBtns.forEach(b => b.classList.remove('active'));
    tabContents.forEach(c => c.classList.remove('active'));
    
    const targetBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    if (targetBtn) {
        targetBtn.classList.add('active');
    }
    document.getElementById('tab-' + tabId).classList.add('active');
    
    // Load preview if switching to preview tab
    if (tabId === 'preview' && selectedResource && selectedLanguage) {
        loadPreview();
    }
}

// Load preview content dynamically
async function loadPreview() {
    if (!selectedResource || !selectedLanguage) {
        hideNavigation();
        previewDisplayDiv.innerHTML = '<p class="loading-message">Select a resource to see a preview.</p>';
        return;
    }
    
    const langData = selectedResource.languages[selectedLanguage];
    if (!langData) {
        hideNavigation();
        previewDisplayDiv.innerHTML = '<p class="no-preview">No preview available for this selection.</p>';
        return;
    }
    
    // Check if we have a JSON path for preview
    const jsonPath = langData.first_json_path;
    if (!jsonPath || !langData.has_json) {
        hideNavigation();
        previewDisplayDiv.innerHTML = '<p class="no-preview">No preview available. This resource does not have JSON content files.</p>';
        return;
    }
    
    // Check cache first - use delimiter-separated key
    const cacheKey = `${selectedResource.name}:${selectedLanguage}:${jsonPath}`;
    if (previewCache[cacheKey]) {
        currentArticles = previewCache[cacheKey];
        currentArticleIndex = 0;
        displayArticle();
        return;
    }
    
    // Show loading message and hide navigation while loading
    hideNavigation();
    previewDisplayDiv.innerHTML = '<p class="loading-message">Loading preview...</p>';
    
    try {
        // Construct URL to raw JSON file
        const url = `https://raw.githubusercontent.com/${ORG_NAME}/${selectedResource.name}/main/${selectedLanguage}/${jsonPath}`;
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch preview content');
        }
        
        const data = await response.json();
        
        // Extract articles from the data array
        // SECURITY NOTE: content is trusted HTML from the BibleAquifer organization's own 
        // JSON files. This is intentionally rendered as HTML to support rich formatting 
        // (headings, paragraphs, links, etc.) in the preview.
        if (Array.isArray(data) && data.length > 0) {
            // Store articles in cache and state
            currentArticles = data;
            previewCache[cacheKey] = data;
            currentArticleIndex = 0;
            displayArticle();
        } else {
            hideNavigation();
            previewDisplayDiv.innerHTML = '<p class="no-preview">No preview content found in the JSON file.</p>';
        }
    } catch (error) {
        console.error('Error loading preview:', error);
        hideNavigation();
        previewDisplayDiv.innerHTML = '<p class="error-message">Error loading preview. Please try again later.</p>';
    }
}

// Display the current article based on index
function displayArticle() {
    if (!currentArticles || currentArticles.length === 0) {
        hideNavigation();
        previewDisplayDiv.innerHTML = '<p class="no-preview">No articles available.</p>';
        return;
    }
    
    const article = currentArticles[currentArticleIndex];
    if (!article || !article.content) {
        previewDisplayDiv.innerHTML = '<p class="no-preview">Article content not available.</p>';
        updateNavigationState();
        return;
    }
    
    const title = article.title || '';
    const titleHtml = title ? `<p><b>${title}</b></p>` : '';
    const previewHtml = '<div class="preview-content">' + titleHtml + article.content + '</div>';
    previewDisplayDiv.innerHTML = previewHtml;
    
    updateNavigationState();
}

// Update navigation button states and position indicator
function updateNavigationState() {
    const total = currentArticles.length;
    const current = currentArticleIndex + 1;
    
    // Update position indicator
    articlePositionSpan.textContent = `Article ${current} of ${total}`;
    
    // Update button states
    prevArticleBtn.disabled = currentArticleIndex === 0;
    nextArticleBtn.disabled = currentArticleIndex >= total - 1;
}

// Hide navigation controls
function hideNavigation() {
    prevArticleBtn.disabled = true;
    nextArticleBtn.disabled = true;
    articlePositionSpan.textContent = '';
}

// Reset article state when resource or language changes
function resetArticleState() {
    currentArticleIndex = 0;
    currentArticles = [];
    hideNavigation();
}

// Handle resource selection
function handleResourceChange() {
    const resourceId = resourceSelect.value;
    
    if (!resourceId) {
        languageSelect.innerHTML = '<option value="">Select a resource first</option>';
        languageSelect.disabled = true;
        contentDisplayDiv.innerHTML = '';
        previewDisplayDiv.innerHTML = '<p class="loading-message">Select a resource to see a preview.</p>';
        contentViewerSection.classList.add('hidden');
        resetArticleState();
        return;
    }
    
    selectedResource = RESOURCES_DATA[resourceId];
    resetArticleState();
    
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
    
    // Switch to Details tab when resource changes
    switchToTab('details');
    
    // Reset preview display
    previewDisplayDiv.innerHTML = '<p class="loading-message">Loading preview...</p>';
    
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
        previewDisplayDiv.innerHTML = '<p class="loading-message">Select a resource to see a preview.</p>';
        contentViewerSection.classList.add('hidden');
        resetArticleState();
        return;
    }
    
    // Switch to Details tab when language changes
    switchToTab('details');
    
    // Reset preview and article state when language changes
    resetArticleState();
    previewDisplayDiv.innerHTML = '<p class="loading-message">Loading preview...</p>';
    
    displayLanguageMetadata();
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
    
    // Display resource title and description at the top
    //    html += `<div class="resource-header">`;
    //    html += `<h3>${selectedResource.title}</h3>`;
    //    html += `<p>${selectedResource.description || 'No description available'}</p>`;
    //    html += `<p><a href="${selectedResource.url}" target="_blank">View on GitHub</a></p>`;
    //    html += `</div>`;
    //    html += '<hr style="margin: 1.5rem 0;">';
    
    // Display citation if available
    if (langData.citation && langData.citation.title) {
        html += '<h3>Citation</h3>';
        html += '<p class="citation">';
        html += `<em>${langData.citation.title}</em>`;
        
        if (langData.citation.copyright_holder) {
            html += `. &copy; ${langData.citation.copyright_dates || ''} ${langData.citation.copyright_holder}`;
        }
        
        if (langData.citation.license_name) {
            html += `. Licensed under ${langData.citation.license_name}`;
        }
        
        html += '.</p>';
        
        // Add adaptation notice if available
        if (langData.citation.adaptation_notice) {
            html += `<div class="adaptation-notice">${langData.citation.adaptation_notice}</div>`;
        }
        
        html += '<hr style="margin: 1.5rem 0;">';
    }
    
    // Create two-column layout for Resource Information and Access Resource
    html += '<div class="resource-details-columns">';
    
    // Left column: Resource Information
    html += '<div class="resource-info-column">';
    html += '<h3>Resource Information</h3>';
    html += '<div class="metadata-grid">';
    
    const metadataFields = [
        { label: 'Title', value: langData.title },
        { label: 'Language', value: langData.language },
        { label: 'Schema Version', value: langData.version },
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
    html += '</div>'; // Close resource-info-column
    
    // Right column: Access Resource
    html += '<div class="resource-access-column">';
    html += '<h3>Access Resource</h3>';
    html += '<p>Browse or download this resource:</p>';
    html += '<ul class="download-list">';
    
    // Dynamically check and add links for all available formats
    const formats = [
        { key: 'has_json', name: 'JSON', label: 'Browse JSON files' },
        { key: 'has_md', name: 'Markdown', label: 'Browse Markdown files' },
        { key: 'has_pdf', name: 'PDF', label: 'Browse PDF files' },
        { key: 'has_docx', name: 'DOCX', label: 'Browse DOCX files' },
        { key: 'has_usx', name: 'USX', label: 'Browse USX files' },
        { key: 'has_usfm', name: 'USFM', label: 'Browse USFM files' },
        { key: 'has_audio', name: 'audio', label: 'Browse audio timings' }
        
    ];
    
    formats.forEach(format => {
        if (langData[format.key]) {
            const dirName = format.key.replace('has_', '');
            html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/tree/main/${selectedLanguage}/${dirName}" target="_blank">${format.label}</a></li>`;
        }
    });
    
    html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/releases/latest" target="_blank">Download latest release</a></li>`;
    html += '</ul>';
    html += '</div>'; // Close resource-access-column
    html += '</div>'; // Close resource-details-columns
    
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
    
    # Check for GitHub token - must have manage-aquifer or GITHUB_AQUIFER_API_KEY
    if not GITHUB_TOKEN and not DEBUG_MODE:
        print("\nERROR: Required GitHub token not found.")
        print("Please set one of the following environment variables:")
        print("  - manage-aquifer")
        print("  - GITHUB_AQUIFER_API_KEY")
        print("\nAlternatively, set DEBUG_MODE=true to use test data.")
        print("\nExample: export manage-aquifer=your_token_here")
        exit(1)
    
    if DEBUG_MODE:
        print("\nDEBUG MODE: Running with test/sample data")
    elif GITHUB_TOKEN:
        print(f"\nUsing GitHub token for API access")
    
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
    output_dir = os.path.join(os.path.dirname(__file__), '..')
    with open(os.path.join(output_dir, 'resources_data.yaml'), 'w') as f:
        yaml.dump(resources, f, default_flow_style=False, sort_keys=False)
    
    # Generate HTML files
    print("\n4. Generating index.html...\n")
    index_html = generate_index_html(readme_formatted)
    with open(os.path.join(output_dir, 'index.html'), 'w') as f:
        f.write(index_html)
    
    print("5. Generating catalog.html...")
    catalog_html = generate_catalog_html(resources)
    with open(os.path.join(output_dir, 'catalog.html'), 'w', encoding="utf-8") as f:
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
