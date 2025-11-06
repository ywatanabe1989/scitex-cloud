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
declare const noUiSlider: any;
/**
 * Extended HTMLElement interface for noUiSlider
 */
interface NoUiSliderElement extends HTMLElement {
    noUiSlider?: any;
}
/**
 * Window interface extension for initialization guard
 */
declare global {
    interface Window {
        __nouisliderInitialized?: boolean;
    }
}
//# sourceMappingURL=nouislider-init.d.ts.map