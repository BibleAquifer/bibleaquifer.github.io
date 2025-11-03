// GitHub API configuration
const GITHUB_API = 'https://api.github.com';
const ORG_NAME = 'BibleAquifer';

// Excluded repos that don't follow the standard data structure
const EXCLUDED_REPOS = ['docs', 'ACAI', 'bibleaquifer.github.io', '.github'];

// UI configuration
const ERROR_DISPLAY_DURATION = 5000; // milliseconds

// State management
let resources = [];
let selectedResource = null;
let selectedLanguage = null;
let languageMetadata = null;

// DOM elements
const resourceSelect = document.getElementById('resource-select');
const languageSelect = document.getElementById('language-select');
const resourceMetadataDiv = document.getElementById('resource-metadata');
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
        resourceMetadataDiv.innerHTML = '';
        contentDisplayDiv.innerHTML = '';
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
async function handleLanguageChange() {
    selectedLanguage = languageSelect.value;
    
    if (!selectedLanguage) {
        contentDisplayDiv.innerHTML = '';
        return;
    }
    
    // Load and display language metadata
    await loadLanguageMetadata();
}

// Load language-specific metadata
async function loadLanguageMetadata() {
    try {
        contentDisplayDiv.innerHTML = '<div class="loading">Loading resource details...</div>';
        
        const url = `https://raw.githubusercontent.com/${ORG_NAME}/${selectedResource.name}/main/${selectedLanguage}/metadata.json`;
        const response = await fetch(url);
        
        if (!response.ok) throw new Error('Failed to fetch metadata');
        
        languageMetadata = await response.json();
        displayLanguageMetadata();
        
    } catch (error) {
        console.error('Error loading language metadata:', error);
        contentDisplayDiv.innerHTML = '<div class="error">Failed to load resource metadata.</div>';
    }
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
    if (!languageMetadata) {
        contentDisplayDiv.innerHTML = '<p>No metadata available for this language.</p>';
        return;
    }
    
    let html = '<h3>Resource Information</h3>';
    html += '<div class="metadata-grid">';
    
    // Display key metadata fields
    const displayFields = [
        'language',
        'languageName',
        'title',
        'version',
        'subject',
        'description',
        'rights',
        'publisher',
        'issued',
        'modified'
    ];
    
    displayFields.forEach(field => {
        if (languageMetadata[field]) {
            html += `
                <div class="metadata-label">${formatFieldName(field)}:</div>
                <div class="metadata-value">${languageMetadata[field]}</div>
            `;
        }
    });
    
    html += '</div>';
    
    // Add download links
    if (selectedResource && selectedLanguage) {
        html += '<hr style="margin: 1.5rem 0;">';
        html += '<h3>Download Options</h3>';
        html += '<p>Access this resource directly from GitHub:</p>';
        html += '<ul>';
        html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/tree/main/${selectedLanguage}/json" target="_blank">View JSON files</a></li>`;
        html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/tree/main/${selectedLanguage}/md" target="_blank">View Markdown files</a></li>`;
        html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/releases" target="_blank">Download from releases</a></li>`;
        html += '</ul>';
    }
    
    contentDisplayDiv.innerHTML = html;
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
// Language codes follow ISO 639-3 standard (3-letter codes)
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

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    
    const main = document.querySelector('main');
    main.insertBefore(errorDiv, main.firstChild);
    
    setTimeout(() => errorDiv.remove(), ERROR_DISPLAY_DURATION);
}

// Initialize the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
