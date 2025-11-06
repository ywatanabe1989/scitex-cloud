"use strict";
/**

 * SciTeX Scholar Main Index - Core Functionality
 *
 * This is the main entry point for the Scholar app, handling search, filters, results display,
 * source selection, BibTeX management, and all core user interactions.
 *
 * @version 1.0.0
 */
// Window interface extensions
console.log("[DEBUG] apps/scholar_app/static/scholar_app/ts/common/scholar-index-main.ts loaded");
/**
 * Reset BibTeX form to initial state
 */
function resetBibtexForm() {
    const formArea = document.getElementById('bibtexFormArea');
    const progressArea = document.getElementById('bibtexProgressArea');
    const form = document.getElementById('bibtexEnrichmentForm');
    if (formArea)
        formArea.style.display = 'block';
    if (progressArea)
        progressArea.style.display = 'none';
    if (form)
        form.reset();
}
// Document ready initialization
document.addEventListener('DOMContentLoaded', function () {
    console.log('[Scholar Index Main] Initializing...');
    // Simple search functionality
    const searchForm = document.querySelector('form');
    const searchInput = document.querySelector('input[name="q"]');
    const searchButton = document.getElementById('searchButton');
    const progressiveLoadingStatus = document.getElementById('progressiveLoadingStatus');
    const progressiveResults = document.getElementById('progressiveResults');
    // Advanced filters functionality
    const toggleAdvancedFilters = document.getElementById('toggleAdvancedFilters');
    const advancedFilters = document.getElementById('advancedFilters');
    const clearFiltersBtn = document.getElementById('clearFilters');
    const saveSearchBtn = document.getElementById('saveSearch');
    // Toggle advanced filters
    if (toggleAdvancedFilters && advancedFilters) {
        toggleAdvancedFilters.addEventListener('click', function () {
            if (advancedFilters.style.display === 'none') {
                advancedFilters.style.display = 'block';
                this.innerHTML = '<i class="fas fa-sliders-h"></i> Hide Advanced Filters';
                this.style.backgroundColor = 'var(--primary-color, #1a2332)';
                this.style.color = 'white';
                this.style.borderColor = 'var(--primary-color, #1a2332)';
            }
            else {
                advancedFilters.style.display = 'none';
                this.innerHTML = '<i class="fas fa-sliders-h"></i> Advanced Filters';
                this.style.backgroundColor = 'transparent';
                this.style.color = 'var(--primary-color, #1a2332)';
                this.style.borderColor = 'var(--primary-color, #1a2332)';
            }
        });
    }
    // Clear all filters
    if (clearFiltersBtn && advancedFilters) {
        clearFiltersBtn.addEventListener('click', function () {
            // Reset all filter inputs
            document.querySelectorAll('#advancedFilters input, #advancedFilters select').forEach(input => {
                const el = input;
                if (el.type === 'checkbox' || el.type === 'radio') {
                    el.checked = false;
                }
                else {
                    el.value = '';
                }
            });
            // Reset basic filters
            document.querySelectorAll('#basicFilters input[type="checkbox"]').forEach(input => {
                input.checked = false;
            });
            // Reset source toggles to all enabled
            document.querySelectorAll('.source-toggle').forEach(toggle => {
                toggle.checked = true;
            });
            saveSourcePreferences();
            updateActiveFilterCount();
        });
    }
    // Save search functionality
    if (saveSearchBtn && searchInput) {
        saveSearchBtn.addEventListener('click', function () {
            const query = searchInput.value.trim();
            const searchName = prompt('Enter a name for this saved search:', query.substring(0, 50));
            if (!searchName)
                return;
            // Collect all active filters
            const filters = {};
            document.querySelectorAll('#advancedFilters input, #advancedFilters select, #basicFilters input[type="checkbox"]:checked').forEach(input => {
                const el = input;
                if (el.name && el.value) {
                    filters[el.name] = el.value;
                }
            });
            // Save to backend
            fetch('/scholar/api/save-search/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') || ''
                },
                body: JSON.stringify({
                    name: searchName,
                    query: query,
                    filters: filters
                })
            })
                .then(response => response.json())
                .then((data) => {
                if (data.status === 'success') {
                    alert('Search saved successfully!');
                }
                else {
                    alert(data.message || 'Error saving search');
                }
            })
                .catch((error) => {
                console.error('Error:', error);
                alert('Error saving search. Please try again.');
            });
        });
    }
    // Update active filter count
    function updateActiveFilterCount() {
        let count = 0;
        // Count advanced filters
        document.querySelectorAll('#advancedFilters input, #advancedFilters select').forEach(input => {
            const el = input;
            if (el.name && el.value) {
                if ((el.type === 'checkbox' && el.checked) ||
                    (el.type !== 'checkbox' && el.type !== 'radio')) {
                    count++;
                }
            }
        });
        // Count basic filters
        document.querySelectorAll('#basicFilters input[type="checkbox"]:checked:not(.source-toggle)').forEach(() => count++);
        // Count enabled sources
        const totalSources = document.querySelectorAll('.source-toggle').length;
        const enabledSources = document.querySelectorAll('.source-toggle:checked').length;
        if (enabledSources < totalSources && enabledSources > 0) {
            count++;
        }
        const activeFilterCountEl = document.getElementById('activeFilterCount');
        if (activeFilterCountEl) {
            activeFilterCountEl.textContent = count.toString();
        }
    }
    // Source preference management with database/localStorage
    function saveSourcePreferences() {
        const preferences = {};
        document.querySelectorAll('.source-toggle').forEach(toggle => {
            const el = toggle;
            preferences[el.value] = el.checked;
        });
        // Save to database if user is logged in, otherwise use localStorage
        if (window.scholarConfig && window.scholarConfig.user && window.scholarConfig.user.isAuthenticated) {
            fetch('/scholar/api/preferences/sources/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ sources: preferences })
            })
                .then(response => response.json())
                .then((data) => {
                if (data.status === 'success') {
                    console.log('Source preferences saved to profile');
                }
            })
                .catch((error) => console.error('Error saving preferences:', error));
        }
        else {
            // For anonymous users, use localStorage
            localStorage.setItem('scholar_source_preferences', JSON.stringify(preferences));
        }
    }
    // Make saveSourcePreferences available globally
    window.saveSourcePreferences = saveSourcePreferences;
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
            getCookie('csrftoken') || '';
    }
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            const lastPart = parts.pop();
            if (lastPart) {
                return lastPart.split(';').shift() || null;
            }
        }
        return null;
    }
    // Update source display text based on selected checkboxes
    function updateSourceDisplay() {
        const selectedSources = document.querySelectorAll('.source-toggle:checked');
        const sourceDisplay = document.getElementById('sourceDisplay');
        if (sourceDisplay) {
            const sourceNames = [];
            selectedSources.forEach(checkbox => {
                switch (checkbox.value) {
                    case 'pubmed':
                        sourceNames.push('PubMed');
                        break;
                    case 'google_scholar':
                        sourceNames.push('Google Scholar');
                        break;
                    case 'arxiv':
                        sourceNames.push('arXiv');
                        break;
                    case 'semantic':
                        sourceNames.push('Semantic Scholar');
                        break;
                }
            });
            let displayText = '';
            if (sourceNames.length === 0) {
                displayText = 'from no sources selected (ERROR: please select at least one source)';
            }
            else if (sourceNames.length === 4) {
                displayText = 'from all external sources: PubMed, Google Scholar, arXiv, Semantic Scholar + SciTeX Index';
            }
            else if (sourceNames.length === 1) {
                displayText = `from ${sourceNames[0]} + SciTeX Index`;
            }
            else {
                displayText = `from ${sourceNames.join(', ')} + SciTeX Index`;
            }
            sourceDisplay.textContent = displayText;
        }
    }
    function loadSourcePreferences() {
        if (window.scholarConfig && window.scholarConfig.user && window.scholarConfig.user.isAuthenticated) {
            // Load from database for logged-in users
            fetch('/scholar/api/preferences/')
                .then(response => response.json())
                .then((data) => {
                if (data.status === 'success' && data.preferences.preferred_sources) {
                    const preferences = data.preferences.preferred_sources;
                    applySourcePreferences(preferences);
                }
                else {
                    setDefaultSourcePreferences();
                }
            })
                .catch((error) => {
                console.log('Could not load user preferences, using localStorage fallback');
                loadSourcePreferencesFromStorage();
            });
        }
        else {
            // Load from localStorage for anonymous users
            loadSourcePreferencesFromStorage();
        }
    }
    function loadSourcePreferencesFromStorage() {
        const saved = localStorage.getItem('scholar_source_preferences');
        if (saved) {
            try {
                const preferences = JSON.parse(saved);
                applySourcePreferences(preferences);
            }
            catch (e) {
                console.log('Could not load source preferences from localStorage');
                setDefaultSourcePreferences();
            }
        }
        else {
            setDefaultSourcePreferences();
        }
    }
    function applySourcePreferences(preferences) {
        let hasAnyPreference = false;
        document.querySelectorAll('.source-toggle').forEach(toggle => {
            const el = toggle;
            if (preferences.hasOwnProperty(el.value)) {
                el.checked = preferences[el.value];
                hasAnyPreference = true;
            }
        });
        if (!hasAnyPreference) {
            setDefaultSourcePreferences();
        }
        updateAllSourcesToggle();
        updateSourceDisplay();
        updateActiveFilterCount();
    }
    function setDefaultSourcePreferences() {
        // Default: All sources enabled
        document.querySelectorAll('.source-toggle').forEach(toggle => {
            toggle.checked = true;
        });
        updateAllSourcesToggle();
        updateSourceDisplay();
        updateActiveFilterCount();
    }
    // Enhanced source toggle logic with "All Sources" master toggle
    function initializeSourceToggles() {
        const allSourcesToggle = document.getElementById('source_all_toggle');
        const sourceToggles = document.querySelectorAll('.source-toggle');
        // Master "All Sources" toggle functionality
        if (allSourcesToggle) {
            allSourcesToggle.addEventListener('change', function () {
                const isChecked = this.checked;
                sourceToggles.forEach(toggle => {
                    toggle.checked = isChecked;
                });
                handleSourceChange();
            });
        }
        // Individual source toggle functionality
        sourceToggles.forEach(toggle => {
            toggle.addEventListener('change', function () {
                updateAllSourcesToggle();
                handleSourceChange();
            });
        });
        // Initial state check
        updateAllSourcesToggle();
    }
    function updateAllSourcesToggle() {
        const allSourcesToggle = document.getElementById('source_all_toggle');
        const sourceToggles = document.querySelectorAll('.source-toggle');
        const checkedToggles = document.querySelectorAll('.source-toggle:checked');
        if (allSourcesToggle) {
            if (checkedToggles.length === sourceToggles.length) {
                allSourcesToggle.checked = true;
                allSourcesToggle.indeterminate = false;
            }
            else if (checkedToggles.length === 0) {
                allSourcesToggle.checked = false;
                allSourcesToggle.indeterminate = false;
            }
            else {
                allSourcesToggle.checked = false;
                allSourcesToggle.indeterminate = true;
            }
        }
    }
    function handleSourceChange() {
        saveSourcePreferences();
        updateActiveFilterCount();
        updateSourceDisplay();
        // Auto-submit search if there's a query
        if (searchInput && searchInput.value.trim()) {
            const autoSubmitForm = document.querySelector('form');
            if (autoSubmitForm) {
                autoSubmitForm.submit();
            }
        }
    }
    // Initialize source toggles
    initializeSourceToggles();
    // Load source preferences on page load
    loadSourcePreferences();
    // Force reload preferences after a brief delay to ensure DOM is ready
    setTimeout(() => {
        loadSourcePreferences();
    }, 200);
    // Monitor filter changes
    document.querySelectorAll('#advancedFilters input, #advancedFilters select, #basicFilters input').forEach(input => {
        input.addEventListener('change', updateActiveFilterCount);
        input.addEventListener('input', updateActiveFilterCount);
    });
    // Initial filter count and source display
    updateActiveFilterCount();
    updateSourceDisplay();
    // Auto-submit on filter changes
    document.querySelectorAll('#basicFilters input[type="checkbox"]:not(.source-toggle)').forEach(input => {
        input.addEventListener('change', function () {
            if (searchInput && searchInput.value.trim() && searchForm) {
                searchForm.submit();
            }
        });
    });
    // Sort functionality
    if (!window._scholarSortInitialized) {
        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect && !sortSelect._listenerAttached) {
            sortSelect.addEventListener('change', function () {
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('sort_by', this.value);
                window.location.href = currentUrl.toString();
            });
            sortSelect._listenerAttached = true;
        }
        window._scholarSortInitialized = true;
    }
    // Helper function to reset all progress indicators
    function resetProgressIndicators() {
        document.querySelectorAll('.progress-source').forEach(source => {
            const badge = source.querySelector('.badge');
            const spinner = source.querySelector('.spinner-border');
            const count = source.querySelector('.count');
            if (badge)
                badge.className = 'badge bg-light';
            if (spinner)
                spinner.style.display = 'none';
            if (count)
                count.textContent = '-';
        });
    }
    // Auto-submit when project filter changes
    document.querySelectorAll('select[name="project"]').forEach(select => {
        select.addEventListener('change', function () {
            if (searchInput && searchInput.value.trim() && searchForm) {
                searchForm.submit();
            }
        });
    });
    // Handle abstract toggle functionality
    document.querySelectorAll('.abstract-toggle').forEach(toggle => {
        toggle.addEventListener('click', function (e) {
            e.preventDefault();
            const abstractPreview = this.closest('.abstract-preview');
            if (!abstractPreview)
                return;
            const shortAbstract = abstractPreview.querySelector('.abstract-short');
            const fullAbstract = abstractPreview.querySelector('.abstract-full');
            if (fullAbstract && shortAbstract && fullAbstract.style.display === 'none') {
                shortAbstract.style.display = 'none';
                fullAbstract.style.display = 'inline';
                this.textContent = '[Show less]';
            }
            else if (fullAbstract && shortAbstract) {
                shortAbstract.style.display = 'inline';
                fullAbstract.style.display = 'none';
                this.textContent = '[Show full abstract]';
            }
        });
    });
    // BibTeX Job Status Polling (moved here from bibtex-enrichment for completeness)
    function pollBibtexJobStatus(jobId, attempts = 0) {
        // This function is now defined in bibtex-enrichment.ts
        // Keeping reference here for backwards compatibility
        console.log('[Scholar Index Main] pollBibtexJobStatus called with jobId:', jobId);
    }
    // Global Abstract Toggle Management
    const savedMode = localStorage.getItem('global_abstract_mode') || 'truncated';
    // Set initial button state
    const toggleButtons = document.querySelectorAll('.global-abstract-toggle');
    toggleButtons.forEach(btn => {
        if (btn.dataset.mode === savedMode) {
            btn.classList.remove('btn-outline-secondary');
            btn.classList.add('btn-primary');
        }
    });
    // Apply saved mode to all existing abstracts
    applyGlobalAbstractMode(savedMode);
    // Add click handlers to toggle buttons
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const mode = this.dataset.mode || 'truncated';
            // Update button states
            toggleButtons.forEach(b => {
                b.classList.remove('btn-primary');
                b.classList.add('btn-outline-secondary');
            });
            this.classList.remove('btn-outline-secondary');
            this.classList.add('btn-primary');
            // Save mode and apply it
            localStorage.setItem('global_abstract_mode', mode);
            applyGlobalAbstractMode(mode);
        });
    });
    // Function to apply global abstract mode to all papers
    function applyGlobalAbstractMode(mode) {
        const abstracts = document.querySelectorAll('.abstract-preview');
        abstracts.forEach(abstract => {
            abstract.classList.remove('mode-all', 'mode-truncated', 'mode-none');
            abstract.classList.add('mode-' + mode);
        });
    }
    console.log('[Scholar Index Main] Initialization complete');
});
// Global functions for file handling (exposed to window for onclick handlers)
window.viewOnWeb = function (link, event) {
    if (event.ctrlKey || event.metaKey || event.button === 1 || event.button === 2) {
        return true;
    }
    event.preventDefault();
    const resultCard = link.closest('.result-card');
    if (!resultCard)
        return false;
    const paperTitle = resultCard.dataset.title || '';
    const doi = resultCard.dataset.doi;
    const pmid = resultCard.dataset.pmid;
    const arxivId = resultCard.dataset.arxivId;
    const externalUrl = resultCard.dataset.externalUrl;
    const urls = [];
    if (doi && doi.trim()) {
        urls.push({ type: 'DOI', url: `https://doi.org/${doi}` });
    }
    if (pmid && pmid.trim()) {
        urls.push({ type: 'PubMed', url: `https://pubmed.ncbi.nlm.nih.gov/${pmid}/` });
    }
    if (arxivId && arxivId.trim()) {
        urls.push({ type: 'arXiv', url: `https://arxiv.org/abs/${arxivId}` });
    }
    if (externalUrl && externalUrl.trim() && !externalUrl.includes('doi.org')) {
        urls.push({ type: 'External', url: externalUrl });
    }
    if (urls.length === 0) {
        urls.push({
            type: 'Google Scholar',
            url: `https://scholar.google.com/scholar?q=${encodeURIComponent(paperTitle)}`
        });
    }
    urls.forEach(item => {
        window.open(item.url, '_blank');
    });
    return false;
};
// Helper function to show toast notifications
window.showToast = function (message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 3000);
};
// Helper function to get cookie
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
// Export getCookie globally for use in other modules
window.getCookie = getCookie;
//# sourceMappingURL=scholar-index-main.js.map