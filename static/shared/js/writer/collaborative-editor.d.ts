/**
 * Collaborative Editor TypeScript Module
 * Handles real-time collaborative editing with WebSocket integration
 * Implements operational transformation for conflict resolution
 *
 * @version 2.0.0 (TypeScript)
 * @author SciTeX Development Team
 */
export declare class CollaborativeEditor {
    private documentId;
    private editorElement;
    private socket;
    private isConnected;
    private activeUsers;
    private documentVersion;
    private userId;
    private userList;
    private connectionStatus;
    private collaborationToggle;
    /**
     * Creates a new CollaborativeEditor instance
     *
     * @param documentId - The document ID for collaboration
     * @param editorElementId - The ID of the editor textarea element
     */
    constructor(documentId: string, editorElementId: string);
    /**
     * Initialize WebSocket connection for real-time collaboration
     * @private
     */
    private initializeWebSocket;
    /**
     * Handle incoming WebSocket messages
     * @private
     */
    private handleWebSocketMessage;
    /**
     * Initialize event listeners for the editor
     * @private
     */
    private initializeEventListeners;
    /**
     * Initialize UI components
     * @private
     */
    private initializeUI;
    /**
     * Handle initial document state
     * @private
     */
    private handleDocumentState;
    /**
     * Handle text changes from the local editor
     * @private
     */
    private handleTextChange;
    /**
     * Handle remote text changes
     * @private
     */
    private handleRemoteTextChange;
    /**
     * Apply remote operation to local editor
     * @private
     */
    private applyRemoteOperation;
    /**
     * Handle selection changes
     * @private
     */
    private handleSelectionChange;
    /**
     * Handle remote selection changes
     * @private
     */
    private handleRemoteSelectionChange;
    /**
     * Handle cursor position changes
     * @private
     */
    private handleRemoteCursorPosition;
    /**
     * Handle user joined event
     * @private
     */
    private handleUserJoined;
    /**
     * Handle user left event
     * @private
     */
    private handleUserLeft;
    /**
     * Send operation to server
     * @private
     */
    private sendOperation;
    /**
     * Send message to WebSocket
     * @private
     */
    private sendMessage;
    /**
     * Request current document state
     * @private
     */
    private requestDocumentState;
    /**
     * Update connection status UI
     * @private
     */
    private updateConnectionStatus;
    /**
     * Render active users list
     * @private
     */
    private renderActiveUsers;
    /**
     * Get consistent color for user
     * @private
     */
    private getUserColor;
    /**
     * Show cursor indicator for remote users
     * @private
     */
    private showCursorIndicator;
    /**
     * Remove cursor indicator
     * @private
     */
    private removeCursorIndicator;
    /**
     * Show selection overlay for remote users
     * @private
     */
    private showSelectionOverlay;
    /**
     * Show user action notification
     * @private
     */
    private showUserAction;
    /**
     * Show general notification
     * @private
     */
    private showNotification;
    /**
     * Add collaboration controls to the UI
     * @private
     */
    private addCollaborationControls;
    /**
     * Toggle collaboration mode
     * @private
     */
    private toggleCollaboration;
    /**
     * Handle keyboard shortcuts
     * @private
     */
    private handleKeyboardShortcuts;
    /**
     * Save document
     * @private
     */
    private saveDocument;
    /**
     * Share document
     * @private
     */
    private shareDocument;
    /**
     * Show version history
     * @private
     */
    private showVersionHistory;
    /**
     * Cleanup and disconnect
     */
    destroy(): void;
}
declare global {
    interface Window {
        collaborativeEditor?: CollaborativeEditor;
        CollaborativeEditor: typeof CollaborativeEditor;
    }
}
//# sourceMappingURL=collaborative-editor.d.ts.map