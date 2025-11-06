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
const resourceInfoSection = document.getElementById('resource-info');
const contentViewerSection = document.getElementById('content-viewer');

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
            title: repo.name,
            description: repo.description,
            url: repo.html_url
        }));
        
        // Populate resource dropdown
        resourceSelect.innerHTML = '<option value="">Select a resource...</option>';
        resources.forEach(resource => {
            const option = document.createElement('option');
            option.value = resource.name;
            option.textContent = resource.name;
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
        resourceInfoSection.classList.add('hidden');
        contentViewerSection.classList.add('hidden');
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
        
        // Check if 'eng' exists in the languages
        const hasEng = languages.some(lang => lang.name === 'eng');
        
        // Populate language dropdown
        languageSelect.innerHTML = '<option value="">Select a language...</option>';
        languages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.name;
            option.textContent = getLanguageName(lang.name);
            // Select 'eng' by default if it exists
            if (lang.name === 'eng' && hasEng) {
                option.selected = true;
            }
            languageSelect.appendChild(option);
        });
        
        languageSelect.disabled = false;
        
        // Display resource metadata
        displayResourceInfo();
        
        // If 'eng' exists, auto-load it
        if (hasEng) {
            selectedLanguage = 'eng';
            await loadLanguageMetadata();
        }
        
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
        contentViewerSection.classList.add('hidden');
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
        await displayLanguageMetadata();
        
    } catch (error) {
        console.error('Error loading language metadata:', error);
        contentDisplayDiv.innerHTML = '<div class="error">Failed to load resource metadata.</div>';
    }
}

// Check if a directory exists in the repository
async function checkDirectoryExists(resourceName, language, dirName) {
    try {
        const url = `${GITHUB_API}/repos/${ORG_NAME}/${resourceName}/contents/${language}/${dirName}`;
        const response = await fetch(url);
        return response.ok;
    } catch (error) {
        console.error(`Error checking directory ${dirName}:`, error);
        return false;
    }
}

// Display resource information
function displayResourceInfo() {
    if (!selectedResource) return;
    
    resourceMetadataDiv.innerHTML = `
        <h3>${selectedResource.title}</h3>
        <p>${selectedResource.description || 'No description available'}</p>
        <p><a href="${selectedResource.url}" target="_blank">View on GitHub</a></p>
    `;
    
    // Show the resource info section
    resourceInfoSection.classList.remove('hidden');
}

// Display language metadata
async function displayLanguageMetadata() {
    if (!languageMetadata) {
        contentDisplayDiv.innerHTML = '<p>No metadata available for this language.</p>';
        return;
    }
    
    const resourceMeta = languageMetadata.resource_metadata || {};
    const licenseMeta = resourceMeta.license_info || {};
    
    let html = '';
    
    // Display citation if available
    if (licenseMeta.title) {
        html += '<h3>Citation</h3>';
        html += '<p class="citation">';
        html += `<em>${licenseMeta.title}</em>`;
        
        // Add copyright holder if available
        if (licenseMeta.copyright?.holder?.name) {
            html += `. © ${licenseMeta.copyright.dates || ''} ${licenseMeta.copyright.holder.name}`;
        }
        
        // Add license info
        if (licenseMeta.licenses && licenseMeta.licenses.length > 0) {
            const firstLicense = licenseMeta.licenses[0];
            const langCode = resourceMeta.language || 'eng';
            if (firstLicense[langCode]) {
                html += `. Licensed under ${firstLicense[langCode].name}`;
            }
        }
        
        html += '.</p>';
        html += '<hr style="margin: 1.5rem 0;">';
    }
    
    // Display key metadata
    html += '<h3>Resource Information</h3>';
    html += '<div class="metadata-grid">';
    
    const metadataToDisplay = [
        { label: 'Title', value: licenseMeta.title || resourceMeta.title },
        { label: 'Language', value: resourceMeta.language },
        { label: 'Version', value: resourceMeta.version },
        { label: 'Type', value: resourceMeta.resource_type || resourceMeta.aquifer_type },
        { label: 'Content Type', value: resourceMeta.content_type }
    ];
    
    metadataToDisplay.forEach(item => {
        if (item.value) {
            html += `
                <div class="metadata-label">${item.label}:</div>
                <div class="metadata-value">${item.value}</div>
            `;
        }
    });
    
    html += '</div>';
    
    // Add download links
    if (selectedResource && selectedLanguage) {
        html += '<hr style="margin: 1.5rem 0;">';
        html += '<h3>Access Resource</h3>';
        html += '<p>Browse or download this resource:</p>';
        html += '<ul class="download-list">';
        html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/tree/main/${selectedLanguage}/json" target="_blank">Browse JSON files</a></li>`;
        html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/tree/main/${selectedLanguage}/md" target="_blank">Browse Markdown files</a></li>`;
        
        // Check for pdf and docx directories and add links if they exist
        const hasPdf = await checkDirectoryExists(selectedResource.name, selectedLanguage, 'pdf');
        if (hasPdf) {
            html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/tree/main/${selectedLanguage}/pdf" target="_blank">Browse PDF files</a></li>`;
        }
        
        const hasDocx = await checkDirectoryExists(selectedResource.name, selectedLanguage, 'docx');
        if (hasDocx) {
            html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/tree/main/${selectedLanguage}/docx" target="_blank">Browse DOCX files</a></li>`;
        }
        
        html += `<li><a href="https://github.com/${ORG_NAME}/${selectedResource.name}/releases/latest" target="_blank">Download latest release</a></li>`;
        html += '</ul>';
    }
    
    contentDisplayDiv.innerHTML = html;
    
    // Show the content viewer section
    contentViewerSection.classList.remove('hidden');
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
