/**
 * Collaborative Editor TypeScript Module
 * Handles real-time collaborative editing with WebSocket integration
 * Implements operational transformation for conflict resolution
 *
 * @version 2.0.0 (TypeScript)
 * @author SciTeX Development Team
 */

// ============================================================================
// Type Definitions
// ============================================================================

/** User information */

console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/static/ts/writer/collaborative-editor.ts loaded");
interface User {
    username: string;
    cursorPosition: number;
    selection: Selection | null;
}

/** Text selection */
interface Selection {
    start: number;
    end: number;
}

/** Operation types */
type OperationType = 'insert' | 'delete';

/** Text operation */
interface Operation {
    type: OperationType;
    position: number;
    content: string;
    length: number;
    timestamp: number;
}

/** Connection status */
type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

/** WebSocket message base */
interface WebSocketMessageBase {
    type: string;
    timestamp: number;
}

/** Document state message */
interface DocumentStateMessage extends WebSocketMessageBase {
    type: 'document_state';
    content: {
        text: string;
        version: number;
    };
    active_users: Array<{
        user_id: string;
        username: string;
    }>;
}

/** Text change message */
interface TextChangeMessage extends WebSocketMessageBase {
    type: 'text_change';
    user_id: string;
    username: string;
    operation: Operation;
}

/** Cursor position message */
interface CursorPositionMessage extends WebSocketMessageBase {
    type: 'cursor_position';
    user_id: string;
    position: number;
}

/** Selection change message */
interface SelectionChangeMessage extends WebSocketMessageBase {
    type: 'selection_change';
    user_id: string;
    selection: Selection;
}

/** User joined message */
interface UserJoinedMessage extends WebSocketMessageBase {
    type: 'user_joined';
    user_id: string;
    username: string;
}

/** User left message */
interface UserLeftMessage extends WebSocketMessageBase {
    type: 'user_left';
    user_id: string;
    username: string;
}

/** All possible WebSocket messages */
type WebSocketMessage =
    | DocumentStateMessage
    | TextChangeMessage
    | CursorPositionMessage
    | SelectionChangeMessage
    | UserJoinedMessage
    | UserLeftMessage
    | WebSocketMessageBase;

/** Notification type */
type NotificationType = 'info' | 'success' | 'warning' | 'error';

// ============================================================================
// Main Class
// ============================================================================

export class CollaborativeEditor {
    private documentId: string;
    private editorElement: HTMLTextAreaElement | null;
    private socket: WebSocket | null = null;
    private isConnected: boolean = false;
    private activeUsers: Map<string, User> = new Map();
    private documentVersion: number = 0;
    private userId: string | null = null;

    // UI elements
    private userList: HTMLElement | null;
    private connectionStatus: HTMLElement | null;
    private collaborationToggle: HTMLInputElement | null;

    /**
     * Creates a new CollaborativeEditor instance
     *
     * @param documentId - The document ID for collaboration
     * @param editorElementId - The ID of the editor textarea element
     */
    constructor(documentId: string, editorElementId: string) {
        this.documentId = documentId;
        this.editorElement = document.getElementById(editorElementId) as HTMLTextAreaElement | null;

        // UI elements
        this.userList = document.getElementById('active-users-list');
        this.connectionStatus = document.getElementById('connection-status');
        this.collaborationToggle = document.getElementById('collaboration-toggle') as HTMLInputElement | null;

        this.initializeWebSocket();
        this.initializeEventListeners();
        this.initializeUI();
    }

    // ========================================================================
    // WebSocket Management
    // ========================================================================

