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
     * Get the current theme preference from localStorage
     */
    function getThemePreference() {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored && [THEME_LIGHT, THEME_DARK].includes(stored)) {
            return stored;
        }
        return THEME_LIGHT; // Default to light theme
    }

    /**
     * Apply theme to the document
     */
    function applyTheme(theme) {
        if (theme === THEME_DARK) {
            document.documentElement.setAttribute('data-theme', 'dark');
            document.documentElement.setAttribute('data-color-mode', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
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
    }

    /**
     * Toggle between themes: light <-> dark
     */
    function toggleTheme() {
        const current = getThemePreference();
        const next = current === THEME_LIGHT ? THEME_DARK : THEME_LIGHT;
        setThemePreference(next);
    }

    /**
     * Update the toggle button appearance
     */
    function updateToggleButton() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (!toggleBtn) return;

        const theme = getThemePreference();

        // Update title/aria-label
        const labels = {
            [THEME_LIGHT]: '☀️ Light',
            [THEME_DARK]: '🌙 Dark'
        };

        toggleBtn.setAttribute('title', `Theme: ${labels[theme]}\nClick to toggle theme`);
        toggleBtn.setAttribute('aria-label', `Current theme: ${labels[theme]}`);

        // Update button content
        const icons = {
            [THEME_LIGHT]: '☀️',
            [THEME_DARK]: '🌙'
        };

        toggleBtn.innerHTML = icons[theme];
    }

    /**
     * Initialize theme on page load
     */
    function initTheme() {
        // Apply theme immediately to prevent flash
        const theme = getThemePreference();
        applyTheme(theme);

        // Set up toggle button when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            const toggleBtn = document.getElementById('theme-toggle');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', toggleTheme);
                updateToggleButton();
            }
        });
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
