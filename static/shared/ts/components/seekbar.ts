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

// ============================================================================
// Type Definitions
// ============================================================================

/** Seekbar values */

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/static/ts/components/seekbar.ts loaded");
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

/** Internal elements references */
interface SeekbarElements {
    container: HTMLDivElement;
    track: HTMLDivElement;
    range: HTMLDivElement;
    handleMin: HTMLDivElement;
    handleMax: HTMLDivElement;
    labelMin: HTMLDivElement | null;
    labelMax: HTMLDivElement | null;
    valueMin?: HTMLSpanElement;
    valueMax?: HTMLSpanElement;
}

/** Complete options with defaults applied */
interface CompleteSeekbarOptions extends Required<Omit<SeekbarOptions, 'onChange' | 'onUpdate' | 'onStart' | 'onEnd'>> {
    onChange: ValueCallback | null;
    onUpdate: ValueCallback | null;
    onStart: ValueCallback | null;
    onEnd: ValueCallback | null;
}

// ============================================================================
// Main Class
// ============================================================================

export class ScitexSeekbar {
    private container: HTMLElement;
    private options: CompleteSeekbarOptions;
    private values: SeekbarValues;
    private dragging: HandleType | null = null;
    private elements!: SeekbarElements; // Initialized in _buildDOM
    /**
     * Creates a new ScitexSeekbar instance
     *
     * @param element - Selector or DOM element
     * @param options - Configuration options
     * @throws Error if element not found
     */
    constructor(element: string | HTMLElement, options: SeekbarOptions = {}) {
        // Get element
        const container = typeof element === 'string'
            ? document.querySelector<HTMLElement>(element)
            : element;

        if (!container) {
            throw new Error('ScitexSeekbar: Element not found');
        }

        this.container = container;
        // Default options
        const dataset = this.container.dataset;
        this.options = {
            min: parseFloat(dataset.min || '0') || 0,
            max: parseFloat(dataset.max || '100') || 100,
            valueMin: parseFloat(dataset.valueMin || '25') || 25,
            valueMax: parseFloat(dataset.valueMax || '75') || 75,
            step: parseFloat(dataset.step || '1') || 1,
            format: (value: number): string => value.toString(),            onChange: null,
            onUpdate: null,
            onStart: null,
            onEnd: null,
            showLabels: true,
            showValues: false,
            ...options
        };
        // Validate values
        this.values = {
            min: this._clamp(this.options.valueMin, this.options.min, this.options.max),
            max: this._clamp(this.options.valueMax, this.options.min, this.options.max)
        };

        // Initialize
        this._init();
    }

    // ========================================================================
    // Initialization
    // ========================================================================
    /**
     * Initialize the seekbar
     * @private
     */
    private _init(): void {
        // Add class to container
        this.container.classList.add('scitex-seekbar-dual');
        // Build DOM structure
        this._buildDOM();
        // Bind event handlers
        this._bindEvents();
        // Initial render
        this._render();
    }
    /**
     * Build DOM structure
     * @private
     */
    private _buildDOM(): void {
        // Create container
        const container = document.createElement('div');
        container.className = 'scitex-seekbar-dual-container';
        // Create track
        const track = document.createElement('div');
        track.className = 'scitex-seekbar-dual-track';
        container.appendChild(track);
        // Create active range
        const range = document.createElement('div');
        range.className = 'scitex-seekbar-dual-range';
        container.appendChild(range);
        // Create min handle
        const handleMin = this._createHandle('min', this.values.min);
        container.appendChild(handleMin);
        // Create max handle
        const handleMax = this._createHandle('max', this.values.max);
        container.appendChild(handleMax);
        // Clear container and append
        this.container.innerHTML = '';
        this.container.appendChild(container);
        // Store references
        this.elements = {
            container,
            track,
            range,
            handleMin,
            handleMax,
            labelMin: this.options.showLabels
                ? handleMin.querySelector<HTMLDivElement>('.scitex-seekbar-dual-handle-label')
                : null,
            labelMax: this.options.showLabels
                ? handleMax.querySelector<HTMLDivElement>('.scitex-seekbar-dual-handle-label')                : null
        };
        // Add value display if requested
        if (this.options.showValues) {
            const valuesDiv = document.createElement('div');
            valuesDiv.className = 'scitex-seekbar-values';
            valuesDiv.innerHTML = `
                <span class="scitex-seekbar-value" data-value="min">${this.options.format(this.values.min)}</span>
                <span class="scitex-seekbar-value" data-value="max">${this.options.format(this.values.max)}</span>
            `;
            this.container.appendChild(valuesDiv);

            this.elements.valueMin = valuesDiv.querySelector<HTMLSpanElement>('[data-value="min"]') || undefined;
            this.elements.valueMax = valuesDiv.querySelector<HTMLSpanElement>('[data-value="max"]') || undefined;        }
    }
    /**
     * Create a handle element
     * @private
     */
    _createHandle(type, value) {
        const handle = document.createElement('div');
        handle.className = 'scitex-seekbar-dual-handle';
        handle.setAttribute('role', 'slider');
        handle.setAttribute('aria-label', type === 'min' ? 'Minimum value' : 'Maximum value');
        handle.setAttribute('aria-valuemin', this.options.min.toString());
        handle.setAttribute('aria-valuemax', this.options.max.toString());
        handle.setAttribute('aria-valuenow', value.toString());
        handle.setAttribute('tabindex', '0');
        handle.dataset.handle = type;
        if (this.options.showLabels) {
            const label = document.createElement('div');
            label.className = 'scitex-seekbar-dual-handle-label';
            label.textContent = this.options.format(value);
            handle.appendChild(label);
        }
        return handle;
    }
    // ========================================================================
    // Event Binding
    // ========================================================================
    /**
     * Create a handle element
     * @private
     */
    private _createHandle(type: HandleType, value: number): HTMLDivElement {
        const handle = document.createElement('div');
        handle.className = 'scitex-seekbar-dual-handle';
        handle.setAttribute('role', 'slider');
        handle.setAttribute('aria-label', type === 'min' ? 'Minimum value' : 'Maximum value');
        handle.setAttribute('aria-valuemin', this.options.min.toString());
        handle.setAttribute('aria-valuemax', this.options.max.toString());
        handle.setAttribute('aria-valuenow', value.toString());
        handle.setAttribute('tabindex', '0');
        handle.dataset.handle = type;

        if (this.options.showLabels) {
            const label = document.createElement('div');
            label.className = 'scitex-seekbar-dual-handle-label';
            label.textContent = this.options.format(value);
            handle.appendChild(label);
        }

        return handle;
    }

