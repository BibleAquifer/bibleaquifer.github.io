// GitHub API configuration
const GITHUB_API = 'https://api.github.com';
const ORG_NAME = 'BibleAquifer';

// Excluded repos that don't follow the standard data structure
const EXCLUDED_REPOS = ['docs', 'ACAI', 'bibleaquifer.github.io', '.github'];

// State management
let resources = [];
let selectedResource = null;
let selectedLanguage = null;
let languageMetadata = null;
let articles = [];

// DOM elements
const resourceSelect = document.getElementById('resource-select');
const languageSelect = document.getElementById('language-select');
const loadBtn = document.getElementById('load-btn');
const resourceMetadataDiv = document.getElementById('resource-metadata');
const articleListDiv = document.getElementById('article-list');
const contentDisplayDiv = document.getElementById('content-display');

// Initialize the application
async function init() {
    try {
        await loadResources();
        setupEventListeners();
    } catch (error) {
        console.error('Initialization error:', error);
        showError('Failed to initialize the application. Please refresh the page.');
    }
}

// Setup event listeners
function setupEventListeners() {
    resourceSelect.addEventListener('change', handleResourceChange);
    languageSelect.addEventListener('change', handleLanguageChange);
    loadBtn.addEventListener('click', loadContent);
}

// Load available resources from GitHub
async function loadResources() {
    try {
        resourceSelect.innerHTML = '<option value="">Loading resources...</option>';
        
        const response = await fetch(`${GITHUB_API}/orgs/${ORG_NAME}/repos?per_page=100`);
        if (!response.ok) throw new Error('Failed to fetch repositories');
        
        const repos = await response.json();
        
        // Filter repos that are data repositories
        resources = repos.filter(repo => 
            !EXCLUDED_REPOS.includes(repo.name) && !repo.archived
        ).map(repo => ({
            name: repo.name,
            description: repo.description,
            url: repo.html_url
        }));
        
        // Populate resource dropdown
        resourceSelect.innerHTML = '<option value="">Select a resource...</option>';
        resources.forEach(resource => {
            const option = document.createElement('option');
            option.value = resource.name;
            option.textContent = formatResourceName(resource.name);
            resourceSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading resources:', error);
        resourceSelect.innerHTML = '<option value="">Error loading resources</option>';
        showError('Failed to load resources. Please check your internet connection.');
    }
}

// Handle resource selection change
async function handleResourceChange() {
    const resourceName = resourceSelect.value;
    
    if (!resourceName) {
        languageSelect.innerHTML = '<option value="">Select a resource first</option>';
        languageSelect.disabled = true;
        loadBtn.disabled = true;
        resourceMetadataDiv.innerHTML = '';
        return;
    }
    
    selectedResource = resources.find(r => r.name === resourceName);
    
    try {
        languageSelect.innerHTML = '<option value="">Loading languages...</option>';
        
        // Fetch the repository contents to get language directories
        const response = await fetch(`${GITHUB_API}/repos/${ORG_NAME}/${resourceName}/contents`);
        if (!response.ok) throw new Error('Failed to fetch repository contents');
        
        const contents = await response.json();
        
        // Filter for directories (languages are 3-letter codes)
        const languages = contents.filter(item => 
            item.type === 'dir' && item.name.length === 3
        );
        
        // Populate language dropdown
        languageSelect.innerHTML = '<option value="">Select a language...</option>';
        languages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.name;
            option.textContent = getLanguageName(lang.name);
            languageSelect.appendChild(option);
        });
        
        languageSelect.disabled = false;
        
        // Display resource metadata
        displayResourceInfo();
        
    } catch (error) {
        console.error('Error loading languages:', error);
        languageSelect.innerHTML = '<option value="">Error loading languages</option>';
        showError('Failed to load languages for this resource.');
    }
}

// Handle language selection change
function handleLanguageChange() {
    selectedLanguage = languageSelect.value;
    loadBtn.disabled = !selectedLanguage;
    
    if (selectedLanguage) {
        articleListDiv.innerHTML = '';
        contentDisplayDiv.innerHTML = '';
    }
}

// Load content for selected resource and language
async function loadContent() {
    if (!selectedResource || !selectedLanguage) return;
    
    try {
        loadBtn.disabled = true;
        loadBtn.textContent = 'Loading...';
        
        // Load language metadata
        await loadLanguageMetadata();
        
        // Load article list
        await loadArticleList();
        
        loadBtn.textContent = 'Load Content';
        loadBtn.disabled = false;
        
    } catch (error) {
        console.error('Error loading content:', error);
        showError('Failed to load content. Please try again.');
        loadBtn.textContent = 'Load Content';
        loadBtn.disabled = false;
    }
}

// Load language-specific metadata
async function loadLanguageMetadata() {
    try {
        const url = `https://raw.githubusercontent.com/${ORG_NAME}/${selectedResource.name}/main/${selectedLanguage}/metadata.json`;
        const response = await fetch(url);
        
        if (!response.ok) throw new Error('Failed to fetch metadata');
        
        languageMetadata = await response.json();
        displayLanguageMetadata();
        
    } catch (error) {
        console.error('Error loading language metadata:', error);
        languageMetadata = null;
    }
}

