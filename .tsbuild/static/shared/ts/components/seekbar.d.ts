/**
 * SciTeX Seekbar Component - TypeScript Implementation
 *
 * Provides dual-handle range slider functionality using native DOM APIs.
 * No external dependencies required.
 *
 * Features:
 * - Dual-handle range slider
 * - Touch and mouse support
 * - Keyboard accessibility (Arrow keys, Home, End, Page Up/Down)
 * - Value formatting callbacks
 * - Event callbacks (onChange, onUpdate, onStart, onEnd)
 * - Programmatic API
 *
 * Usage:
 *   const seekbar = new ScitexSeekbar('#mySeekbar', {
 *     min: 0,
 *     max: 100,
 *     valueMin: 25,
 *     valueMax: 75,
 *     step: 1,
 *     onChange: (values) => console.log(values)
 *   });
 *
 * @version 2.0.0 (TypeScript)
 * @author SciTeX Development Team
 */
export interface SeekbarValues {
    min: number;
    max: number;
}
/** Value formatter function */
export type FormatFunction = (value: number) => string;
/** Callback for value changes */
export type ValueCallback = (values: SeekbarValues) => void;
/** Handle type */
export type HandleType = 'min' | 'max';
/** Seekbar configuration options */
export interface SeekbarOptions {
    /** Minimum value (default: 0) */
    min?: number;
    /** Maximum value (default: 100) */
    max?: number;
    /** Initial minimum value */
    valueMin?: number;
    /** Initial maximum value */
    valueMax?: number;
    /** Step increment (default: 1) */
    step?: number;
    /** Value formatting function */
    format?: FormatFunction;
    /** Called when value changes */
    onChange?: ValueCallback | null;
    /** Called during drag */
    onUpdate?: ValueCallback | null;
    /** Called when drag starts */
    onStart?: ValueCallback | null;
    /** Called when drag ends */
    onEnd?: ValueCallback | null;
    /** Show value labels on hover (default: true) */
    showLabels?: boolean;
    /** Show value display below (default: false) */
    showValues?: boolean;
}
export declare class ScitexSeekbar {
    private container;
    private options;
    private values;
    private dragging;
    private elements;
    /**
     * Creates a new ScitexSeekbar instance
     *
     * @param element - Selector or DOM element
     * @param options - Configuration options
     * @throws Error if element not found
     */
    constructor(element: string | HTMLElement, options?: SeekbarOptions);
    /**
     * Initialize the seekbar
     * @private
     */
    private _init;
    /**
     * Build DOM structure
     * @private
     */
    private _buildDOM;
    /**
     * Create a handle element
     * @private
     */
    private _createHandle;
    /**
     * Bind event handlers
     * @private
     */
    private _bindEvents;
    /**
     * Mouse down handler
     * @private
     */
    private _onMouseDown;
    /**
     * Mouse move handler
     * @private
     */
    private _onMouseMove;
    /**
     * Touch start handler
     * @private
     */
    private _onTouchStart;
    /**
     * Touch move handler
     * @private
     */
    private _onTouchMove;
    /**
     * Drag end handler
     * @private
     */
    private _onDragEnd;
    /**
     * Keyboard handler
     * @private
     */
    private _onKeyDown;
    /**
     * Track click handler
     * @private
     */
    private _onTrackClick;
    /**
     * Get value from mouse/touch position
     * @private
     */
    private _getValueFromPosition;
    /**
     * Update a handle value
     * @private
     */
    private _updateValue;
    /**
     * Render the seekbar
     * @private
     */
    private _render;
    /**
     * Clamp a value between min and max
     * @private
     */
    private _clamp;
    /**
     * Snap value to step
     * @private
     */
    private _snapToStep;
    /**
     * Get current values
     * @returns Current min and max values
     */
    getValues(): SeekbarValues;
    /**
     * Set values programmatically
     * @param min - Minimum value
     * @param max - Maximum value
     */
    setValues(min: number, max: number): void;
    /**
     * Reset to initial values
     */
    reset(): void;
    /**
     * Destroy the seekbar instance
     */
    destroy(): void;
}
declare global {
    interface Window {
        ScitexSeekbar: typeof ScitexSeekbar;
    }
}
//# sourceMappingURL=seekbar.d.ts.map