    // ========================================================================
    // Event Binding
    // ========================================================================

    /**
     * Bind event handlers
     * @private
     */
    private _bindEvents(): void {
        // Mouse events
        this.elements.handleMin.addEventListener('mousedown', (e) => this._onMouseDown(e, 'min'));
        this.elements.handleMax.addEventListener('mousedown', (e) => this._onMouseDown(e, 'max'));
        // Touch events
        this.elements.handleMin.addEventListener('touchstart', (e) => this._onTouchStart(e, 'min'), { passive: false });
        this.elements.handleMax.addEventListener('touchstart', (e) => this._onTouchStart(e, 'max'), { passive: false });
        // Keyboard events
        this.elements.handleMin.addEventListener('keydown', (e) => this._onKeyDown(e, 'min'));
        this.elements.handleMax.addEventListener('keydown', (e) => this._onKeyDown(e, 'max'));
        // Track click
        this.elements.track.addEventListener('click', (e) => this._onTrackClick(e));
    }

    // ========================================================================
    // Mouse Event Handlers
    // ========================================================================
    /**
     * Mouse down handler
     * @private
     */
    private _onMouseDown(e: MouseEvent, handle: HandleType): void {
        e.preventDefault();
        this.dragging = handle;
        if (this.options.onStart) {
            this.options.onStart(this.getValues());
        }

        const onMouseMove = (e: MouseEvent): void => this._onMouseMove(e);
        const onMouseUp = (): void => {            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            this._onDragEnd();
        };
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    }
    /**
     * Mouse move handler
     * @private
     */
    private _onMouseMove(e: MouseEvent): void {
        if (!this.dragging) return;

        const value = this._getValueFromPosition(e.clientX);
        this._updateValue(this.dragging, value);
    }

    // ========================================================================
    // Touch Event Handlers
    // ========================================================================
    /**
     * Touch start handler
     * @private
     */
    private _onTouchStart(e: TouchEvent, handle: HandleType): void {
        e.preventDefault();
        this.dragging = handle;
        if (this.options.onStart) {
            this.options.onStart(this.getValues());
        }

        const onTouchMove = (e: TouchEvent): void => this._onTouchMove(e);
        const onTouchEnd = (): void => {            document.removeEventListener('touchmove', onTouchMove);
            document.removeEventListener('touchend', onTouchEnd);
            this._onDragEnd();
        };
        document.addEventListener('touchmove', onTouchMove, { passive: false });
        document.addEventListener('touchend', onTouchEnd);
    }
    /**
     * Touch move handler
     * @private
     */
    private _onTouchMove(e: TouchEvent): void {
        if (!this.dragging) return;        e.preventDefault();
        const touch = e.touches[0];
        if (!touch) return;
        const value = this._getValueFromPosition(touch.clientX);
        this._updateValue(this.dragging, value);
    }
    /**
     * Drag end handler
     * @private
     */
    private _onDragEnd(): void {
        if (!this.dragging) return;
        if (this.options.onEnd) {
            this.options.onEnd(this.getValues());
        }
        this.dragging = null;
    }

