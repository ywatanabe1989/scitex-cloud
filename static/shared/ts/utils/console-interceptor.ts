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

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/static/ts/utils/console-interceptor.ts loaded",
);
interface ConsoleLogEntry {
  level: string;
  message: string;
  source: string;
  timestamp: number;
  url: string;
}

class ConsoleInterceptor {
  private buffer: ConsoleLogEntry[] = [];
  private batchInterval: number = 1000; // 1 second
  private maxBatchSize: number = 50;
  private apiEndpoint: string = "/dev/api/console/";
  private enabled: boolean = false;

  // Store original console methods
  private originalConsole = {
    log: console.log,
    info: console.info,
    warn: console.warn,
    error: console.error,
    debug: console.debug,
  };

  constructor() {
    // Only enable in development
    this.enabled =
      document.documentElement.hasAttribute("data-debug") ||
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1";

    if (this.enabled) {
      this.init();
    }
  }

  private init(): void {
    this.interceptConsoleMethods();
    this.startBatchSender();
    console.info(
      "[Console Interceptor] Active - logs will be saved to ./logs/console.log",
    );
  }

  private interceptConsoleMethods(): void {
    const self = this;

    // Intercept console.log
    console.log = function (...args: any[]) {
      self.originalConsole.log.apply(console, args);
      self.capture("log", args);
    };

    // Intercept console.info
    console.info = function (...args: any[]) {
      self.originalConsole.info.apply(console, args);
      self.capture("info", args);
    };

    // Intercept console.warn
    console.warn = function (...args: any[]) {
      self.originalConsole.warn.apply(console, args);
      self.capture("warn", args);
    };

    // Intercept console.error
    console.error = function (...args: any[]) {
      self.originalConsole.error.apply(console, args);
      self.capture("error", args);
    };

    // Intercept console.debug
    console.debug = function (...args: any[]) {
      self.originalConsole.debug.apply(console, args);
      self.capture("debug", args);
    };
  }

  private capture(level: string, args: any[]): void {
    const message = this.formatMessage(args);
    const source = this.getSource();

    const entry: ConsoleLogEntry = {
      level,
      message,
      source,
      timestamp: Date.now(),
      url: window.location.href,
    };

    this.buffer.push(entry);

    // Send immediately if buffer is full
    if (this.buffer.length >= this.maxBatchSize) {
      this.sendBatch();
    }
  }

  private formatMessage(args: any[]): string {
    return args
      .map((arg) => {
        if (typeof arg === "object") {
          try {
            return JSON.stringify(arg, null, 2);
          } catch (e) {
            return String(arg);
          }
        }
        return String(arg);
      })
      .join(" ");
  }

  private getSource(): string {
    try {
      const stack = new Error().stack;
      if (!stack) return "";

      // Parse stack trace to get calling file and line
      const lines = stack.split("\n");
      // Skip first 3 lines (Error, getSource, capture)
      for (let i = 3; i < lines.length; i++) {
        const line = lines[i];
        // Match file:line:col pattern
        const match = line.match(/(?:https?:\/\/[^\/]+)?([^\s]+):(\d+):(\d+)/);
        if (match) {
          const [, file, lineNum, col] = match;
          // Clean up file path
          const cleanFile = file.split("/").slice(-2).join("/");
          return `${cleanFile}:${lineNum}:${col}`;
        }
      }
    } catch (e) {
      // Ignore errors
    }
    return "";
  }

  private startBatchSender(): void {
    setInterval(() => {
      if (this.buffer.length > 0) {
        this.sendBatch();
      }
    }, this.batchInterval);
  }

  private async sendBatch(): Promise<void> {
    if (this.buffer.length === 0) return;

    const logs = this.buffer.splice(0, this.maxBatchSize);

    try {
      const response = await fetch(this.apiEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ logs }),
      });

      if (!response.ok) {
        // Use original console to avoid recursion
        this.originalConsole.warn(
          `[Console Interceptor] Failed to send logs: ${response.status}`,
        );
      }
    } catch (error) {
      // Use original console to avoid recursion
      this.originalConsole.warn("[Console Interceptor] Network error:", error);
    }
  }
}

// Auto-initialize when script loads
if (typeof window !== "undefined") {
  new ConsoleInterceptor();
}
