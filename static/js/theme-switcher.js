/**
 * SciTeX Theme Switcher
 * Handles Light/Dark mode switching with localStorage persistence
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'scitex-theme-preference';
    const THEME_LIGHT = 'light';
    const THEME_DARK = 'dark';

    /**
     * Get the current theme preference from localStorage or database
     */
    function getThemePreference() {
        const stored = localStorage.getItem(STORAGE_KEY);

        // Migration: Clean up old 'auto' or 'system' values from previous implementation
        if (stored && !['light', 'dark'].includes(stored)) {
            console.log(`Migrating invalid theme value: "${stored}" → "light"`);
            localStorage.setItem(STORAGE_KEY, THEME_LIGHT);
            return THEME_LIGHT;
        }

        if (stored && [THEME_LIGHT, THEME_DARK].includes(stored)) {
            return stored;
        }
        return THEME_DARK; // Default to dark theme for new visitors
    }

    /**
     * Load theme preference from database (for authenticated users)
     */
    async function loadThemeFromDatabase() {
        try {
            const response = await fetch('/auth/api/get-theme/');
            const data = await response.json();
            if (data.theme) {
                return data.theme;
            }
        } catch (error) {
            console.warn('Failed to load theme from database:', error);
        }
        return null;
    }

    /**
     * Save theme preference to database (for authenticated users)
     */
    async function saveThemeToDatabase(theme) {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            const response = await fetch('/auth/api/save-theme/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || getCookie('csrftoken')
                },
                body: JSON.stringify({ theme: theme })
            });
            const data = await response.json();
            if (data.success) {
                console.log('Theme saved to database:', theme);
            }
        } catch (error) {
            console.warn('Failed to save theme to database:', error);
        }
    }

    /**
     * Helper function to get CSRF token from cookies
     */
    function getCookie(name) {
        let cookieValue = null;
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

    /**
     * Apply theme to the document
     */
    function applyTheme(theme) {
        if (theme === THEME_DARK) {
            document.documentElement.setAttribute('data-theme', 'dark');
            document.documentElement.setAttribute('data-color-mode', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            document.documentElement.setAttribute('data-color-mode', 'light');
        }

        // Update toggle button if exists
        updateToggleButton();
    }

    /**
     * Set theme preference and apply
     */
    function setThemePreference(preference) {
        localStorage.setItem(STORAGE_KEY, preference);
        applyTheme(preference);
        // Save to database for authenticated users (async, don't wait)
        saveThemeToDatabase(preference);
    }

    /**
     * Toggle between themes: light <-> dark
     */
    function toggleTheme() {
        const current = getThemePreference();
        const next = current === THEME_LIGHT ? THEME_DARK : THEME_LIGHT;
        console.log(`Theme toggle: ${current} → ${next}`);
        setThemePreference(next);
    }

    /**
     * Update the toggle button appearance
     */
    function updateToggleButton() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (!toggleBtn) return;

        const theme = getThemePreference();

        // Update aria-label (accessibility)
        const labels = {
            [THEME_LIGHT]: '☀️ Light',
            [THEME_DARK]: '🌙 Dark'
        };

        // Note: title attribute removed to avoid duplicate tooltips with data-tooltip
        toggleBtn.setAttribute('aria-label', `Current theme: ${labels[theme]}`);

        // Update button content
        const icons = {
            [THEME_LIGHT]: '☀️',
            [THEME_DARK]: '🌙'
        };

        toggleBtn.innerHTML = icons[theme];
    }

    /**
     * Set up toggle button (call when DOM is ready)
     */
    function setupToggleButton() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            console.log('✓ Theme toggle button found, attaching click handler');
            toggleBtn.addEventListener('click', function(e) {
                console.log('✓ Theme toggle clicked');
                toggleTheme();
            });
            updateToggleButton();
        } else {
            console.warn('✗ Theme toggle button NOT found');
        }
    }

    /**
     * Initialize theme on page load
     */
    async function initTheme() {
        // Try to load from database first (for authenticated users)
        const dbTheme = await loadThemeFromDatabase();
        let theme;

        if (dbTheme) {
            // Use database theme and sync to localStorage
            theme = dbTheme;
            localStorage.setItem(STORAGE_KEY, dbTheme);
        } else {
            // Fallback to localStorage
            theme = getThemePreference();
        }

        // Apply theme immediately to prevent flash
        applyTheme(theme);

        // Set up toggle button - handle both pre-loaded and post-loaded states
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setupToggleButton);
        } else {
            // DOM already loaded
            setupToggleButton();
        }
    }

    // Initialize immediately (before DOM loads to prevent flash)
    initTheme();

    // Expose API for manual control and settings page
    window.SciTeX = window.SciTeX || {};
    window.SciTeX.theme = {
        toggle: toggleTheme,
        set: setThemePreference,
        get: getThemePreference,
        LIGHT: THEME_LIGHT,
        DARK: THEME_DARK
    };

})();
