/**
 * Writer Collaborative Editing Integration
 * Main entry point for real-time collaborative editing in Writer
 *
 * Integrates:
 * - WebSocket client
 * - OT operations
 * - Monaco editor
 * - Cursor rendering
 * - Presence indicators
 *
 * @version 1.0.0
 * @author SciTeX Development Team
 */

import { WebSocketCollaborationClient, Collaborator, RemoteCursor } from './websocket-client.js';
import { TextOperation } from './ot/operations.js';

console.log("[DEBUG] Writer Collaboration Integration loaded");

// ============================================================================
// Global Type Declarations
// ============================================================================

declare global {
  interface Window {
    WRITER_CONFIG?: {
      projectId: number;
      userId: number;
      username: string;
    };
    monacoEditors?: Map<string, any>;
    writerCollaboration?: WriterCollaboration;
    monaco?: any;
  }
}

// ============================================================================
// Remote Cursor Decoration
// ============================================================================

class RemoteCursorManager {
  private editor: any;
  private decorations: Map<number, string[]> = new Map();
  private widgets: Map<number, any> = new Map();

  constructor(editor: any) {
    this.editor = editor;
  }

  updateCursor(cursor: RemoteCursor): void {
    // Remove old decorations
    const oldDecorations = this.decorations.get(cursor.userId) || [];
    this.decorations.set(
      cursor.userId,
      this.editor.deltaDecorations(oldDecorations, [
        {
          range: new window.monaco.Range(
            cursor.lineNumber || 1,
            cursor.column || 1,
            cursor.lineNumber || 1,
            cursor.column || 1
          ),
          options: {
            className: `remote-cursor remote-cursor-${cursor.userId}`,
            stickiness: window.monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
          }
        }
      ])
    );

    // Update cursor label widget
    this.updateCursorWidget(cursor);
  }

  private updateCursorWidget(cursor: RemoteCursor): void {
    // Remove old widget if exists
    const oldWidget = this.widgets.get(cursor.userId);
    if (oldWidget) {
      this.editor.removeContentWidget(oldWidget);
    }

    // Create new widget
    const widget = {
      getId: () => `remote-cursor-widget-${cursor.userId}`,
      getDomNode: () => {
        const node = document.createElement('div');
        node.className = 'remote-cursor-label';
        node.style.background = cursor.color || '#4ECDC4';
        node.style.color = '#fff';
        node.style.padding = '2px 6px';
        node.style.borderRadius = '3px';
        node.style.fontSize = '11px';
        node.style.fontWeight = 'bold';
        node.style.pointerEvents = 'none';
        node.style.zIndex = '100';
        node.textContent = cursor.username;
        return node;
      },
      getPosition: () => ({
        position: {
          lineNumber: cursor.lineNumber || 1,
          column: cursor.column || 1
        },
        preference: [
          window.monaco.editor.ContentWidgetPositionPreference.ABOVE,
          window.monaco.editor.ContentWidgetPositionPreference.BELOW
        ]
      })
    };

    this.editor.addContentWidget(widget);
    this.widgets.set(cursor.userId, widget);
  }

  removeCursor(userId: number): void {
    // Remove decorations
    const decorations = this.decorations.get(userId) || [];
    this.editor.deltaDecorations(decorations, []);
    this.decorations.delete(userId);

    // Remove widget
    const widget = this.widgets.get(userId);
    if (widget) {
      this.editor.removeContentWidget(widget);
      this.widgets.delete(userId);
    }
  }

  clear(): void {
    this.decorations.forEach((decorations) => {
      this.editor.deltaDecorations(decorations, []);
    });
    this.decorations.clear();

    this.widgets.forEach((widget) => {
      this.editor.removeContentWidget(widget);
    });
    this.widgets.clear();
  }
}

// ============================================================================
// Writer Collaboration Manager
// ============================================================================

class WriterCollaboration {
  private wsClient: WebSocketCollaborationClient | null = null;
  cursorManagers: Map<string, RemoteCursorManager> = new Map();
  private isEnabled: boolean = false;

  private changeListeners: Map<string, any> = new Map();
  private cursorListeners: Map<string, any> = new Map();

  constructor() {
    console.log('[WriterCollab] Initializing collaboration');
  }

  /**
   * Enable collaborative editing
   */
  enable(manuscriptId: number): void {
    if (this.isEnabled) {
      console.log('[WriterCollab] Already enabled');
      return;
    }

    console.log('[WriterCollab] Enabling collaboration for manuscript:', manuscriptId);
    this.isEnabled = true;

    // Create WebSocket client
    this.wsClient = new WebSocketCollaborationClient(manuscriptId, {
      onConnected: () => this.handleConnected(),
      onDisconnected: () => this.handleDisconnected(),
      onError: (error) => this.handleError(error),
      onUserJoined: (user) => this.handleUserJoined(user),
      onUserLeft: (userId) => this.handleUserLeft(userId),
      onCursorUpdate: (cursor) => this.handleCursorUpdate(cursor),
      onSectionLocked: (section, userId, username) => this.handleSectionLocked(section, userId, username),
      onSectionUnlocked: (section) => this.handleSectionUnlocked(section),
      onApplyOperation: (section, operation) => this.applyRemoteOperation(section, operation),
      onCollaboratorsUpdate: (collaborators) => this.handleCollaboratorsUpdate(collaborators)
    });

    // Connect to server
    this.wsClient.connect();

    // Setup editor listeners
    this.setupEditorListeners();

    // Update UI
    this.updateCollaborationUI(true);
  }