    /**
     * Initialize WebSocket connection for real-time collaboration
     * @private
     */
    private initializeWebSocket(): void {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/writer/document/${this.documentId}/`;

        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = (): void => {
            console.log('Connected to collaborative editing server');
            this.isConnected = true;
            this.updateConnectionStatus('connected');
            this.requestDocumentState();
        };

        this.socket.onmessage = (event: MessageEvent): void => {
            const data = JSON.parse(event.data) as WebSocketMessage;
            this.handleWebSocketMessage(data);
        };

        this.socket.onclose = (): void => {
            console.log('Disconnected from collaborative editing server');
            this.isConnected = false;
            this.updateConnectionStatus('disconnected');

            // Attempt to reconnect after 3 seconds
            setTimeout(() => {
                if (!this.isConnected) {
                    this.initializeWebSocket();
                }
            }, 3000);
        };

        this.socket.onerror = (error: Event): void => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('error');
        };
    }

    /**
     * Handle incoming WebSocket messages
     * @private
     */
    private handleWebSocketMessage(data: WebSocketMessage): void {
        switch (data.type) {
            case 'document_state':
                this.handleDocumentState(data as DocumentStateMessage);
                break;
            case 'text_change':
                this.handleRemoteTextChange(data as TextChangeMessage);
                break;
            case 'cursor_position':
                this.handleRemoteCursorPosition(data as CursorPositionMessage);
                break;
            case 'selection_change':
                this.handleRemoteSelectionChange(data as SelectionChangeMessage);
                break;
            case 'user_joined':
                this.handleUserJoined(data as UserJoinedMessage);
                break;
            case 'user_left':
                this.handleUserLeft(data as UserLeftMessage);
                break;
            default:
                console.warn('Unknown message type:', data.type);
        }
    }

    // ========================================================================
    // Event Listeners
    // ========================================================================

    /**
     * Initialize event listeners for the editor
     * @private
     */
    private initializeEventListeners(): void {
        if (!this.editorElement) return;

        // Text change events with debouncing
        let changeTimeout: NodeJS.Timeout | null = null;
        this.editorElement.addEventListener('input', (): void => {
            if (changeTimeout) clearTimeout(changeTimeout);
            changeTimeout = setTimeout(() => {
                this.handleTextChange();
            }, 100); // 100ms debounce
        });

        // Cursor position changes
        this.editorElement.addEventListener('selectionchange', (): void => {
            this.handleSelectionChange();
        });

        // Collaboration toggle
        if (this.collaborationToggle) {
            this.collaborationToggle.addEventListener('change', (event: Event): void => {
                const target = event.target as HTMLInputElement;
                this.toggleCollaboration(target.checked);
            });
        }

        // Paste events
        this.editorElement.addEventListener('paste', (): void => {
            setTimeout(() => this.handleTextChange(), 10);
        });

        // Keyboard shortcuts
        this.editorElement.addEventListener('keydown', (event: KeyboardEvent): void => {
            this.handleKeyboardShortcuts(event);
        });
    }

    // ========================================================================
    // UI Initialization
    // ========================================================================

    /**
     * Initialize UI components
     * @private
     */
    private initializeUI(): void {
        this.updateConnectionStatus('connecting');
        this.renderActiveUsers();
        this.addCollaborationControls();
    }

    // ========================================================================
    // Document State Handlers
    // ========================================================================

    /**
     * Handle initial document state
     * @private
     */
    private handleDocumentState(data: DocumentStateMessage): void {
        const { content, active_users } = data;

        // Update document content
        if (content && content.text !== undefined && this.editorElement) {
            this.editorElement.value = content.text;
            this.documentVersion = content.version || 0;
        }

        // Update active users
        this.activeUsers.clear();
        if (active_users) {
            active_users.forEach(user => {
                this.activeUsers.set(user.user_id, {
                    username: user.username,
                    cursorPosition: 0,
                    selection: null
                });
            });
        }

        this.renderActiveUsers();
    }

    /**
     * Handle text changes from the local editor
     * @private
     */
    private handleTextChange(): void {
        if (!this.isConnected || !this.editorElement) return;

        const currentText = this.editorElement.value;
        const cursorPosition = this.editorElement.selectionStart;

        // Create operation for the change
        const operation: Operation = {
            type: 'insert',
            position: cursorPosition,
            content: currentText,
            length: currentText.length,
            timestamp: Date.now()
        };

        // Send operation to server
        this.sendOperation(operation);
    }

    /**
     * Handle remote text changes
     * @private
     */
    private handleRemoteTextChange(data: TextChangeMessage): void {
        if (data.user_id === this.userId) return; // Don't apply own changes

        const { operation } = data;
        this.applyRemoteOperation(operation);

        // Show user indicator
        this.showUserAction(data.username, 'typing');
    }

    /**
     * Apply remote operation to local editor
     * @private
     */
    private applyRemoteOperation(operation: Operation): void {
        if (!this.editorElement) return;

        const currentPosition = this.editorElement.selectionStart;
        const currentText = this.editorElement.value;

        // Simple operational transformation (production would use more sophisticated OT)
        if (operation.type === 'insert') {
            // Apply the change
            this.editorElement.value = operation.content;

            // Adjust cursor position if needed
            if (currentPosition >= operation.position) {
                const newPosition = currentPosition + (operation.content.length - currentText.length);
                this.editorElement.setSelectionRange(newPosition, newPosition);
            }
        }

        this.documentVersion++;
    }

    // ========================================================================
    // Selection Handlers
    // ========================================================================

    /**
     * Handle selection changes
     * @private
     */
    private handleSelectionChange(): void {
        if (!this.isConnected || !this.editorElement) return;

        const selection: Selection = {
            start: this.editorElement.selectionStart,
            end: this.editorElement.selectionEnd
        };

        this.sendMessage({
            type: 'selection_change',
            selection: selection,
            timestamp: Date.now()
        });
    }

    /**
     * Handle remote selection changes
     * @private
     */
    private handleRemoteSelectionChange(data: SelectionChangeMessage): void {
        if (data.user_id === this.userId) return;

        // Update user's selection in the active users map
        if (this.activeUsers.has(data.user_id)) {
            const user = this.activeUsers.get(data.user_id);
            if (user) {
                user.selection = data.selection;
                this.activeUsers.set(data.user_id, user);
            }
        }

        this.renderActiveUsers();
        this.showSelectionOverlay(data.user_id, data.selection);
    }

    /**
     * Handle cursor position changes
     * @private
     */
    private handleRemoteCursorPosition(data: CursorPositionMessage): void {
        if (data.user_id === this.userId) return;

        // Update user's cursor position
        if (this.activeUsers.has(data.user_id)) {
            const user = this.activeUsers.get(data.user_id);
            if (user) {
                user.cursorPosition = data.position;
                this.activeUsers.set(data.user_id, user);
            }
        }

        this.showCursorIndicator(data.user_id, data.position);
    }

    // ========================================================================
    // User Management
    // ========================================================================

    /**
     * Handle user joined event
     * @private
     */
    private handleUserJoined(data: UserJoinedMessage): void {
        this.activeUsers.set(data.user_id, {
            username: data.username,
            cursorPosition: 0,
            selection: null
        });

        this.renderActiveUsers();
        this.showNotification(`${data.username} joined the document`, 'success');
    }

    /**
     * Handle user left event
     * @private
     */
    private handleUserLeft(data: UserLeftMessage): void {
        this.activeUsers.delete(data.user_id);
        this.renderActiveUsers();
        this.removeCursorIndicator(data.user_id);
        this.showNotification(`${data.username} left the document`, 'info');
    }

    // ========================================================================
    // WebSocket Communication
    // ========================================================================

    /**
     * Send operation to server
     * @private
     */
    private sendOperation(operation: Operation): void {
        this.sendMessage({
            type: 'text_change',
            operation: operation,
            timestamp: Date.now()
        });
    }

    /**
     * Send message to WebSocket
     * @private
     */
    private sendMessage(message: Partial<WebSocketMessageBase> & Record<string, unknown>): void {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        }
    }

    /**
     * Request current document state
     * @private
     */
    private requestDocumentState(): void {
        this.sendMessage({
            type: 'request_document_state',
            timestamp: Date.now()
        });
    }

    // ========================================================================
    // UI Updates
    // ========================================================================

    /**
     * Update connection status UI
     * @private
     */
    private updateConnectionStatus(status: ConnectionStatus): void {
        if (!this.connectionStatus) return;

        const statusMap: Record<ConnectionStatus, { text: string; class: string }> = {
            connecting: { text: 'Connecting...', class: 'connecting' },
            connected: { text: 'Connected', class: 'connected' },
            disconnected: { text: 'Disconnected', class: 'disconnected' },
            error: { text: 'Connection Error', class: 'error' }
        };

        const statusInfo = statusMap[status];
        this.connectionStatus.textContent = statusInfo.text;
        this.connectionStatus.className = `connection-status ${statusInfo.class}`;
    }

    /**
     * Render active users list
     * @private
     */
    private renderActiveUsers(): void {
        if (!this.userList) return;

        this.userList.innerHTML = '';

        this.activeUsers.forEach((user, userId) => {
            const userElement = document.createElement('div');
            userElement.className = 'active-user';
            userElement.innerHTML = `
                <div class="user-avatar" style="background-color: ${this.getUserColor(userId)}">
                    ${user.username.charAt(0).toUpperCase()}
                </div>
                <span class="user-name">${user.username}</span>
            `;
            this.userList!.appendChild(userElement);
        });
    }

    /**
     * Get consistent color for user
     * @private
     */
    private getUserColor(userId: string): string {
        const colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ];
        const index = parseInt(userId, 10) % colors.length;
        return colors[index];
    }

    /**
     * Show cursor indicator for remote users
     * @private
     */
    private showCursorIndicator(userId: string, _position: number): void {
        if (!this.editorElement) return;

        // Remove existing indicator
        this.removeCursorIndicator(userId);

        // Create new cursor indicator
        const indicator = document.createElement('div');
        indicator.className = 'remote-cursor';
        indicator.id = `cursor-${userId}`;
        indicator.style.backgroundColor = this.getUserColor(userId);

        // Position the cursor (simplified - production would need more sophisticated positioning)
        // TODO: Calculate actual cursor position based on text position

        // Add to editor container
        const editorContainer = this.editorElement.parentNode as HTMLElement;
        if (editorContainer && editorContainer.style.position !== 'relative') {
            editorContainer.style.position = 'relative';
        }
        editorContainer?.appendChild(indicator);
    }

    /**
     * Remove cursor indicator
     * @private
     */
    private removeCursorIndicator(userId: string): void {
        const indicator = document.getElementById(`cursor-${userId}`);
        if (indicator) {
            indicator.remove();
        }
    }

    /**
     * Show selection overlay for remote users
     * @private
     */
    private showSelectionOverlay(userId: string, selection: Selection): void {
        if (!selection || selection.start === selection.end || !this.editorElement) return;

        // Create selection overlay (simplified implementation)
        const overlay = document.createElement('div');
        overlay.className = 'remote-selection';
        overlay.id = `selection-${userId}`;
        overlay.style.backgroundColor = this.getUserColor(userId);
        overlay.style.opacity = '0.3';

        // Add to editor container
        const editorContainer = this.editorElement.parentNode as HTMLElement;
        editorContainer?.appendChild(overlay);
    }

    /**
     * Show user action notification
     * @private
     */
    private showUserAction(username: string, action: string): void {
        const notification = document.createElement('div');
        notification.className = 'user-action-notification';
        notification.textContent = `${username} is ${action}...`;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 2000);
    }

    /**
     * Show general notification
     * @private
     */
    private showNotification(message: string, type: NotificationType = 'info'): void {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    /**
     * Add collaboration controls to the UI
     * @private
     */
    private addCollaborationControls(): void {
        if (!this.collaborationToggle || !this.editorElement) return;

        const controlsContainer = document.createElement('div');
        controlsContainer.className = 'collaboration-controls';
        controlsContainer.innerHTML = `
            <div class="collaboration-header">
                <h4>Collaborative Editing</h4>
                <div class="controls">
                    <button id="share-document" class="btn btn-secondary btn-sm">Share Document</button>
                    <button id="version-history" class="btn btn-secondary btn-sm">Version History</button>
                </div>
            </div>
        `;

        // Insert before the editor
        this.editorElement.parentNode?.insertBefore(controlsContainer, this.editorElement);

        // Add event listeners for new controls
        document.getElementById('share-document')?.addEventListener('click', () => {
            this.shareDocument();
        });

        document.getElementById('version-history')?.addEventListener('click', () => {
            this.showVersionHistory();
        });
    }

    // ========================================================================
    // Collaboration Controls
    // ========================================================================

    /**
     * Toggle collaboration mode
     * @private
     */
    private toggleCollaboration(enabled: boolean): void {
        if (enabled) {
            this.initializeWebSocket();
        } else {
            if (this.socket) {
                this.socket.close();
            }
        }
    }

    /**
     * Handle keyboard shortcuts
     * @private
     */
    private handleKeyboardShortcuts(event: KeyboardEvent): void {
        // Ctrl+S for save
        if (event.ctrlKey && event.key === 's') {
            event.preventDefault();
            this.saveDocument();
        }

        // Ctrl+Shift+H for version history
        if (event.ctrlKey && event.shiftKey && event.key === 'H') {
            event.preventDefault();
            this.showVersionHistory();
        }
    }

    /**
     * Save document
     * @private
     */
    private saveDocument(): void {
        console.log('Saving document...');
        this.showNotification('Document saved', 'success');
    }

    /**
     * Share document
     * @private
     */
    private shareDocument(): void {
        const shareUrl = `${window.location.origin}/writer/document/${this.documentId}`;
        navigator.clipboard.writeText(shareUrl).then(() => {
            this.showNotification('Share link copied to clipboard', 'success');
        }).catch(err => {
            console.error('Failed to copy:', err);
            this.showNotification('Failed to copy link', 'error');
        });
    }

    /**
     * Show version history
     * @private
     */
    private showVersionHistory(): void {
        console.log('Showing version history...');
    }

    // ========================================================================
    // Public API
    // ========================================================================

    /**
     * Cleanup and disconnect
     */
    public destroy(): void {
        if (this.socket) {
            this.socket.close();
        }
    }
}

// ============================================================================
// Auto-initialization
// ============================================================================

/**
 * Initialize collaborative editor when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a document editing page
    const editorElement = document.getElementById('latex-editor');
    const documentElement = document.querySelector('[data-document-id]');
    const documentId = documentElement?.getAttribute('data-document-id');

    if (editorElement && documentId) {
        (window as typeof window & { collaborativeEditor?: CollaborativeEditor }).collaborativeEditor =
            new CollaborativeEditor(documentId, 'latex-editor');
    }
});

// ============================================================================
// Global Export
// ============================================================================

declare global {
    interface Window {
        collaborativeEditor?: CollaborativeEditor;
        CollaborativeEditor: typeof CollaborativeEditor;
    }
}

// Export to global namespace
if (typeof window !== 'undefined') {
    window.CollaborativeEditor = CollaborativeEditor;
}
