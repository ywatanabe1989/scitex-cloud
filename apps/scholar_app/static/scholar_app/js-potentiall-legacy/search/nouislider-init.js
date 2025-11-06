/**
 * noUiSlider Initialization for SciTeX Scholar Filters
 * Proper dual-range slider implementation without z-index issues
 */

// Guard against multiple initializations
if (window.__nouisliderInitialized) {
    console.log('[noUiSlider] Already initialized, skipping');
} else {
    window.__nouisliderInitialized = true;
    document.addEventListener('DOMContentLoaded', function() {
        console.log('[noUiSlider] Initializing dual-range sliders...');

    // Get URL parameters for initial values
    const urlParams = new URLSearchParams(window.location.search);

    // ============================================
    // Year Slider (dynamic range from data attributes)
    // ============================================
    const yearSlider = document.getElementById('yearSlider');
    if (yearSlider && !yearSlider.noUiSlider) {
        try {
            const yearMinRange = parseInt(yearSlider.dataset.min) || 1900;
            const yearMaxRange = parseInt(yearSlider.dataset.max) || 2025;
            const yearMin = parseInt(urlParams.get('year_from')) || yearMinRange;
            const yearMax = parseInt(urlParams.get('year_to')) || yearMaxRange;

            noUiSlider.create(yearSlider, {
                start: [yearMin, yearMax],
                connect: true,
                range: {
                    'min': yearMinRange,
                    'max': yearMaxRange
                },
                step: 1,
                format: {
                    to: function(value) {
                        return Math.round(value);
                    },
                    from: function(value) {
                        return Math.round(value);
                    }
                }
            });

            // Sync slider to hidden inputs and display badges
            yearSlider.noUiSlider.on('update', function(values, handle) {
                const minValue = values[0];
                const maxValue = values[1];

                document.getElementById('yearFromInput').value = minValue;
                document.getElementById('yearToInput').value = maxValue;
                document.getElementById('yearMinDisplay').textContent = minValue;
                document.getElementById('yearMaxDisplay').textContent = maxValue;
            });

            console.log('[noUiSlider] Year slider initialized:', yearMin, '-', yearMax, '(range:', yearMinRange, '-', yearMaxRange + ')');
        } catch (e) {
            console.warn('[noUiSlider] Year slider initialization error:', e.message);
        }
    }

    // ============================================
    // Citations Slider (dynamic max from data attribute)
    // ============================================
    const citationsSlider = document.getElementById('citationsSlider');
    if (citationsSlider && !citationsSlider.noUiSlider) {
        try {
            const citationsMin = parseInt(urlParams.get('min_citations')) || 0;
            const citationsMaxRange = parseInt(citationsSlider.dataset.max) || 12000;
            const citationsMax = parseInt(urlParams.get('max_citations')) || citationsMaxRange;

            noUiSlider.create(citationsSlider, {
                start: [citationsMin, citationsMax],
                connect: true,
                range: {
                    'min': 0,
                    'max': citationsMaxRange
                },
                step: Math.max(1, Math.floor(citationsMaxRange / 100)),
                format: {
                    to: function(value) {
                        return Math.round(value);
                    },
                    from: function(value) {
                        return Math.round(value);
                    }
                }
            });

            // Sync slider to hidden inputs and display badges
            citationsSlider.noUiSlider.on('update', function(values, handle) {
                const minValue = values[0];
                const maxValue = values[1];

                document.getElementById('citationsMinInput').value = minValue;
                document.getElementById('citationsMaxInput').value = maxValue;
                document.getElementById('citationsMinDisplay').textContent = minValue;
                document.getElementById('citationsMaxDisplay').textContent = maxValue;
            });

            console.log('[noUiSlider] Citations slider initialized:', citationsMin, '-', citationsMax, '(max range:', citationsMaxRange + ')');
        } catch (e) {
            console.warn('[noUiSlider] Citations slider initialization error:', e.message);
        }
    }

    // ============================================
    // Impact Factor Slider (dynamic max from data attribute, decimals)
    // ============================================
    const impactFactorSlider = document.getElementById('impactFactorSlider');
    if (impactFactorSlider && !impactFactorSlider.noUiSlider) {
        try {
            const impactMin = parseFloat(urlParams.get('min_impact_factor')) || 0;
            const impactMaxRange = parseFloat(impactFactorSlider.dataset.max) || 50.0;
            const impactMax = parseFloat(urlParams.get('max_impact_factor')) || impactMaxRange;

            noUiSlider.create(impactFactorSlider, {
                start: [impactMin, impactMax],
                connect: true,
                range: {
                    'min': 0,
                    'max': impactMaxRange
                },
                step: Math.max(0.1, impactMaxRange / 100),
                format: {
                    to: function(value) {
                        return value.toFixed(1);
                    },
                    from: function(value) {
                        return parseFloat(value);
                    }
                }
            });

            // Sync slider to hidden inputs and display badges
            impactFactorSlider.noUiSlider.on('update', function(values, handle) {
                const minValue = values[0];
                const maxValue = values[1];

                document.getElementById('impactFactorMinInput').value = minValue;
                document.getElementById('impactFactorMaxInput').value = maxValue;
                document.getElementById('impactFactorMinDisplay').textContent = minValue;
                document.getElementById('impactFactorMaxDisplay').textContent = maxValue;
            });

            console.log('[noUiSlider] Impact Factor slider initialized:', impactMin, '-', impactMax, '(max range:', impactMaxRange + ')');
        } catch (e) {
            console.warn('[noUiSlider] Impact Factor slider initialization error:', e.message);
        }
    }

    console.log('[noUiSlider] All sliders initialized successfully with dynamic ranges');
    });
}