  /**
   * Disable collaborative editing
   */
  disable(): void {
    if (!this.isEnabled) {
      return;
    }

    console.log('[WriterCollab] Disabling collaboration');
    this.isEnabled = false;

    // Disconnect WebSocket
    if (this.wsClient) {
      this.wsClient.disconnect();
      this.wsClient = null;
    }

    // Remove editor listeners
    this.removeEditorListeners();

    // Clear cursor managers
    this.cursorManagers.forEach(manager => manager.clear());
    this.cursorManagers.clear();

    // Update UI
    this.updateCollaborationUI(false);
  }

  private setupEditorListeners(): void {
    if (!window.monacoEditors) {
      console.warn('[WriterCollab] Monaco editors not initialized');
      return;
    }

    window.monacoEditors.forEach((editor, section) => {
      // Listen for content changes
      const changeListener = editor.onDidChangeModelContent((event: any) => {
        this.handleEditorChange(section, event, editor);
      });
      this.changeListeners.set(section, changeListener);

      // Listen for cursor position changes
      const cursorListener = editor.onDidChangeCursorPosition((_event: any) => {
        this.handleCursorChange(section, _event);
      });
      this.cursorListeners.set(section, cursorListener);

      // Create cursor manager for this editor
      this.cursorManagers.set(section, new RemoteCursorManager(editor));

      // Send cursor position when focusing
      editor.onDidFocusEditorText(() => {
        this.sendCurrentCursorPosition(section, editor);
      });
    });
  }

  private removeEditorListeners(): void {
    this.changeListeners.forEach(listener => listener.dispose());
    this.changeListeners.clear();

    this.cursorListeners.forEach(listener => listener.dispose());
    this.cursorListeners.clear();
  }

  private handleEditorChange(section: string, event: any, editor: any): void {
    if (!this.wsClient || !this.isEnabled) {
      return;
    }

    // Convert Monaco changes to OT operations
    for (const change of event.changes) {
      const operation = this.monacoChangeToOTOperation(change, editor);
      if (!operation.isNoop()) {
        this.wsClient.applyLocalOperation(section, operation);
      }
    }
  }

  private monacoChangeToOTOperation(change: any, editor: any): TextOperation {
    const operation = new TextOperation();
    const model = editor.getModel();
    const fullText = model.getValue();

    // Calculate position before change
    const startOffset = model.getOffsetAt(change.range.getStartPosition());
    const endOffset = model.getOffsetAt(change.range.getEndPosition());

    // Retain characters before change
    if (startOffset > 0) {
      operation.retain(startOffset);
    }

    // Delete old text if any
    const deletedLength = endOffset - startOffset;
    if (deletedLength > 0) {
      operation.delete(deletedLength);
    }

    // Insert new text if any
    if (change.text.length > 0) {
      operation.insert(change.text);
    }

    // Retain characters after change
    const remainingLength = fullText.length - startOffset - change.text.length;
    if (remainingLength > 0) {
      operation.retain(remainingLength);
    }

    return operation;
  }

  private applyRemoteOperation(section: string, operation: TextOperation): void {
    if (!window.monacoEditors) {
      return;
    }

    const editor = window.monacoEditors.get(section);
    if (!editor) {
      console.warn(`[WriterCollab] Editor not found for section: ${section}`);
      return;
    }

    const model = editor.getModel();
    const currentText = model.getValue();

    // Suppress our own change listeners while applying remote operation
    const changeListener = this.changeListeners.get(section);
    if (changeListener) {
      changeListener.dispose();
    }

    try {
      // Apply operation to text
      const newText = operation.apply(currentText);

      // Update editor
      model.setValue(newText);
    } catch (error) {
      console.error('[WriterCollab] Failed to apply remote operation:', error);
    } finally {
      // Re-enable change listener
      const newListener = editor.onDidChangeModelContent((event: any) => {
        this.handleEditorChange(section, event, editor);
      });
      this.changeListeners.set(section, newListener);
    }
  }

  private handleCursorChange(section: string, _event: any): void {
    if (!this.wsClient || !this.isEnabled) {
      return;
    }

    this.sendCurrentCursorPosition(section, window.monacoEditors?.get(section));
  }

  private sendCurrentCursorPosition(section: string, editor: any): void {
    if (!this.wsClient || !editor) {
      return;
    }

    const position = editor.getPosition();
    const model = editor.getModel();
    const offset = model.getOffsetAt(position);

    this.wsClient.sendCursorPosition({
      section: section,
      position: offset,
      lineNumber: position.lineNumber,
      column: position.column
    });
  }

