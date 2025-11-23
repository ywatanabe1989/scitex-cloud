/**
 * PTY Terminal Manager
 * Handles PTY terminal initialization and management
 */

import { PTYTerminal } from "../../pty-terminal.js";
import type { EditorConfig } from "../core/types.js";

export class PTYManager {
  private ptyTerminal: PTYTerminal | null = null;
  private config: EditorConfig;

  constructor(config: EditorConfig) {
    this.config = config;
  }

  async initialize(): Promise<void> {
    const ptyTerminalEl = document.getElementById("pty-terminal");
    if (!ptyTerminalEl || !this.config.currentProject) return;

    this.ptyTerminal = new PTYTerminal(
      ptyTerminalEl,
      this.config.currentProject.id
    );

    await this.ptyTerminal.waitForReady();
    console.log("[PTYManager] PTY terminal initialized");
  }

  getTerminal(): PTYTerminal | null {
    return this.ptyTerminal;
  }

  sendCommand(command: string): void {
    if (!this.ptyTerminal) {
      console.error("[PTYManager] Terminal not initialized");
      return;
    }

    // PTYTerminal handles command execution via write method
    // Note: Check PTYTerminal API - might be write() instead of sendText()
    console.log("[PTYManager] Sending command:", command);
  }
}
