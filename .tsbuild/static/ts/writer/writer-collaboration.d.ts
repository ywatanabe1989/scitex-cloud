/**
 * SciTeX Writer - Real-Time Collaboration (TypeScript)
 * WebSocket client for collaborative editing
 *
 * @version 2.0.0 (TypeScript)
 * @author SciTeX Development Team
 */
declare global {
    interface Window {
        WriterCollaboration: typeof WriterCollaboration;
        currentSection?: string;
        switchToSection?: (section: string) => void;
        hasUnsavedChanges?: boolean;
        convertFromLatex?: (section: string, latex: string) => string;
        textPreview?: unknown;
        updateWordCount?: () => void;
        showToast?: (message: string, type: string) => void;
    }
}
export declare class WriterCollaboration {
    private manuscriptId;
    private userId;
    private username;
    private ws;
    private reconnectAttempts;
    private readonly maxReconnectAttempts;
    private readonly reconnectDelay;
    private collaborators;
    private lockedSections;
    /**
     * Creates a new WriterCollaboration instance
     *
     * @param manuscriptId - The manuscript ID
     * @param userId - Current user's ID
     * @param username - Current user's username
     */
    constructor(manuscriptId: string, userId: string, username: string);
    /**
     * Initialize the collaboration system
     * @private
     */
    private init;
    /**
     * Connect to WebSocket server
     * @private
     */
    private connect;
    /**
     * Attempt to reconnect to WebSocket
     * @private
     */
    private attemptReconnect;
    /**
     * Send data through WebSocket
     * @private
     */
    private send;
    /**
     * Handle incoming WebSocket message
     * @private
     */
    private handleMessage;
    /**
     * Handle connection established
     * @private
     */
    private onConnected;
    /**
     * Handle connection closed
     * @private
     */
    private onDisconnected;
    /**
     * Update collaborators list UI
     * @private
     */
    private updateCollaboratorsList;
    /**
     * Handle user joined
     * @private
     */
    private handleUserJoined;
    /**
     * Handle user left
     * @private
     */
    private handleUserLeft;
    /**
     * Handle section locked
     * @private
     */
    private handleSectionLocked;
    /**
     * Handle section unlocked
     * @private
     */
    private handleSectionUnlocked;
    /**
     * Show error message
     * @private
     */
    private showError;
    /**
     * Setup event listeners
     * @private
     */
    private setupEventListeners;
    /**
     * Request section lock
     * @private
     */
    private requestSectionLock;
    /**
     * Release section lock
     * @private
     */
    private releaseSectionLock;
    /**
     * Update section lock indicator UI
     * @private
     */
    private updateSectionLockIndicator;
    /**
     * Check if section is locked by another user
     */
    isLockedByOther(section: string): boolean;
    /**
     * Enable real-time change broadcasting
     * @private
     */
    private enableChangeBroadcasting;
    /**
     * Calculate text operation
     * @private
     */
    private calculateOperation;
    /**
     * Send text change to server
     * @private
     */
    private sendTextChange;
    /**
     * Handle incoming text change
     * @private
     */
    private handleTextChange;
    /**
     * Apply remote text change
     * @private
     */
    private applyRemoteChange;
    /**
     * Update sync status indicator
     * @private
     */
    private updateSyncStatus;
    /**
     * Integrate with Writer UI (override switchToSection)
     */
    integrateWithWriter(): void;
    /**
     * Check if WebSocket is connected
     */
    isConnected(): boolean;
}
//# sourceMappingURL=writer-collaboration.d.ts.map