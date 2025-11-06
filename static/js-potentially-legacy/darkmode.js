/**
 * SciTeX Dark Mode
 * 
 * This script handles dark mode functionality for the SciTeX website.
 * It detects user preference, saves settings to localStorage, and
 * provides toggle functionality.
 */

(function() {
    // DOM elements
    let darkModeToggle;
    
    // Dark mode state
    const darkModeState = {
        isDark: false,
        userPreference: 'auto', // 'dark', 'light', or 'auto'
        
        // Get stored preference or detect OS setting
        init() {
            // Check localStorage for saved preference
            const savedPreference = localStorage.getItem('scitex-theme-preference');
            if (savedPreference) {
                this.userPreference = savedPreference;
            }
            
            // Apply the preference
            this.applyPreference();
            
            // Watch for OS preference changes
            if (window.matchMedia) {
                const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
                mediaQuery.addEventListener('change', () => {
                    if (this.userPreference === 'auto') {
                        this.applyPreference();
                    }
                });
            }
        },
        
        // Toggle dark mode
        toggle() {
            if (this.userPreference === 'auto') {
                // If auto, toggle between light and dark
                this.userPreference = this.isDark ? 'light' : 'dark';
            } else {
                // Toggle between current mode and auto
                this.userPreference = this.userPreference === 'dark' ? 'light' : 'dark';
            }
            
            // Save the preference
            localStorage.setItem('scitex-theme-preference', this.userPreference);
            
            // Apply the preference
            this.applyPreference();
            
            // Update toggle button text
            this.updateToggleText();
        },
        
        // Apply the current preference
        applyPreference() {
            if (this.userPreference === 'auto') {
                // If auto, use OS preference
                this.isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            } else {
                // Otherwise use user preference
                this.isDark = this.userPreference === 'dark';
            }
            
            // Apply dark mode
            if (this.isDark) {
                document.documentElement.classList.add('dark-mode');
            } else {
                document.documentElement.classList.remove('dark-mode');
            }
            
            // Update toggle text when initialized
            if (darkModeToggle) {
                this.updateToggleText();
            }
        },
        
        // Update toggle button text
        updateToggleText() {
            if (!darkModeToggle) return;
            
            const toggleIcon = darkModeToggle.querySelector('i');
            if (this.isDark) {
                toggleIcon.className = 'fas fa-sun';
                darkModeToggle.setAttribute('title', 'Switch to light mode');
                darkModeToggle.setAttribute('aria-label', 'Switch to light mode');
            } else {
                toggleIcon.className = 'fas fa-moon';
                darkModeToggle.setAttribute('title', 'Switch to dark mode');
                darkModeToggle.setAttribute('aria-label', 'Switch to dark mode');
            }
        }
    };
    
    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        // Create dark mode toggle button
        createDarkModeToggle();
        
        // Initialize dark mode
        darkModeState.init();
    });
    
    // Create dark mode toggle in header
    function createDarkModeToggle() {
        // Create the toggle button
        darkModeToggle = document.createElement('button');
        darkModeToggle.className = 'dark-mode-toggle';
        darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        darkModeToggle.setAttribute('aria-label', 'Toggle dark mode');
        
        // Add toggle functionality
        darkModeToggle.addEventListener('click', () => {
            darkModeState.toggle();
        });
        
        // Find header actions or create a container
        const headerActions = document.querySelector('.header-actions');
        if (headerActions) {
            // Insert before the first element in header-actions
            headerActions.insertBefore(darkModeToggle, headerActions.firstChild);
        } else {
            // If no header actions, add to body for now
            document.body.appendChild(darkModeToggle);
        }
    }
})();