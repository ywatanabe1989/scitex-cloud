/**
 * Timer and debounce/throttle utilities
 */
/**
 * Debounce function to delay execution
 */
export function debounce(func, wait, immediate = false) {
    let timeout = null;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate)
                func(...args);
        };
        const callNow = immediate && !timeout;
        if (timeout)
            clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow)
            func(...args);
    };
}
/**
 * Throttle function to limit execution frequency
 */
export function throttle(func, limit) {
    let inThrottle = false;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => (inThrottle = false), limit);
        }
    };
}
/**
 * Format elapsed time for display
 */
export function formatElapsedTime(milliseconds) {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    if (minutes > 0) {
        return `${minutes}m ${seconds}s`;
    }
    return `${seconds}s`;
}
/**
 * Create a simple timer
 */
export class SimpleTimer {
    constructor() {
        this.startTime = 0;
        this.isRunning = false;
    }
    start(onTick) {
        this.startTime = Date.now();
        this.isRunning = true;
        if (onTick) {
            this.interval = setInterval(() => {
                if (this.isRunning) {
                    const elapsed = Date.now() - this.startTime;
                    onTick(elapsed);
                }
            }, 100);
        }
    }
    stop() {
        this.isRunning = false;
        if (this.interval) {
            clearInterval(this.interval);
        }
        return Date.now() - this.startTime;
    }
    getElapsed() {
        if (!this.isRunning)
            return 0;
        return Date.now() - this.startTime;
    }
    reset() {
        this.stop();
        this.startTime = 0;
    }
    isActive() {
        return this.isRunning;
    }
}
/**
 * Wait for specified time
 */
export function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
/**
 * Create a cancellable timeout
 */
export function createTimeout(callback, ms) {
    const timeout = setTimeout(callback, ms);
    return {
        cancel: () => clearTimeout(timeout),
    };
}
//# sourceMappingURL=timer.utils.js.map