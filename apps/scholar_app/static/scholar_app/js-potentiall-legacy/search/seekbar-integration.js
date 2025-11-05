/**
 * SciTeX Seekbar Integration for Scholar App
 *
 * This file provides integration between the SciTeX Seekbar component
 * and the Scholar app's existing filter system. It can work alongside
 * noUiSlider or replace it entirely.
 *
 * @version 1.0.0
 */

class ScholarSeekbarIntegration {
    constructor() {
        this.sliders = {};
        this.init();
    }

    init() {
        // Guard against multiple initializations
        if (window.__scholarSeekbarInitialized) {
            console.log('[ScholarSeekbar] Already initialized, skipping');
            return;
        }
        window.__scholarSeekbarInitialized = true;

        console.log('[ScholarSeekbar] Initializing seekbar integration...');

        // Check if we should use ScitexSeekbar or fall back to noUiSlider
        const useScitexSeekbar = document.querySelector('[data-use-scitex-seekbar="true"]');

        // Skip initialization if sliders are already initialized by noUiSlider
        if (document.getElementById('yearSlider')?.noUiSlider) {
            console.log('[ScholarSeekbar] noUiSlider already initialized, skipping ScitexSeekbar');
            return;
        }

        if (useScitexSeekbar && typeof ScitexSeekbar !== 'undefined') {
            this.initScitexSeekbars();
        } else if (typeof noUiSlider !== 'undefined') {
            console.log('[ScholarSeekbar] noUiSlider detected, keeping existing implementation');
        } else {
            console.warn('[ScholarSeekbar] No slider library found. Load either ScitexSeekbar or noUiSlider.');
        }
    }

    /**
     * Initialize SciTeX Seekbars for all filter ranges
     */
    initScitexSeekbars() {
        // Get URL parameters for initial values
        const urlParams = new URLSearchParams(window.location.search);

        // Year Slider
        this.initYearSlider(urlParams);

        // Citations Slider
        this.initCitationsSlider(urlParams);

        // Impact Factor Slider
        this.initImpactFactorSlider(urlParams);

        console.log('[ScholarSeekbar] All seekbars initialized successfully');
    }

    /**
     * Initialize Year Range Slider
     */
    initYearSlider(urlParams) {
        const container = document.getElementById('yearSlider');
        if (!container) return;

        const yearMin = parseInt(urlParams.get('year_from')) || 1900;
        const yearMax = parseInt(urlParams.get('year_to')) || 2025;

        // Replace existing container content
        container.innerHTML = '';
        container.classList.add('scitex-seekbar-container');

        this.sliders.year = new ScitexSeekbar(container, {
            min: 1900,
            max: 2025,
            valueMin: yearMin,
            valueMax: yearMax,
            step: 1,
            showValues: false, // Using badge display instead
            format: (value) => Math.round(value).toString(),
            onChange: (values) => {
                this.updateYearDisplay(values);
                this.updateHiddenInputs('year', values);
            },
            onUpdate: (values) => {
                this.updateYearDisplay(values);
            }
        });

        // Initial display update
        this.updateYearDisplay({ min: yearMin, max: yearMax });

        console.log('[ScholarSeekbar] Year slider initialized:', yearMin, '-', yearMax);
    }

    /**
     * Initialize Citations Range Slider
     */
    initCitationsSlider(urlParams) {
        const container = document.getElementById('citationsSlider');
        if (!container) return;

        const citationsMaxRange = parseInt(container.dataset.max) || 12000;
        const citationsMin = parseInt(urlParams.get('min_citations')) || 0;
        const citationsMax = parseInt(urlParams.get('max_citations')) || citationsMaxRange;

        // Replace existing container content
        container.innerHTML = '';
        container.classList.add('scitex-seekbar-container');

        this.sliders.citations = new ScitexSeekbar(container, {
            min: 0,
            max: citationsMaxRange,
            valueMin: citationsMin,
            valueMax: citationsMax,
            step: Math.max(1, Math.floor(citationsMaxRange / 100)),
            showValues: false,
            format: (value) => {
                const v = Math.round(value);
                if (v >= 10000) return (v / 1000).toFixed(0) + 'k';
                if (v >= 1000) return (v / 1000).toFixed(1) + 'k';
                return v.toString();
            },
            onChange: (values) => {
                this.updateCitationsDisplay(values);
                this.updateHiddenInputs('citations', values);
            },
            onUpdate: (values) => {
                this.updateCitationsDisplay(values);
            }
        });

        // Initial display update
        this.updateCitationsDisplay({ min: citationsMin, max: citationsMax });

        console.log('[ScholarSeekbar] Citations slider initialized:', citationsMin, '-', citationsMax);
    }

