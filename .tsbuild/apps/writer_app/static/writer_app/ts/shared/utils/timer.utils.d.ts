/**
 * Timer and debounce/throttle utilities
 */
export declare function debounce<T extends (...args: any[]) => any>(func: T, wait: number, immediate?: boolean): (...args: Parameters<T>) => void;
/**
 * Throttle function to limit execution frequency
 */
export declare function throttle<T extends (...args: any[]) => any>(func: T, limit: number): (...args: Parameters<T>) => void;
/**
 * Format elapsed time for display
 */
export declare function formatElapsedTime(milliseconds: number): string;
/**
 * Create a simple timer
 */
export declare class SimpleTimer {
    private startTime;
    private isRunning;
    private interval?;
    start(onTick?: (elapsed: number) => void): void;
    stop(): number;
    getElapsed(): number;
    reset(): void;
    isActive(): boolean;
}
/**
 * Wait for specified time
 */
export declare function wait(ms: number): Promise<void>;
/**
 * Create a cancellable timeout
 */
export declare function createTimeout(callback: () => void, ms: number): {
    cancel: () => void;
};
//# sourceMappingURL=timer.utils.d.ts.map