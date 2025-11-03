// GitHub API configuration
const GITHUB_API = 'https://api.github.com';
const ORG_NAME = 'BibleAquifer';
const REPO_NAME = 'bibleaquifer.github.io';
const README_PATH = '.github/profile/README.md';

// Simple markdown to HTML converter
function markdownToHTML(markdown) {
    let html = markdown;
    
    // Convert headers (## Header)
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    
    // Convert links [text](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    
    // Convert bold/italic _text_
    html = html.replace(/_(.*?)_/g, '<em>$1</em>');
    
    // Convert code `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Split into paragraphs and wrap in <p> tags
    const lines = html.split('\n');
    let result = '';
    let inParagraph = false;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // Skip empty lines
        if (line === '') {
            if (inParagraph) {
                result += '</p>\n';
                inParagraph = false;
            }
            continue;
        }
        
        // Headers don't need paragraph wrapping
        if (line.startsWith('<h2>')) {
            if (inParagraph) {
                result += '</p>\n';
                inParagraph = false;
            }
            result += line + '\n';
        } else {
            // Regular text - wrap in paragraph
            if (!inParagraph) {
                result += '<p>';
                inParagraph = true;
            } else {
                result += ' ';
            }
            result += line;
        }
    }
    
    // Close any open paragraph
    if (inParagraph) {
        result += '</p>\n';
    }
    
    return result;
}

// Load and display README content
async function loadReadmeContent() {
    const contentContainer = document.getElementById('dynamic-content');
    
    if (!contentContainer) {
        console.error('Content container not found');
        return;
    }
    
    try {
        // Show loading state
        contentContainer.innerHTML = '<div class="loading">Loading content...</div>';
        
        // Fetch README from GitHub
        const url = `https://raw.githubusercontent.com/${ORG_NAME}/${REPO_NAME}/main/${README_PATH}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch README: ${response.status}`);
        }
        
        const markdownContent = await response.text();
        
        // Convert markdown to HTML
        const htmlContent = markdownToHTML(markdownContent);
        
        // Wrap each section in a content-section div
        const sections = htmlContent.split('<h2>');
        let formattedContent = '';
        
        for (let i = 0; i < sections.length; i++) {
            const section = sections[i].trim();
            if (section) {
                if (i === 0) {
                    // First section doesn't have an h2, wrap it differently if needed
                    formattedContent += `<section class="content-section">${section}</section>`;
                } else {
                    // Add h2 back and wrap in section
                    formattedContent += `<section class="content-section"><h2>${section}</section>`;
                }
            }
        }
        
        // Display the content
        contentContainer.innerHTML = formattedContent;
        
    } catch (error) {
        console.error('Error loading README content:', error);
        contentContainer.innerHTML = `
            <section class="content-section">
                <div class="error">
                    Failed to load content. Please check your internet connection or try again later.
                </div>
            </section>
        `;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadReadmeContent);
} else {
    loadReadmeContent();
}
