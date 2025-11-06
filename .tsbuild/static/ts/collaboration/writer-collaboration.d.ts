/**
 * SciTeX Writer - Real-Time Collaboration
 * WebSocket client for collaborative editing
 *
 * @version 2.0.0 (TypeScript)
 * @author SciTeX Development Team
 */
declare global {
    interface Window {
        WriterCollaboration: typeof WriterCollaboration;
        currentSection?: string;
        hasUnsavedChanges?: boolean;
        switchToSection?: (section: string) => void;
        showToast?: (message: string, type: string) => void;
        convertFromLatex?: (section: string, latex: string) => string;
        textPreview?: any;
        updateWordCount?: () => void;
    }
}
declare class WriterCollaboration {
    private manuscriptId;
    private userId;
    private username;
    private ws;
    private reconnectAttempts;
    private maxReconnectAttempts;
    private reconnectDelay;
    private collaborators;
    private lockedSections;
    private changeTimeout;
    private lastContent;
    constructor(manuscriptId: string, userId: number, username: string);
    private init;
    private connect;
    private attemptReconnect;
    private send;
    private handleMessage;
    private onConnected;
    private onDisconnected;
    private updateCollaboratorsList;
    private handleUserJoined;
    private handleUserLeft;
    private handleSectionLocked;
    private handleSectionUnlocked;
    private updateSectionLockIndicator;
    requestSectionLock(section: string): void;
    releaseSectionLock(section: string): void;
    private isLockedByOther;
    private setupEventListeners;
    private enableChangeBroadcasting;
    private calculateOperation;
    private sendTextChange;
    private handleTextChange;
    private applyRemoteChange;
    private updateSyncStatus;
    integrateWithWriter(): void;
    isConnected(): boolean;
    private showError;
    private escapeHtml;
}
export {};
//# sourceMappingURL=writer-collaboration.d.ts.map