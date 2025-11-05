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
// ============================================================================
// Main Class
// ============================================================================
export class CollaborativeEditor {
    documentId;
    editorElement;
    socket = null;
    isConnected = false;
    activeUsers = new Map();
    documentVersion = 0;
    userId = null;
    // UI elements
    userList;
    connectionStatus;
    collaborationToggle;
    /**
     * Creates a new CollaborativeEditor instance
     *
     * @param documentId - The document ID for collaboration
     * @param editorElementId - The ID of the editor textarea element
     */
    constructor(documentId, editorElementId) {
        this.documentId = documentId;
        this.editorElement = document.getElementById(editorElementId);
        // UI elements
        this.userList = document.getElementById('active-users-list');
        this.connectionStatus = document.getElementById('connection-status');
        this.collaborationToggle = document.getElementById('collaboration-toggle');
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
    initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/writer/document/${this.documentId}/`;
        this.socket = new WebSocket(wsUrl);
        this.socket.onopen = () => {
            console.log('Connected to collaborative editing server');
            this.isConnected = true;
            this.updateConnectionStatus('connected');
            this.requestDocumentState();
        };
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        this.socket.onclose = () => {
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
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('error');
        };
    }
    /**
     * Handle incoming WebSocket messages
     * @private
     */
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'document_state':
                this.handleDocumentState(data);
                break;
            case 'text_change':
                this.handleRemoteTextChange(data);
                break;
            case 'cursor_position':
                this.handleRemoteCursorPosition(data);
                break;
            case 'selection_change':
                this.handleRemoteSelectionChange(data);
                break;
            case 'user_joined':
                this.handleUserJoined(data);
                break;
            case 'user_left':
                this.handleUserLeft(data);
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
    initializeEventListeners() {
        if (!this.editorElement)
            return;
        // Text change events with debouncing
        let changeTimeout = null;
        this.editorElement.addEventListener('input', () => {
            if (changeTimeout)
                clearTimeout(changeTimeout);
            changeTimeout = setTimeout(() => {
                this.handleTextChange();
            }, 100); // 100ms debounce
        });
        // Cursor position changes
        this.editorElement.addEventListener('selectionchange', () => {
            this.handleSelectionChange();
        });
        // Collaboration toggle
        if (this.collaborationToggle) {
            this.collaborationToggle.addEventListener('change', (event) => {
                const target = event.target;
                this.toggleCollaboration(target.checked);
            });
        }
        // Paste events
        this.editorElement.addEventListener('paste', () => {
            setTimeout(() => this.handleTextChange(), 10);
        });
        // Keyboard shortcuts
        this.editorElement.addEventListener('keydown', (event) => {
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
    initializeUI() {
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
    handleDocumentState(data) {
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
    handleTextChange() {
        if (!this.isConnected || !this.editorElement)
            return;
        const currentText = this.editorElement.value;
        const cursorPosition = this.editorElement.selectionStart;
        // Create operation for the change
        const operation = {
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
    handleRemoteTextChange(data) {
        if (data.user_id === this.userId)
            return; // Don't apply own changes
        const { operation } = data;
        this.applyRemoteOperation(operation);
        // Show user indicator
        this.showUserAction(data.username, 'typing');
    }
    /**
     * Apply remote operation to local editor
     * @private
     */
    applyRemoteOperation(operation) {
        if (!this.editorElement)
            return;
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
    handleSelectionChange() {
        if (!this.isConnected || !this.editorElement)
            return;
        const selection = {
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
    handleRemoteSelectionChange(data) {
        if (data.user_id === this.userId)
            return;
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
    handleRemoteCursorPosition(data) {
        if (data.user_id === this.userId)
            return;
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
    handleUserJoined(data) {
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
    handleUserLeft(data) {
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
    sendOperation(operation) {
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
    sendMessage(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        }
    }
    /**
     * Request current document state
     * @private
     */
    requestDocumentState() {
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
    updateConnectionStatus(status) {
        if (!this.connectionStatus)
            return;
        const statusMap = {
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
    renderActiveUsers() {
        if (!this.userList)
            return;
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
            this.userList.appendChild(userElement);
        });
    }
    /**
     * Get consistent color for user
     * @private
     */
    getUserColor(userId) {
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
    showCursorIndicator(userId, _position) {
        if (!this.editorElement)
            return;
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
        const editorContainer = this.editorElement.parentNode;
        if (editorContainer && editorContainer.style.position !== 'relative') {
            editorContainer.style.position = 'relative';
        }
        editorContainer?.appendChild(indicator);
    }
    /**
     * Remove cursor indicator
     * @private
     */
    removeCursorIndicator(userId) {
        const indicator = document.getElementById(`cursor-${userId}`);
        if (indicator) {
            indicator.remove();
        }
    }
    /**
     * Show selection overlay for remote users
     * @private
     */
    showSelectionOverlay(userId, selection) {
        if (!selection || selection.start === selection.end || !this.editorElement)
            return;
        // Create selection overlay (simplified implementation)
        const overlay = document.createElement('div');
        overlay.className = 'remote-selection';
        overlay.id = `selection-${userId}`;
        overlay.style.backgroundColor = this.getUserColor(userId);
        overlay.style.opacity = '0.3';
        // Add to editor container
        const editorContainer = this.editorElement.parentNode;
        editorContainer?.appendChild(overlay);
    }
    /**
     * Show user action notification
     * @private
     */
    showUserAction(username, action) {
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
    showNotification(message, type = 'info') {
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
    addCollaborationControls() {
        if (!this.collaborationToggle || !this.editorElement)
            return;
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
    toggleCollaboration(enabled) {
        if (enabled) {
            this.initializeWebSocket();
        }
        else {
            if (this.socket) {
                this.socket.close();
            }
        }
    }
    /**
     * Handle keyboard shortcuts
     * @private
     */
    handleKeyboardShortcuts(event) {
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
    saveDocument() {
        console.log('Saving document...');
        this.showNotification('Document saved', 'success');
    }
    /**
     * Share document
     * @private
     */
    shareDocument() {
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
    showVersionHistory() {
        console.log('Showing version history...');
    }
    // ========================================================================
    // Public API
    // ========================================================================
    /**
     * Cleanup and disconnect
     */
    destroy() {
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
document.addEventListener('DOMContentLoaded', function () {
    // Check if we're on a document editing page
    const editorElement = document.getElementById('latex-editor');
    const documentElement = document.querySelector('[data-document-id]');
    const documentId = documentElement?.getAttribute('data-document-id');
    if (editorElement && documentId) {
        window.collaborativeEditor =
            new CollaborativeEditor(documentId, 'latex-editor');
    }
});
// Export to global namespace
if (typeof window !== 'undefined') {
    window.CollaborativeEditor = CollaborativeEditor;
}
//# sourceMappingURL=collaborative-editor.js.map