// Load list of articles
async function loadArticleList() {
    try {
        articleListDiv.innerHTML = '<div class="loading">Loading articles...</div>';
        
        // Fetch JSON directory contents
        const response = await fetch(
            `${GITHUB_API}/repos/${ORG_NAME}/${selectedResource.name}/contents/${selectedLanguage}/json`
        );
        
        if (!response.ok) throw new Error('Failed to fetch articles');
        
        const files = await response.json();
        
        // Filter JSON files
        articles = files.filter(file => file.name.endsWith('.json'));
        
        displayArticleList();
        
    } catch (error) {
        console.error('Error loading article list:', error);
        articleListDiv.innerHTML = '<div class="error">Failed to load articles.</div>';
    }
}

// Display article list
function displayArticleList() {
    articleListDiv.innerHTML = '';
    
    if (articles.length === 0) {
        articleListDiv.innerHTML = '<p>No articles found for this language.</p>';
        return;
    }
    
    articles.forEach(article => {
        const articleItem = document.createElement('div');
        articleItem.className = 'article-item';
        
        const title = article.name.replace('.json', '').replace(/_/g, ' ');
        
        articleItem.innerHTML = `
            <h4>${title}</h4>
            <p>Click to view content</p>
        `;
        
        articleItem.addEventListener('click', () => loadArticle(article));
        
        articleListDiv.appendChild(articleItem);
    });
}

// Load and display an article
async function loadArticle(article) {
    try {
        contentDisplayDiv.innerHTML = '<div class="loading">Loading article...</div>';
        
        // Fetch the JSON content
        const response = await fetch(article.download_url);
        if (!response.ok) throw new Error('Failed to fetch article');
        
        const content = await response.json();
        
        displayArticleContent(content, article.name);
        
    } catch (error) {
        console.error('Error loading article:', error);
        contentDisplayDiv.innerHTML = '<div class="error">Failed to load article content.</div>';
    }
}

// Display article content
function displayArticleContent(content, filename) {
    const title = filename.replace('.json', '').replace(/_/g, ' ');
    
    let html = `<h3>${title}</h3>`;
    
    // Display article metadata if available
    if (content.metadata) {
        html += '<div class="metadata-grid">';
        for (const [key, value] of Object.entries(content.metadata)) {
            if (typeof value === 'string' || typeof value === 'number') {
                html += `
                    <div class="metadata-label">${formatFieldName(key)}:</div>
                    <div class="metadata-value">${value}</div>
                `;
            }
        }
        html += '</div><hr style="margin: 1rem 0;">';
    }
    
    // Display content body
    if (content.content) {
        html += `<div class="content-body">${formatContent(content.content)}</div>`;
    } else if (content.text) {
        html += `<div class="content-body">${formatContent(content.text)}</div>`;
    } else {
        // Display raw JSON if no standard content field
        html += `<pre>${JSON.stringify(content, null, 2)}</pre>`;
    }
    
    contentDisplayDiv.innerHTML = html;
}

// Display resource information
function displayResourceInfo() {
    if (!selectedResource) return;
    
    resourceMetadataDiv.innerHTML = `
        <h3>${formatResourceName(selectedResource.name)}</h3>
        <p>${selectedResource.description || 'No description available'}</p>
        <p><a href="${selectedResource.url}" target="_blank">View on GitHub</a></p>
    `;
}

// Display language metadata
function displayLanguageMetadata() {
    if (!languageMetadata) return;
    
    let metadataHtml = '<h4>Language Resource Information</h4>';
    metadataHtml += '<div class="metadata-grid">';
    
    // Display key metadata fields
    const displayFields = ['language', 'languageName', 'title', 'version', 'subject', 'rights'];
    
    displayFields.forEach(field => {
        if (languageMetadata[field]) {
            metadataHtml += `
                <div class="metadata-label">${formatFieldName(field)}:</div>
                <div class="metadata-value">${languageMetadata[field]}</div>
            `;
        }
    });
    
    metadataHtml += '</div>';
    
    resourceMetadataDiv.innerHTML += metadataHtml;
}

// Helper function to format resource names
function formatResourceName(name) {
    // Convert camelCase to Title Case with spaces
    return name
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .trim();
}

// Helper function to format field names
function formatFieldName(name) {
    return name
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .trim();
}

// Helper function to get language name from code
function getLanguageName(code) {
    const languageMap = {
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
    };
    
    return languageMap[code] || code.toUpperCase();
}

// Helper function to format content (basic markdown-like formatting)
function formatContent(content) {
    if (typeof content !== 'string') {
        return content;
    }
    
    // Basic formatting
    return content
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/^/, '<p>')
        .replace(/$/, '</p>');
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    
    const main = document.querySelector('main');
    main.insertBefore(errorDiv, main.firstChild);
    
    setTimeout(() => errorDiv.remove(), 5000);
}

// Initialize the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