    /**
     * Initialize Impact Factor Range Slider
     */
    initImpactFactorSlider(urlParams) {
        const container = document.getElementById('impactFactorSlider');
        if (!container) return;

        const impactMaxRange = parseFloat(container.dataset.max) || 50.0;
        const impactMin = parseFloat(urlParams.get('min_impact_factor')) || 0;
        const impactMax = parseFloat(urlParams.get('max_impact_factor')) || impactMaxRange;

        // Replace existing container content
        container.innerHTML = '';
        container.classList.add('scitex-seekbar-container');

        this.sliders.impactFactor = new ScitexSeekbar(container, {
            min: 0,
            max: impactMaxRange,
            valueMin: impactMin,
            valueMax: impactMax,
            step: Math.max(0.1, impactMaxRange / 100),
            showValues: false,
            format: (value) => value.toFixed(1),
            onChange: (values) => {
                this.updateImpactFactorDisplay(values);
                this.updateHiddenInputs('impactFactor', values);
            },
            onUpdate: (values) => {
                this.updateImpactFactorDisplay(values);
            }
        });

        // Initial display update
        this.updateImpactFactorDisplay({ min: impactMin, max: impactMax });

        console.log('[ScholarSeekbar] Impact Factor slider initialized:', impactMin, '-', impactMax);
    }

    /**
     * Update year display badges
     */
    updateYearDisplay(values) {
        const minDisplay = document.getElementById('yearMinDisplay');
        const maxDisplay = document.getElementById('yearMaxDisplay');

        if (minDisplay) minDisplay.textContent = Math.round(values.min);
        if (maxDisplay) maxDisplay.textContent = Math.round(values.max);
    }

    /**
     * Update citations display badges
     */
    updateCitationsDisplay(values) {
        const minDisplay = document.getElementById('citationsMinDisplay');
        const maxDisplay = document.getElementById('citationsMaxDisplay');

        if (minDisplay) minDisplay.textContent = Math.round(values.min);
        if (maxDisplay) maxDisplay.textContent = Math.round(values.max);
    }

    /**
     * Update impact factor display badges
     */
    updateImpactFactorDisplay(values) {
        const minDisplay = document.getElementById('impactFactorMinDisplay');
        const maxDisplay = document.getElementById('impactFactorMaxDisplay');

        if (minDisplay) minDisplay.textContent = values.min.toFixed(1);
        if (maxDisplay) maxDisplay.textContent = values.max.toFixed(1);
    }

    /**
     * Update hidden form inputs
     */
    updateHiddenInputs(type, values) {
        switch (type) {
            case 'year':
                const yearFromInput = document.getElementById('yearFromInput');
                const yearToInput = document.getElementById('yearToInput');
                if (yearFromInput) yearFromInput.value = Math.round(values.min);
                if (yearToInput) yearToInput.value = Math.round(values.max);
                break;

            case 'citations':
                const citationsMinInput = document.getElementById('citationsMinInput');
                const citationsMaxInput = document.getElementById('citationsMaxInput');
                if (citationsMinInput) citationsMinInput.value = Math.round(values.min);
                if (citationsMaxInput) citationsMaxInput.value = Math.round(values.max);
                break;

            case 'impactFactor':
                const impactMinInput = document.getElementById('impactFactorMinInput');
                const impactMaxInput = document.getElementById('impactFactorMaxInput');
                if (impactMinInput) impactMinInput.value = values.min.toFixed(1);
                if (impactMaxInput) impactMaxInput.value = values.max.toFixed(1);
                break;
        }
    }

    /**
     * Get current slider values
     */
    getValues(sliderName) {
        if (this.sliders[sliderName]) {
            return this.sliders[sliderName].getValues();
        }
        return null;
    }

    /**
     * Set slider values programmatically
     */
    setValues(sliderName, min, max) {
        if (this.sliders[sliderName]) {
            this.sliders[sliderName].setValues(min, max);
        }
    }

    /**
     * Reset all sliders to default
     */
    resetAll() {
        Object.keys(this.sliders).forEach(key => {
            if (this.sliders[key]) {
                this.sliders[key].reset();
            }
        });
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if ScitexSeekbar is available and requested
    if (typeof ScitexSeekbar !== 'undefined') {
        window.scholarSeekbar = new ScholarSeekbarIntegration();
    }
});
