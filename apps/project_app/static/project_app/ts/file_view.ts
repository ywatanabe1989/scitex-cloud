// =============================================================================
// File View - IIFE wrapper for TypeScript
// =============================================================================

// Local type declarations (Window interface is defined in global.d.ts)
interface CodeThemePreferences {
    light: string;
    dark: string;
}

interface ProjectData {
    owner: string;
    slug: string;
}

interface ThemeResponse {
    code_theme_light?: string;
    code_theme_dark?: string;
    success?: boolean;
    error?: string;
}

interface BranchSwitchResponse {
    success: boolean;
    error?: string;
}

(function() {
    'use strict';

    // =============================================================================
    // Theme Configuration
    // =============================================================================

    const DARK_THEMES: string[] = ['dracula', 'monokai', 'nord', 'atom-one-dark', 'github-dark', 'vs2015'];
    const LIGHT_THEMES: string[] = ['atom-one-light', 'github', 'stackoverflow-light', 'default', 'xcode'];

    // Default themes
    let codeThemePreferences: CodeThemePreferences = {
        light: 'atom-one-light',
        dark: 'nord'
    };

    // Store original code content
    let originalCodeContent: string | null = null;

    // =============================================================================
    // Helper Functions
    // =============================================================================

    // Helper function to escape HTML
    function escapeHtml(text: string): string {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Helper function to get CSRF token
    function getCookie(name: string): string | null {
        let cookieValue: string | null = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // =============================================================================
    // Theme Management
    // =============================================================================

    // Load theme preferences from database
    async function loadCodeThemePreferences(): Promise<void> {
        try {
            const response = await fetch('/auth/api/get-theme/');
            const data = await response.json() as ThemeResponse;
            if (data.code_theme_light && data.code_theme_dark) {
                codeThemePreferences = {
                    light: data.code_theme_light,
                    dark: data.code_theme_dark
                };
            }
        } catch (error) {
            console.warn('Failed to load code theme preferences:', error);
        }
    }

    // Save theme preferences to database
    async function saveCodeThemePreferences(): Promise<void> {
        try {
            const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement | null;
            const csrfToken = csrfTokenElement?.value || getCookie('csrftoken') || '';
            const response = await fetch('/auth/api/save-theme/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    code_theme_light: codeThemePreferences.light,
                    code_theme_dark: codeThemePreferences.dark
                })
            });
            const data = await response.json() as ThemeResponse;
            if (data.success) {
                console.log('Code theme preferences saved:', codeThemePreferences);
            }
        } catch (error) {
            console.warn('Failed to save code theme preferences:', error);
        }
    }

    // Switch highlight.js theme
    function switchHighlightTheme(themeName: string, reHighlight: boolean = false): void {
        // Disable all themes
        document.querySelectorAll<HTMLLinkElement>('.hljs-theme').forEach(link => {
            link.disabled = true;
        });

        // Enable selected theme
        const themeLink = document.querySelector<HTMLLinkElement>(`.hljs-theme[data-theme-name="${themeName}"]`);
        if (themeLink) {
            themeLink.disabled = false;
            console.log('Switched to highlight theme:', themeName);

            // Re-highlight code if requested
            if (reHighlight && originalCodeContent) {
                const pre = document.querySelector<HTMLPreElement>('.file-content pre');
                if (pre) {
                    const codeElement = pre.querySelector('code');
                    const language = codeElement?.className.replace('language-', '') || '';
                    // Restore original code (escaped)
                    pre.innerHTML = `<code id="code-content" class="language-${language}">${escapeHtml(originalCodeContent)}</code>`;
                    const newCodeBlock = pre.querySelector<HTMLElement>('#code-content');
                    if (newCodeBlock && window.hljs) {
                        // Re-apply highlighting
                        window.hljs.highlightElement(newCodeBlock);
                        if (window.hljs.lineNumbersBlock) {
                            window.hljs.lineNumbersBlock(newCodeBlock);
                        }
                    }
                }
            }
        }
    }

    // Update theme based on current site theme (light/dark)
    function updateHighlightTheme(): void {
        const currentSiteTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const preferredTheme = codeThemePreferences[currentSiteTheme as keyof CodeThemePreferences];
        switchHighlightTheme(preferredTheme);
    }

    // =============================================================================
    // Scroll Shadow Management
    // =============================================================================

    // Handle scroll shadows
    function updateScrollShadows(container: HTMLElement): void {
        const scrollTop = container.scrollTop;
        const scrollHeight = container.scrollHeight;
        const clientHeight = container.clientHeight;
        const scrollBottom = scrollHeight - scrollTop - clientHeight;

        // Add/remove classes based on scroll position
        if (scrollTop > 0) {
            container.classList.add('scrolled-top');
        } else {
            container.classList.remove('scrolled-top');
        }

        if (scrollBottom > 0) {
            container.classList.add('scrolled-bottom');
        } else {
            container.classList.remove('scrolled-bottom');
        }
    }

    // =============================================================================
    // Copy and Preview Functions
    // =============================================================================

    function copyToClipboard(): void {
        const fileContent = document.querySelector<HTMLElement>('.file-content');
        const markdownBody = document.querySelector<HTMLElement>('.markdown-body');
        const content = fileContent?.innerText || markdownBody?.innerText || '';

        navigator.clipboard.writeText(content).then(() => {
            const btn = event?.target as HTMLElement;
            if (!btn) return;

            const originalText = btn.innerHTML;
            const checkIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" class="octicon octicon-16" style="vertical-align: text-bottom; margin-right: 4px;"><path fill="currentColor" d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"></path></svg>';
            btn.innerHTML = `${checkIcon} Copied!`;
            setTimeout(() => { btn.innerHTML = originalText; }, 2000);
        }).catch(err => {
            alert('Failed to copy: ' + err);
        });
    }

    function showCode(): void {
        const markdownPreview = document.getElementById('markdownPreview') as HTMLElement | null;
        const markdownCode = document.getElementById('markdownCode') as HTMLElement | null;
        const codeBtn = document.getElementById('codeBtn') as HTMLElement | null;
        const previewBtn = document.getElementById('previewBtn') as HTMLElement | null;

        if (markdownPreview) markdownPreview.style.display = 'none';
        if (markdownCode) markdownCode.style.display = 'block';
        if (codeBtn) codeBtn.classList.add('active');
        if (previewBtn) previewBtn.classList.remove('active');
    }

    function showPreview(): void {
        const markdownPreview = document.getElementById('markdownPreview') as HTMLElement | null;
        const markdownCode = document.getElementById('markdownCode') as HTMLElement | null;
        const codeBtn = document.getElementById('codeBtn') as HTMLElement | null;
        const previewBtn = document.getElementById('previewBtn') as HTMLElement | null;

        if (markdownPreview) markdownPreview.style.display = 'block';
        if (markdownCode) markdownCode.style.display = 'none';
        if (codeBtn) codeBtn.classList.remove('active');
        if (previewBtn) previewBtn.classList.add('active');
    }

    // =============================================================================
    // Branch Selector
    // =============================================================================

    // Branch selector dropdown
    function toggleBranchDropdown(event: Event): void {
        event.stopPropagation();
        const dropdown = document.getElementById('branchDropdown') as HTMLElement | null;
        if (dropdown) {
            dropdown.classList.toggle('show');
        }
    }

    // Switch branch via API
    async function switchBranch(branch: string): Promise<void> {
        console.log('Switching to branch:', branch);

        const projectData = window.SCITEX_PROJECT_DATA;
        if (!projectData) return;

        try {
            // Call the branch switching API
            const response = await fetch(`/${projectData.owner}/${projectData.slug}/api/switch-branch/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') || ''
                },
                body: JSON.stringify({ branch: branch })
            });

            const data = await response.json() as BranchSwitchResponse;

            if (data.success) {
                // Reload page to show file from new branch
                window.location.reload();
            } else {
                alert('Failed to switch branch: ' + data.error);
            }
        } catch (error) {
            console.error('Error switching branch:', error);
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            alert('Failed to switch branch: ' + errorMessage);
        }
    }

    // =============================================================================
    // Event Listeners
    // =============================================================================

    // Initialize syntax highlighting with line numbers
    document.addEventListener('DOMContentLoaded', async function() {
        // Store original code content before highlighting
        const codeBlock = document.getElementById('code-content') as HTMLElement | null;
        if (codeBlock) {
            originalCodeContent = codeBlock.textContent;
        }

        // Load preferences from database
        await loadCodeThemePreferences();

        // Set initial theme
        updateHighlightTheme();

        // Apply highlighting
        if (codeBlock && window.hljs) {
            window.hljs.highlightElement(codeBlock);
            if (window.hljs.lineNumbersBlock) {
                window.hljs.lineNumbersBlock(codeBlock);
            }
        }

        // Setup scroll shadow handlers
        const fileContent = document.querySelector<HTMLElement>('.file-content');
        if (fileContent) {
            // Initial check
            updateScrollShadows(fileContent);

            // Update on scroll
            fileContent.addEventListener('scroll', function() {
                updateScrollShadows(fileContent);
            });

            // Update on resize
            window.addEventListener('resize', function() {
                updateScrollShadows(fileContent);
            });
        }

        // Listen for site theme changes (light/dark toggle)
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
                    const newSiteTheme = document.documentElement.getAttribute('data-theme') || 'dark';
                    const preferredTheme = codeThemePreferences[newSiteTheme as keyof CodeThemePreferences];

                    // Switch theme and re-highlight
                    switchHighlightTheme(preferredTheme, true);

                    console.log(`Site theme changed to ${newSiteTheme}, code theme: ${preferredTheme}`);
                }
            });
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(event: Event) {
        const dropdown = document.getElementById('branchDropdown') as HTMLElement | null;
        const branchSelector = document.querySelector<HTMLElement>('.branch-selector');

        if (dropdown && branchSelector && !branchSelector.contains(event.target as Node)) {
            dropdown.classList.remove('show');
        }
    });

    // =============================================================================
    // Expose Functions to Window
    // =============================================================================

    window.copyToClipboard = copyToClipboard;
    window.showCode = showCode;
    window.showPreview = showPreview;
    window.toggleBranchDropdown = toggleBranchDropdown;
    window.switchBranch = switchBranch;

})();
