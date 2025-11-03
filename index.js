// GitHub API configuration
const ORG_NAME = 'BibleAquifer';
const ORG_REPO_NAME = '.github';
const README_PATH = 'profile/README.md';

// Simple markdown to HTML converter
function markdownToHTML(markdown) {
    let html = markdown;
    
    // Remove the first H1 header and its following line (subtitle) if present
    // The site already has the title in the header
    html = html.replace(/^# [^\n]+\n[^\n]+\n\n/m, '');
    
    // Convert headers (## Header)
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    
    // Store links temporarily to avoid underscore conflicts
    const links = [];
    let linkIndex = 0;
    
    // Extract and replace links with placeholders (using a pattern that won't match italic regex)
    html = html.replace(/\[_([^_]+)_\]\(([^)]+)\)/g, (match, text, url) => {
        const placeholder = `{{LINK${linkIndex}}}`;
        links.push({ placeholder, html: `<a href="${url}" target="_blank"><em>${text}</em></a>` });
        linkIndex++;
        return placeholder;
    });
    
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
        const placeholder = `{{LINK${linkIndex}}}`;
        links.push({ placeholder, html: `<a href="${url}" target="_blank">${text}</a>` });
        linkIndex++;
        return placeholder;
    });
    
    // Convert bold/italic _text_ (now safe since links are placeholders)
    html = html.replace(/_([^_]+)_/g, '<em>$1</em>');
    
    // Restore links
    links.forEach(link => {
        html = html.replace(link.placeholder, link.html);
    });
    
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
        
        // Fetch README from GitHub organization
        const url = `https://raw.githubusercontent.com/${ORG_NAME}/${ORG_REPO_NAME}/main/${README_PATH}`;
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
                    // First section doesn't have an h2, skip if empty
                    if (section.length > 0) {
                        formattedContent += `<section class="content-section">${section}</section>`;
                    }
                } else {
                    // Add h2 back (section already contains </h2>)
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
