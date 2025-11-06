"use strict";
/**

 * noUiSlider Initialization for SciTeX Scholar Filters
 *
 * This file initializes dual-range sliders using the noUiSlider library for filtering
 * scholarly papers by year, citations, and impact factor. The sliders read their initial
 * values from URL parameters and update hidden form inputs when changed.
 *
 * External library: noUiSlider (requires `any` types or @ts-ignore)
 *
 * @version 1.0.0
 */
// @ts-ignore - noUiSlider library types
console.log("[DEBUG] apps/scholar_app/static/scholar_app/ts/search/nouislider-init.ts loaded");
// Guard against multiple initializations
if (window.__nouisliderInitialized) {
    console.log('[noUiSlider] Already initialized, skipping');
}
else {
    window.__nouisliderInitialized = true;
    document.addEventListener('DOMContentLoaded', function () {
        console.log('[noUiSlider] Initializing dual-range sliders...');
        // Get URL parameters for initial values
        const urlParams = new URLSearchParams(window.location.search);
        // ============================================
        // Year Slider (dynamic range from data attributes)
        // ============================================
        const yearSlider = document.getElementById('yearSlider');
        if (yearSlider && !yearSlider.noUiSlider) {
            try {
                const yearMinRange = parseInt(yearSlider.dataset.min || '1900');
                const yearMaxRange = parseInt(yearSlider.dataset.max || '2025');
                const yearMin = parseInt(urlParams.get('year_from') || '') || yearMinRange;
                const yearMax = parseInt(urlParams.get('year_to') || '') || yearMaxRange;
                // @ts-ignore - noUiSlider library
                noUiSlider.create(yearSlider, {
                    start: [yearMin, yearMax],
                    connect: true,
                    range: {
                        'min': yearMinRange,
                        'max': yearMaxRange
                    },
                    step: 1,
                    format: {
                        to: function (value) {
                            return Math.round(value);
                        },
                        from: function (value) {
                            return Math.round(value);
                        }
                    }
                });
                // Sync slider to hidden inputs and display badges
                yearSlider.noUiSlider.on('update', function (values, handle) {
                    const minValue = values[0];
                    const maxValue = values[1];
                    const yearFromInput = document.getElementById('yearFromInput');
                    const yearToInput = document.getElementById('yearToInput');
                    const yearMinDisplay = document.getElementById('yearMinDisplay');
                    const yearMaxDisplay = document.getElementById('yearMaxDisplay');
                    if (yearFromInput)
                        yearFromInput.value = minValue;
                    if (yearToInput)
                        yearToInput.value = maxValue;
                    if (yearMinDisplay)
                        yearMinDisplay.textContent = minValue;
                    if (yearMaxDisplay)
                        yearMaxDisplay.textContent = maxValue;
                });
                console.log('[noUiSlider] Year slider initialized:', yearMin, '-', yearMax, '(range:', yearMinRange, '-', yearMaxRange + ')');
            }
            catch (e) {
                console.warn('[noUiSlider] Year slider initialization error:', e.message);
            }
        }
        // ============================================
        // Citations Slider (dynamic max from data attribute)
        // ============================================
        const citationsSlider = document.getElementById('citationsSlider');
        if (citationsSlider && !citationsSlider.noUiSlider) {
            try {
                const citationsMin = parseInt(urlParams.get('min_citations') || '0') || 0;
                const citationsMaxRange = parseInt(citationsSlider.dataset.max || '12000') || 12000;
                const citationsMax = parseInt(urlParams.get('max_citations') || '') || citationsMaxRange;
                // @ts-ignore - noUiSlider library
                noUiSlider.create(citationsSlider, {
                    start: [citationsMin, citationsMax],
                    connect: true,
                    range: {
                        'min': 0,
                        'max': citationsMaxRange
                    },
                    step: Math.max(1, Math.floor(citationsMaxRange / 100)),
                    format: {
                        to: function (value) {
                            return Math.round(value);
                        },
                        from: function (value) {
                            return Math.round(value);
                        }
                    }
                });
                // Sync slider to hidden inputs and display badges
                citationsSlider.noUiSlider.on('update', function (values, handle) {
                    const minValue = values[0];
                    const maxValue = values[1];
                    const citationsMinInput = document.getElementById('citationsMinInput');
                    const citationsMaxInput = document.getElementById('citationsMaxInput');
                    const citationsMinDisplay = document.getElementById('citationsMinDisplay');
                    const citationsMaxDisplay = document.getElementById('citationsMaxDisplay');
                    if (citationsMinInput)
                        citationsMinInput.value = minValue;
                    if (citationsMaxInput)
                        citationsMaxInput.value = maxValue;
                    if (citationsMinDisplay)
                        citationsMinDisplay.textContent = minValue;
                    if (citationsMaxDisplay)
                        citationsMaxDisplay.textContent = maxValue;
                });
                console.log('[noUiSlider] Citations slider initialized:', citationsMin, '-', citationsMax, '(max range:', citationsMaxRange + ')');
            }
            catch (e) {
                console.warn('[noUiSlider] Citations slider initialization error:', e.message);
            }
        }
        // ============================================
        // Impact Factor Slider (dynamic max from data attribute, decimals)
        // ============================================
        const impactFactorSlider = document.getElementById('impactFactorSlider');
        if (impactFactorSlider && !impactFactorSlider.noUiSlider) {
            try {
                const impactMin = parseFloat(urlParams.get('min_impact_factor') || '0') || 0;
                const impactMaxRange = parseFloat(impactFactorSlider.dataset.max || '50.0') || 50.0;
                const impactMax = parseFloat(urlParams.get('max_impact_factor') || '') || impactMaxRange;
                // @ts-ignore - noUiSlider library
                noUiSlider.create(impactFactorSlider, {
                    start: [impactMin, impactMax],
                    connect: true,
                    range: {
                        'min': 0,
                        'max': impactMaxRange
                    },
                    step: Math.max(0.1, impactMaxRange / 100),
                    format: {
                        to: function (value) {
                            return value.toFixed(1);
                        },
                        from: function (value) {
                            return parseFloat(value);
                        }
                    }
                });
                // Sync slider to hidden inputs and display badges
                impactFactorSlider.noUiSlider.on('update', function (values, handle) {
                    const minValue = values[0];
                    const maxValue = values[1];
                    const impactFactorMinInput = document.getElementById('impactFactorMinInput');
                    const impactFactorMaxInput = document.getElementById('impactFactorMaxInput');
                    const impactFactorMinDisplay = document.getElementById('impactFactorMinDisplay');
                    const impactFactorMaxDisplay = document.getElementById('impactFactorMaxDisplay');
                    if (impactFactorMinInput)
                        impactFactorMinInput.value = minValue;
                    if (impactFactorMaxInput)
                        impactFactorMaxInput.value = maxValue;
                    if (impactFactorMinDisplay)
                        impactFactorMinDisplay.textContent = minValue;
                    if (impactFactorMaxDisplay)
                        impactFactorMaxDisplay.textContent = maxValue;
                });
                console.log('[noUiSlider] Impact Factor slider initialized:', impactMin, '-', impactMax, '(max range:', impactMaxRange + ')');
            }
            catch (e) {
                console.warn('[noUiSlider] Impact Factor slider initialization error:', e.message);
            }
        }
        console.log('[noUiSlider] All sliders initialized successfully with dynamic ranges');
    });
}
//# sourceMappingURL=nouislider-init.js.map