    // ========================================================================
    // Keyboard Event Handler
    // ========================================================================
    /**
     * Keyboard handler
     * @private
     */
    private _onKeyDown(e: KeyboardEvent, handle: HandleType): void {
        let delta = 0;
        switch (e.key) {
            case 'ArrowLeft':
            case 'ArrowDown':
                delta = -this.options.step;
                break;
            case 'ArrowRight':
            case 'ArrowUp':
                delta = this.options.step;
                break;
            case 'PageDown':
                delta = -this.options.step * 10;
                break;
            case 'PageUp':
                delta = this.options.step * 10;
                break;
            case 'Home':
                this._updateValue(handle, this.options.min);
                e.preventDefault();
                return;
            case 'End':
                this._updateValue(handle, this.options.max);
                e.preventDefault();
                return;
            default:
                return;
        }
        if (delta !== 0) {
            e.preventDefault();
            const newValue = this.values[handle] + delta;
            this._updateValue(handle, newValue);
        }
    }
    /**
     * Track click handler
     * @private
     */
    private _onTrackClick(e: MouseEvent): void {
        const value = this._getValueFromPosition(e.clientX);
        const distMin = Math.abs(value - this.values.min);
        const distMax = Math.abs(value - this.values.max);
        // Move the closest handle
        const handle: HandleType = distMin < distMax ? 'min' : 'max';
        this._updateValue(handle, value);
        if (this.options.onChange) {
            this.options.onChange(this.getValues());
        }
    }

    // ========================================================================
    // Value Manipulation
    // ========================================================================
    /**
     * Get value from mouse/touch position
     * @private
     */
    private _getValueFromPosition(clientX: number): number {
        const rect = this.elements.track.getBoundingClientRect();
        const percent = (clientX - rect.left) / rect.width;
        const rawValue = this.options.min + percent * (this.options.max - this.options.min);
        return this._snapToStep(rawValue);
    }
    /**
     * Update a handle value
     * @private
     */
    private _updateValue(handle: HandleType, value: number): void {
        // Clamp value
        value = this._clamp(value, this.options.min, this.options.max);
        // Ensure min <= max
        if (handle === 'min') {
            value = Math.min(value, this.values.max);
        }
        else {
            value = Math.max(value, this.values.min);
        }
        // Update value
        this.values[handle] = value;
        // Update ARIA
        const element = handle === 'min' ? this.elements.handleMin : this.elements.handleMax;
        element.setAttribute('aria-valuenow', value.toString());
    }

    // ========================================================================
    // Utility Methods
    // ========================================================================
    /**
     * Clamp a value between min and max
     * @private
     */
    private _clamp(value: number, min: number, max: number): number {
        return Math.min(Math.max(value, min), max);
    }
    /**
     * Snap value to step
     * @private
     */
    private _snapToStep(value: number): number {
        const steps = Math.round((value - this.options.min) / this.options.step);
        return this.options.min + steps * this.options.step;
    }

    // ========================================================================
    // Public API
    // ========================================================================
    /**
     * Get current values
     * @returns Current min and max values
     */
    public getValues(): SeekbarValues {
        return {
            min: this.values.min,
            max: this.values.max
        };
    }
    /**
     * Set values programmatically
     * @param min - Minimum value
     * @param max - Maximum value
     */
    public setValues(min: number, max: number): void {
        this._updateValue('min', min);
        this._updateValue('max', max);
        if (this.options.onChange) {
            this.options.onChange(this.getValues());
        }
    }
    /**
     * Reset to initial values
     */
    public reset(): void {
        this.setValues(this.options.valueMin, this.options.valueMax);
    }
    /**
     * Destroy the seekbar instance
     */
    public destroy(): void {
        if (this.container) {
            this.container.innerHTML = '';
            this.container.classList.remove('scitex-seekbar-dual');
        }
    }
}

// ============================================================================
// Auto-initialization
// ============================================================================
/**
 * Auto-initialization from DOM
 * Automatically initializes all elements with data-scitex-seekbar attribute
 */
document.addEventListener('DOMContentLoaded', () => {
    const autoInit = document.querySelectorAll<HTMLElement>('[data-scitex-seekbar="auto"]');
    autoInit.forEach(element => {
        new ScitexSeekbar(element);
    });
});

// ============================================================================
// Global Export
// ============================================================================

declare global {
    interface Window {
        ScitexSeekbar: typeof ScitexSeekbar;
    }
}

// Export to global namespace
if (typeof window !== 'undefined') {
    window.ScitexSeekbar = ScitexSeekbar;
}
//# sourceMappingURL=seekbar.js.map