  private handleConnected(): void {
    console.log('[WriterCollab] Connected to server');
    this.showNotification('Connected to collaboration server', 'success');
  }

  private handleDisconnected(): void {
    console.log('[WriterCollab] Disconnected from server');
    this.showNotification('Disconnected from collaboration server', 'warning');
  }

  private handleError(error: Error): void {
    console.error('[WriterCollab] Error:', error);
    this.showNotification(`Collaboration error: ${error.message}`, 'danger');
  }

  private handleUserJoined(user: Collaborator): void {
    console.log('[WriterCollab] User joined:', user.username);
    this.showNotification(`${user.username} joined`, 'info');
    this.updatePresenceUI();
  }

  private handleUserLeft(userId: number): void {
    console.log('[WriterCollab] User left:', userId);

    // Remove cursor decorations
    this.cursorManagers.forEach(manager => manager.removeCursor(userId));

    this.updatePresenceUI();
  }

  private handleCursorUpdate(cursor: RemoteCursor): void {
    const manager = this.cursorManagers.get(cursor.section);
    if (manager) {
      manager.updateCursor(cursor);
    }
  }

  private handleSectionLocked(section: string, _userId: number, username: string): void {
    console.log(`[WriterCollab] Section ${section} locked by ${username}`);

    // Add visual indication that section is locked
    const sectionEl = document.getElementById(`section-${section}`);
    if (sectionEl) {
      sectionEl.classList.add('section-locked');
      const lockBadge = document.createElement('span');
      lockBadge.className = 'section-lock-badge';
      lockBadge.textContent = `🔒 ${username}`;
      sectionEl.parentElement?.insertBefore(lockBadge, sectionEl);
    }
  }

  private handleSectionUnlocked(section: string): void {
    console.log(`[WriterCollab] Section ${section} unlocked`);

    const sectionEl = document.getElementById(`section-${section}`);
    if (sectionEl) {
      sectionEl.classList.remove('section-locked');
      const lockBadge = sectionEl.parentElement?.querySelector('.section-lock-badge');
      if (lockBadge) {
        lockBadge.remove();
      }
    }
  }

  private handleCollaboratorsUpdate(collaborators: Collaborator[]): void {
    console.log('[WriterCollab] Collaborators updated:', collaborators);
    this.updatePresenceUI();
  }

  private updateCollaborationUI(enabled: boolean): void {
    const statusEl = document.getElementById('collab-status');
    const toggleBtn = document.getElementById('collaboration-toggle');

    if (enabled) {
      statusEl?.classList.remove('hidden');
      statusEl?.classList.add('collab-active');
      toggleBtn?.classList.add('active');
    } else {
      statusEl?.classList.add('hidden');
      statusEl?.classList.remove('collab-active');
      toggleBtn?.classList.remove('active');
    }
  }

  private updatePresenceUI(): void {
    if (!this.wsClient) {
      return;
    }

    const collaborators = this.wsClient.getCollaborators();
    const presenceContainer = document.getElementById('collaborators-list');

    if (!presenceContainer) {
      return;
    }

    presenceContainer.innerHTML = collaborators.map(c => `
      <div class="collaborator-item">
        <span class="collaborator-indicator" style="background-color: ${c.color}"></span>
        <span class="collaborator-name">${c.username}</span>
      </div>
    `).join('');
  }

  private showNotification(message: string, type: string = 'info'): void {
    console.log(`[WriterCollab] ${type.toUpperCase()}: ${message}`);
    // Could integrate with a notification system here
  }

  // ========================================================================
  // Public API
  // ========================================================================

  getStatus(): any {
    return {
      enabled: this.isEnabled,
      connected: this.wsClient?.isConnected() || false,
      collaborators: this.wsClient?.getCollaborators() || []
    };
  }
}

// ============================================================================
// Initialize and Export
// ============================================================================

// Create global instance
window.writerCollaboration = new WriterCollaboration();

// Auto-enable if we're on a writer page with a manuscript
if (window.WRITER_CONFIG?.projectId && window.location.pathname.includes('/writer/')) {
  // Wait for DOM and Monaco to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(() => checkAndEnableCollaboration(), 1000);
    });
  } else {
    setTimeout(() => checkAndEnableCollaboration(), 1000);
  }
}

function checkAndEnableCollaboration(): void {
  // Check if collaboration toggle exists and is enabled
  const toggleBtn = document.getElementById('collaboration-toggle');

  if (toggleBtn && window.WRITER_CONFIG?.projectId) {
    // Auto-enable if toggle is active
    if (toggleBtn.classList.contains('active')) {
      window.writerCollaboration?.enable(window.WRITER_CONFIG.projectId);
    }

    // Listen for toggle clicks
    toggleBtn.addEventListener('click', () => {
      if (window.writerCollaboration?.getStatus().enabled) {
        window.writerCollaboration?.disable();
      } else if (window.WRITER_CONFIG?.projectId) {
        window.writerCollaboration?.enable(window.WRITER_CONFIG.projectId);
      }
    });
  }
}

console.log('[WriterCollab] Module loaded and ready');

export { WriterCollaboration };
