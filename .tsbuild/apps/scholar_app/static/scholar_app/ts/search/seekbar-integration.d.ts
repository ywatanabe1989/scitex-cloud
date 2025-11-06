/**

 * SciTeX Seekbar Integration for Scholar App
 *
 * This file provides integration between the SciTeX Seekbar component
 * and the Scholar app's existing filter system. It can work alongside
 * noUiSlider or replace it entirely.
 *
 * External library: ScitexSeekbar (requires `any` types or @ts-ignore)
 *
 * @version 1.0.0
 */
declare const ScitexSeekbar: any;
/**
 * Seekbar values interface
 */
interface SeekbarValues {
    min: number;
    max: number;
}
/**
 * Seekbar instance interface
 */
interface SeekbarInstance {
    getValues: () => SeekbarValues;
    setValues: (min: number, max: number) => void;
    reset: () => void;
}
/**
 * Extended HTMLElement with noUiSlider property
 */
interface NoUiSliderElement extends HTMLElement {
    noUiSlider?: any;
}
/**
 * Window interface extension
 */
declare global {
    interface Window {
        __scholarSeekbarInitialized?: boolean;
        scholarSeekbar?: ScholarSeekbarIntegration;
    }
}
/**
 * ScholarSeekbarIntegration class
 */
declare class ScholarSeekbarIntegration {
    private sliders;
    constructor();
    /**
     * Initialize seekbar integration
     */
    private init;
    /**
     * Initialize SciTeX Seekbars for all filter ranges
     */
    private initScitexSeekbars;
    /**
     * Initialize Year Range Slider
     */
    private initYearSlider;
    /**
     * Initialize Citations Range Slider
     */
    private initCitationsSlider;
    /**
     * Initialize Impact Factor Range Slider
     */
    private initImpactFactorSlider;
    /**
     * Update year display badges
     */
    private updateYearDisplay;
    /**
     * Update citations display badges
     */
    private updateCitationsDisplay;
    /**
     * Update impact factor display badges
     */
    private updateImpactFactorDisplay;
    /**
     * Update hidden form inputs
     */
    private updateHiddenInputs;
    /**
     * Get current slider values
     */
    getValues(sliderName: string): SeekbarValues | null;
    /**
     * Set slider values programmatically
     */
    setValues(sliderName: string, min: number, max: number): void;
    /**
     * Reset all sliders to default
     */
    resetAll(): void;
}
//# sourceMappingURL=seekbar-integration.d.ts.map