/**
 * SciTeX Theme Switcher
 * Handles Light/Dark/System mode switching with localStorage persistence
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'scitex-theme-preference';
    const THEME_LIGHT = 'light';
    const THEME_DARK = 'dark';
    const THEME_SYSTEM = 'system';

    /**
     * Get system theme preference
     */
    function getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return THEME_DARK;
        }
        return THEME_LIGHT;
    }

    /**
     * Get the current theme preference from localStorage
     */
    function getThemePreference() {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored && [THEME_LIGHT, THEME_DARK, THEME_SYSTEM].includes(stored)) {
            return stored;
        }
        return THEME_SYSTEM; // Default to system preference
    }

    /**
     * Get the effective theme to apply (resolves 'system' to actual theme)
     */
    function getEffectiveTheme() {
        const preference = getThemePreference();
        if (preference === THEME_SYSTEM) {
            return getSystemTheme();
        }
        return preference;
    }

    /**
     * Apply theme to the document
     */
    function applyTheme(effectiveTheme) {
        if (effectiveTheme === THEME_DARK) {
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
        const effectiveTheme = getEffectiveTheme();
        applyTheme(effectiveTheme);
    }

    /**
     * Cycle through themes: light -> dark -> system -> light...
     */
    function cycleTheme() {
        const current = getThemePreference();
        let next;

        if (current === THEME_LIGHT) {
            next = THEME_DARK;
        } else if (current === THEME_DARK) {
            next = THEME_SYSTEM;
        } else {
            next = THEME_LIGHT;
        }

        setThemePreference(next);
    }

    /**
     * Update the toggle button appearance
     */
    function updateToggleButton() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (!toggleBtn) return;

        const preference = getThemePreference();
        const effectiveTheme = getEffectiveTheme();

        // Update title/aria-label with all three options
        const labels = {
            [THEME_LIGHT]: '☀️ Light',
            [THEME_DARK]: '🌙 Dark',
            [THEME_SYSTEM]: '💻 System'
        };

        toggleBtn.setAttribute('title', `Theme: ${labels[preference]}\nClick to cycle: Light → Dark → System`);
        toggleBtn.setAttribute('aria-label', `Current theme: ${labels[preference]}`);

        // Update button content
        const icons = {
            [THEME_LIGHT]: '☀️',
            [THEME_DARK]: '🌙',
            [THEME_SYSTEM]: '💻'
        };

        toggleBtn.innerHTML = icons[preference];
    }

    /**
     * Initialize theme on page load
     */
    function initTheme() {
        // Apply theme immediately to prevent flash
        const effectiveTheme = getEffectiveTheme();
        applyTheme(effectiveTheme);

        // Set up toggle button when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            const toggleBtn = document.getElementById('theme-toggle');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', cycleTheme);
                updateToggleButton();
            }
        });

        // Listen for system theme changes (only if using system preference)
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
                // Only auto-switch if user is using system preference
                if (getThemePreference() === THEME_SYSTEM) {
                    const newEffectiveTheme = e.matches ? THEME_DARK : THEME_LIGHT;
                    applyTheme(newEffectiveTheme);
                }
            });
        }
    }

    // Initialize immediately (before DOM loads to prevent flash)
    initTheme();

    // Expose API for manual control and settings page
    window.SciTeX = window.SciTeX || {};
    window.SciTeX.theme = {
        cycle: cycleTheme,
        set: setThemePreference,
        getPreference: getThemePreference,
        getEffective: getEffectiveTheme,
        LIGHT: THEME_LIGHT,
        DARK: THEME_DARK,
        SYSTEM: THEME_SYSTEM
    };

})();
