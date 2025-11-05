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
// ============================================================================
// Main Class
// ============================================================================
export class ScitexSeekbar {
    container;
    options;
    values;
    dragging = null;
    elements; // Initialized in _buildDOM
    /**
     * Creates a new ScitexSeekbar instance
     *
     * @param element - Selector or DOM element
     * @param options - Configuration options
     * @throws Error if element not found
     */
    constructor(element, options = {}) {
        // Get element
        const container = typeof element === 'string'
            ? document.querySelector(element)
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
            format: (value) => value.toString(),
            onChange: null,
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
    _init() {
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
    _buildDOM() {
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
                ? handleMin.querySelector('.scitex-seekbar-dual-handle-label')
                : null,
            labelMax: this.options.showLabels
                ? handleMax.querySelector('.scitex-seekbar-dual-handle-label')
                : null
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
            this.elements.valueMin = valuesDiv.querySelector('[data-value="min"]') || undefined;
            this.elements.valueMax = valuesDiv.querySelector('[data-value="max"]') || undefined;
        }
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
     * Bind event handlers
     * @private
     */
    _bindEvents() {
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
    _onMouseDown(e, handle) {
        e.preventDefault();
        this.dragging = handle;
        if (this.options.onStart) {
            this.options.onStart(this.getValues());
        }
        const onMouseMove = (e) => this._onMouseMove(e);
        const onMouseUp = () => {
            document.removeEventListener('mousemove', onMouseMove);
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
    _onMouseMove(e) {
        if (!this.dragging)
            return;
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
    _onTouchStart(e, handle) {
        e.preventDefault();
        this.dragging = handle;
        if (this.options.onStart) {
            this.options.onStart(this.getValues());
        }
        const onTouchMove = (e) => this._onTouchMove(e);
        const onTouchEnd = () => {
            document.removeEventListener('touchmove', onTouchMove);
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
    _onTouchMove(e) {
        if (!this.dragging)
            return;
        e.preventDefault();
        const touch = e.touches[0];
        if (!touch)
            return;
        const value = this._getValueFromPosition(touch.clientX);
        this._updateValue(this.dragging, value);
    }
    /**
     * Drag end handler
     * @private
     */
    _onDragEnd() {
        if (!this.dragging)
            return;
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
    _onKeyDown(e, handle) {
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
    _onTrackClick(e) {
        const value = this._getValueFromPosition(e.clientX);
        const distMin = Math.abs(value - this.values.min);
        const distMax = Math.abs(value - this.values.max);
        // Move the closest handle
        const handle = distMin < distMax ? 'min' : 'max';
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
    _getValueFromPosition(clientX) {
        const rect = this.elements.track.getBoundingClientRect();
        const percent = (clientX - rect.left) / rect.width;
        const rawValue = this.options.min + percent * (this.options.max - this.options.min);
        return this._snapToStep(rawValue);
    }
    /**
     * Update a handle value
     * @private
     */
    _updateValue(handle, value) {
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
        // Render
        this._render();
        // Callbacks
        if (this.options.onUpdate) {
            this.options.onUpdate(this.getValues());
        }
        if (this.dragging && this.options.onChange) {
            this.options.onChange(this.getValues());
        }
    }
    /**
     * Render the seekbar
     * @private
     */
    _render() {
        const range = this.options.max - this.options.min;
        const minPercent = ((this.values.min - this.options.min) / range) * 100;
        const maxPercent = ((this.values.max - this.options.min) / range) * 100;
        // Position handles
        this.elements.handleMin.style.left = `${minPercent}%`;
        this.elements.handleMax.style.left = `${maxPercent}%`;
        // Position active range
        this.elements.range.style.left = `${minPercent}%`;
        this.elements.range.style.width = `${maxPercent - minPercent}%`;
        // Update labels
        if (this.options.showLabels) {
            if (this.elements.labelMin) {
                this.elements.labelMin.textContent = this.options.format(this.values.min);
            }
            if (this.elements.labelMax) {
                this.elements.labelMax.textContent = this.options.format(this.values.max);
            }
        }
        // Update value displays
        if (this.options.showValues) {
            if (this.elements.valueMin) {
                this.elements.valueMin.textContent = this.options.format(this.values.min);
            }
            if (this.elements.valueMax) {
                this.elements.valueMax.textContent = this.options.format(this.values.max);
            }
        }
    }
    // ========================================================================
    // Utility Methods
    // ========================================================================
    /**
     * Clamp a value between min and max
     * @private
     */
    _clamp(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }
    /**
     * Snap value to step
     * @private
     */
    _snapToStep(value) {
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
    getValues() {
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
    setValues(min, max) {
        this._updateValue('min', min);
        this._updateValue('max', max);
        if (this.options.onChange) {
            this.options.onChange(this.getValues());
        }
    }
    /**
     * Reset to initial values
     */
    reset() {
        this.setValues(this.options.valueMin, this.options.valueMax);
    }
    /**
     * Destroy the seekbar instance
     */
    destroy() {
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
    const autoInit = document.querySelectorAll('[data-scitex-seekbar="auto"]');
    autoInit.forEach(element => {
        new ScitexSeekbar(element);
    });
});
// Export to global namespace
if (typeof window !== 'undefined') {
    window.ScitexSeekbar = ScitexSeekbar;
}
//# sourceMappingURL=seekbar.js.map