/**
 * Console Interceptor - Tee-like functionality for console logs
 *
 * Captures console.log, console.info, console.warn, console.error
 * and sends them to server to be written to ./logs/console.log
 *
 * Works like `tee`:
 * - Shows in browser DevTools (stdout)
 * - Writes to file on server (file)
 */
interface ConsoleLogEntry {
    level: string;
    message: string;
    source: string;
    timestamp: number;
    url: string;
}
declare class ConsoleInterceptor {
    private buffer;
    private batchInterval;
    private maxBatchSize;
    private apiEndpoint;
    private enabled;
    private originalConsole;
    constructor();
    private init;
    private interceptConsoleMethods;
    private capture;
    private formatMessage;
    private getSource;
    private startBatchSender;
    private sendBatch;
}
//# sourceMappingURL=console-interceptor.d.ts.map