/**
 * Real PTY Terminal with xterm.js
 * Provides full interactive terminal with IPython, vim, etc.
 */

console.log("[DEBUG] apps/code_app/static/code_app/ts/pty-terminal.ts loaded");

export class PTYTerminal {
  private term: any;
  private ws: WebSocket | null = null;
  private projectId: number;
  private imageContainer: HTMLElement | null = null;

  constructor(containerEl: HTMLElement, projectId: number) {
    this.projectId = projectId;
    this.initXterm(containerEl);
    this.connect();
  }

  private async initXterm(containerEl: HTMLElement): Promise<void> {
    // Wait for xterm.js to load
    while (!(window as any).Terminal) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    const Terminal = (window as any).Terminal;
    const FitAddon = (window as any).FitAddon?.FitAddon;
    const ImageAddon = (window as any).ImageAddon?.ImageAddon;

    this.term = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: "'JetBrains Mono', 'Monaco', 'Menlo', monospace",
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
        cursor: '#d4d4d4',
        black: '#000000',
        red: '#cd0000',
        green: '#00cd00',
        yellow: '#cdcd00',
        blue: '#0000ee',
        magenta: '#cd00cd',
        cyan: '#00cdcd',
        white: '#e5e5e5',
        brightBlack: '#7f7f7f',
        brightRed: '#ff0000',
        brightGreen: '#00ff00',
        brightYellow: '#ffff00',
        brightBlue: '#5c5cff',
        brightMagenta: '#ff00ff',
        brightCyan: '#00ffff',
        brightWhite: '#ffffff',
      },
      allowProposedApi: true,
    });

    this.term.open(containerEl);

    // Fit addon for auto-resize
    if (FitAddon) {
      const fitAddon = new FitAddon();
      this.term.loadAddon(fitAddon);
      fitAddon.fit();

      // Resize on window resize
      window.addEventListener('resize', () => {
        fitAddon.fit();
        this.sendResize();
      });
    }

    // Image addon for inline images (matplotlib, PIL, etc.)
    if (ImageAddon) {
      try {
        const imageAddon = new ImageAddon();
        this.term.loadAddon(imageAddon);
        console.log('[PTY] ✓ ImageAddon loaded successfully - inline images enabled');
      } catch (err) {
        console.error('[PTY] ✗ Failed to load ImageAddon:', err);
      }
    } else {
      console.warn('[PTY] ⚠ ImageAddon not available - window.ImageAddon is undefined');
    }

    // Handle user input
    this.term.onData((data: string) => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(data);
      }
    });

    // Add clipboard support (Ctrl+Shift+C to copy, Ctrl+Shift+V to paste)
    this.term.attachCustomKeyEventHandler((event: KeyboardEvent) => {
      // Ctrl+Shift+C: Copy selected text
      if (event.ctrlKey && event.shiftKey && event.key === 'C') {
        const selection = this.term.getSelection();
        if (selection) {
          navigator.clipboard.writeText(selection);
          console.log('[PTY] Copied to clipboard:', selection.substring(0, 50) + '...');
        }
        return false; // Prevent default
      }

      // Ctrl+Shift+V: Paste from clipboard
      if (event.ctrlKey && event.shiftKey && event.key === 'V') {
        navigator.clipboard.readText().then(text => {
          if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(text);
          }
        });
        return false; // Prevent default
      }

      return true; // Allow other keys
    });

    console.log('[PTY] xterm.js initialized');
  }

  private connect(): void {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/code/terminal/?project_id=${this.projectId}`;

    console.log('[PTY] Connecting to:', wsUrl);

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('[PTY] WebSocket connected');
      this.term.write('\r\n\x1b[1;32m[SciTeX Cloud Code]\x1b[0m Connected to terminal\r\n\r\n');
      this.sendResize();
    };

    this.ws.onmessage = (event) => {
      // Simply write all data to terminal - no inline image rendering
      this.term.write(event.data);
    };

    this.ws.onerror = (error) => {
      console.error('[PTY] WebSocket error:', error);
      this.term.write('\r\n\x1b[1;31mTerminal connection error\x1b[0m\r\n');
    };

    this.ws.onclose = () => {
      console.log('[PTY] WebSocket closed');
      this.term.write('\r\n\x1b[1;33m[Disconnected]\x1b[0m\r\n');

      // Attempt reconnect after 3 seconds
      setTimeout(() => this.connect(), 3000);
    };
  }

  private sendResize(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN && this.term) {
      const rows = this.term.rows;
      const cols = this.term.cols;
      this.ws.send(`resize:${rows}:${cols}`);
    }
  }

  public write(text: string): void {
    if (this.term) {
      this.term.write(text);
    }
  }

  public writeln(text: string): void {
    if (this.term) {
      this.term.writeln(text);
    }
  }

  public clear(): void {
    if (this.term) {
      this.term.clear();
      console.log('[PTY] Terminal cleared');
    }

    // Also clear inline images and hide panel
    if (this.imageContainer) {
      this.imageContainer.innerHTML = '';
      this.imageContainer.style.display = 'none';
      console.log('[PTY] Inline images cleared');
    }
  }

  public executeCommand(command: string): void {
    /**
     * Execute a command in the PTY terminal
     * This sends the command as if the user typed it and pressed Enter
     */
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      // Send command followed by Enter (\r)
      this.ws.send(command + '\r');
      console.log('[PTY] Executing command:', command);
    } else {
      console.error('[PTY] Cannot execute command - WebSocket not connected');
    }
  }

  public destroy(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    if (this.term) {
      this.term.dispose();
    }
  }
}
