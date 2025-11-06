/**
 * SciTeX Writer - Real-Time Collaboration (TypeScript)
 * WebSocket client for collaborative editing
 *
 * @version 2.0.0 (TypeScript)
 * @author SciTeX Development Team
 */
// ============================================================================
// Main Class
// ============================================================================
export class WriterCollaboration {
    /**
     * Creates a new WriterCollaboration instance
     *
     * @param manuscriptId - The manuscript ID
     * @param userId - Current user's ID
     * @param username - Current user's username
     */
    constructor(manuscriptId, userId, username) {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.collaborators = [];
        this.lockedSections = new Set();
        this.manuscriptId = manuscriptId;
        this.userId = userId;
        this.username = username;
        this.init();
    }
    // ========================================================================
    // Initialization
    // ========================================================================
    /**
     * Initialize the collaboration system
     * @private
     */
    init() {
        this.connect();
        this.setupEventListeners();
    }
    /**
     * Connect to WebSocket server
     * @private
     */
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/writer/manuscript/${this.manuscriptId}/`;
        console.log(`Connecting to WebSocket: ${wsUrl}`);
        this.ws = new WebSocket(wsUrl);
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
            this.onConnected();
        };
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        this.ws.onclose = (event) => {
            console.log('WebSocket closed:', event.code, event.reason);
            this.onDisconnected();
            this.attemptReconnect();
        };
    }
    /**
     * Attempt to reconnect to WebSocket
     * @private
     */
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * this.reconnectAttempts;
            console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            setTimeout(() => {
                this.connect();
            }, delay);
        }
        else {
            console.error('Max reconnection attempts reached');
            this.showError('Connection lost. Please refresh the page.');
        }
    }
    // ========================================================================
    // Message Handling
    // ========================================================================
    /**
     * Send data through WebSocket
     * @private
     */
    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }
    /**
     * Handle incoming WebSocket message
     * @private
     */
    handleMessage(data) {
        switch (data.type) {
            case 'collaborators_list':
                this.updateCollaboratorsList(data.collaborators);
                break;
            case 'user_joined':
                this.handleUserJoined(data);
                break;
            case 'user_left':
                this.handleUserLeft(data);
                break;
            case 'section_locked':
                this.handleSectionLocked(data);
                break;
            case 'section_unlocked':
                this.handleSectionUnlocked(data);
                break;
            case 'text_change':
                this.handleTextChange(data);
                break;
            case 'error':
                this.showError(data.message);
                break;
        }
    }
    // ========================================================================
    // Event Handlers
    // ========================================================================
    /**
     * Handle connection established
     * @private
     */
    onConnected() {
        const indicator = document.getElementById('collaboration-status');
        if (indicator) {
            indicator.innerHTML = '<i class="fas fa-circle text-success"></i> Connected';
        }
        // Enable change broadcasting
        this.enableChangeBroadcasting();
        console.log('✓ Real-time features enabled');
    }
    /**
     * Handle connection closed
     * @private
     */
    onDisconnected() {
        const indicator = document.getElementById('collaboration-status');
        if (indicator) {
            indicator.innerHTML = '<i class="fas fa-circle text-danger"></i> Disconnected';
        }
    }
    /**
     * Update collaborators list UI
     * @private
     */
    updateCollaboratorsList(collaborators) {
        this.collaborators = collaborators;
        const container = document.getElementById('collaborators-list');
        if (!container)
            return;
        if (collaborators.length === 0) {
            container.innerHTML = '<small style="color: var(--color-fg-muted);">No other collaborators online</small>';
            return;
        }
        container.innerHTML = collaborators.map(collab => `
            <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; margin-bottom: 0.25rem; background: var(--color-canvas-subtle); border-radius: 4px;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: var(--color-accent-emphasis); color: var(--color-fg-on-emphasis); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600;">
                    ${collab.username.charAt(0).toUpperCase()}
                </div>
                <span style="font-size: 0.85rem; color: var(--color-fg-default);">${collab.username}</span>
            </div>
        `).join('');
        const count = document.getElementById('collaborators-count');
        if (count) {
            count.textContent = collaborators.length.toString();
        }
    }
    /**
     * Handle user joined
     * @private
     */
    handleUserJoined(data) {
        console.log(`User joined: ${data.username}`);
        if (!this.collaborators.find(c => c.user_id === data.user_id)) {
            this.collaborators.push({
                user_id: data.user_id,
                username: data.username,
                locked_sections: []
            });
            this.updateCollaboratorsList(this.collaborators);
        }
        if (typeof window.showToast === 'function') {
            window.showToast(`${data.username} joined`, 'info');
        }
    }
    /**
     * Handle user left
     * @private
     */
    handleUserLeft(data) {
        console.log(`User left: ${data.username}`);
        this.collaborators = this.collaborators.filter(c => c.user_id !== data.user_id);
        this.updateCollaboratorsList(this.collaborators);
        if (typeof window.showToast === 'function') {
            window.showToast(`${data.username} left`, 'info');
        }
    }
    /**
     * Handle section locked
     * @private
     */
    handleSectionLocked(data) {
        this.lockedSections.add(data.section);
        this.updateSectionLockIndicator(data.section, true, data.username);
        // Update collaborator's locked sections
        const collab = this.collaborators.find(c => c.user_id === data.user_id);
        if (collab) {
            if (!collab.locked_sections)
                collab.locked_sections = [];
            if (!collab.locked_sections.includes(data.section)) {
                collab.locked_sections.push(data.section);
            }
            this.updateCollaboratorsList(this.collaborators);
        }
    }
    /**
     * Handle section unlocked
     * @private
     */
    handleSectionUnlocked(data) {
        this.lockedSections.delete(data.section);
        this.updateSectionLockIndicator(data.section, false);
        // Update collaborator's locked sections
        const collab = this.collaborators.find(c => c.user_id === data.user_id);
        if (collab && collab.locked_sections) {
            collab.locked_sections = collab.locked_sections.filter(s => s !== data.section);
            this.updateCollaboratorsList(this.collaborators);
        }
    }
    /**
     * Show error message
     * @private
     */
    showError(message) {
        if (typeof window.showToast === 'function') {
            window.showToast(message, 'danger');
        }
        else {
            console.error(message);
        }
    }
    // ========================================================================
    // Event Listeners Setup
    // ========================================================================
    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // Auto-lock section when user starts editing
        const editor = document.getElementById('latex-editor-textarea');
        if (editor) {
            editor.addEventListener('focus', () => {
                const currentSection = window.currentSection || 'abstract';
                if (!this.lockedSections.has(currentSection)) {
                    this.requestSectionLock(currentSection);
                }
            });
        }
        // Release locks on page unload
        window.addEventListener('beforeunload', () => {
            this.lockedSections.forEach(section => {
                this.releaseSectionLock(section);
            });
        });
    }
    // ========================================================================
    // Section Lock Management
    // ========================================================================
    /**
     * Request section lock
     * @private
     */
    requestSectionLock(section) {
        this.send({ type: 'section_lock', section: section });
    }
    /**
     * Release section lock
     * @private
     */
    releaseSectionLock(section) {
        this.send({ type: 'section_unlock', section: section });
    }
    /**
     * Update section lock indicator UI
     * @private
     */
    updateSectionLockIndicator(section, locked, username) {
        const sectionCard = document.querySelector(`[data-section="${section}"]`);
        if (sectionCard) {
            if (locked && username && username !== this.username) {
                sectionCard.classList.add('section-locked');
                sectionCard.setAttribute('title', `Locked by ${username}`);
                // Add lock indicator
                let lockIcon = sectionCard.querySelector('.lock-indicator');
                if (!lockIcon) {
                    lockIcon = document.createElement('span');
                    lockIcon.className = 'lock-indicator';
                    lockIcon.style.cssText = 'position: absolute; right: 2rem; top: 50%; transform: translateY(-50%); font-size: 1rem;';
                    lockIcon.innerHTML = '🔒';
                    sectionCard.style.position = 'relative';
                    sectionCard.appendChild(lockIcon);
                }
            }
            else {
                sectionCard.classList.remove('section-locked');
                sectionCard.removeAttribute('title');
                // Remove lock indicator
                const lockIcon = sectionCard.querySelector('.lock-indicator');
                if (lockIcon) {
                    lockIcon.remove();
                }
            }
        }
    }
    /**
     * Check if section is locked by another user
     */
    isLockedByOther(section) {
        const collaborator = this.collaborators.find(c => c.locked_sections && c.locked_sections.includes(section));
        return !!collaborator && collaborator.user_id !== this.userId;
    }
    // ========================================================================
    // Change Broadcasting (Sprint 1.3)
    // ========================================================================
    /**
     * Enable real-time change broadcasting
     * @private
     */
    enableChangeBroadcasting() {
        const editor = document.getElementById('latex-editor-textarea');
        if (!editor)
            return;
        let changeTimeout = null;
        let lastContent = editor.value;
        // Debounced change handler (500ms after typing stops)
        editor.addEventListener('input', () => {
            if (changeTimeout)
                clearTimeout(changeTimeout);
            changeTimeout = setTimeout(() => {
                const currentContent = editor.value;
                if (currentContent !== lastContent) {
                    const operation = this.calculateOperation(lastContent, currentContent);
                    lastContent = currentContent;
                    // Broadcast change
                    const currentSection = window.currentSection || 'abstract';
                    this.sendTextChange(currentSection, operation);
                    // Update sync indicator
                    this.updateSyncStatus('syncing');
                    setTimeout(() => this.updateSyncStatus('synced'), 500);
                }
            }, 500);
        });
        console.log('✓ Change broadcasting enabled');
    }
    /**
     * Calculate text operation
     * @private
     */
    calculateOperation(oldText, newText) {
        // Simple diff calculation (basic version, will be enhanced with OT)
        return {
            type: 'replace',
            old_text: oldText,
            new_text: newText,
            timestamp: Date.now()
        };
    }
    /**
     * Send text change to server
     * @private
     */
    sendTextChange(section, operation) {
        this.send({
            type: 'text_change',
            section: section,
            operation: operation
        });
    }
    /**
     * Handle incoming text change
     * @private
     */
    handleTextChange(data) {
        console.log('Text change received from', data.username);
        this.applyRemoteChange(data.section, data.operation);
        this.updateSyncStatus('synced');
    }
    /**
     * Apply remote text change
     * @private
     */
    applyRemoteChange(section, operation) {
        const editor = document.getElementById('latex-editor-textarea');
        if (!editor)
            return;
        const currentSection = window.currentSection || 'abstract';
        // Only apply if not currently focused (prevent conflicts)
        if (section !== currentSection || document.activeElement !== editor) {
            console.log('Applying remote change to', section);
            // If this is the current section, update editor
            if (section === currentSection && operation.new_text) {
                const cursorPosition = editor.selectionStart;
                editor.value = operation.new_text;
                // Restore cursor position (approximate)
                editor.setSelectionRange(cursorPosition, cursorPosition);
                // Update preview
                if (typeof window.convertFromLatex === 'function') {
                    const textContent = window.convertFromLatex(section, operation.new_text);
                    const preview = document.getElementById('text-preview');
                    if (preview) {
                        preview.textContent = textContent;
                    }
                }
                // Update word count
                if (typeof window.updateWordCount === 'function') {
                    window.updateWordCount();
                }
            }
        }
        else {
            console.log('Skipping remote change - user is actively editing');
            // TODO: Queue change for later application with OT
        }
    }
    /**
     * Update sync status indicator
     * @private
     */
    updateSyncStatus(status) {
        const saveStatus = document.getElementById('save-status');
        if (!saveStatus)
            return;
        switch (status) {
            case 'syncing':
                saveStatus.innerHTML = '<i class="fas fa-sync fa-spin text-info me-1"></i>Syncing...';
                break;
            case 'synced':
                saveStatus.innerHTML = '<i class="fas fa-check-circle text-success me-1"></i>Synced with collaborators';
                setTimeout(() => {
                    // Revert to original save status after 2 seconds
                    const hasUnsaved = window.hasUnsavedChanges || false;
                    if (!hasUnsaved) {
                        saveStatus.innerHTML = '<i class="fas fa-check-circle text-success me-1"></i>All changes saved';
                    }
                }, 2000);
                break;
            case 'conflict':
                saveStatus.innerHTML = '<i class="fas fa-exclamation-triangle text-warning me-1"></i>Sync conflict';
                break;
            case 'error':
                saveStatus.innerHTML = '<i class="fas fa-times-circle text-danger me-1"></i>Sync error';
                break;
        }
    }
    // ========================================================================
    // Writer Integration
    // ========================================================================
    /**
     * Integrate with Writer UI (override switchToSection)
     */
    integrateWithWriter() {
        const originalSwitchToSection = window.switchToSection;
        // Override switchToSection to handle locks
        window.switchToSection = (section) => {
            // Release lock on current section
            if (window.currentSection && this.lockedSections.has(window.currentSection)) {
                this.releaseSectionLock(window.currentSection);
            }
            // Call original function
            if (originalSwitchToSection) {
                originalSwitchToSection(section);
            }
            // Request lock on new section
            setTimeout(() => {
                this.requestSectionLock(section);
            }, 100);
        };
        // Disable editor for locked sections
        const editor = document.getElementById('latex-editor-textarea');
        if (editor) {
            const checkLockStatus = () => {
                const currentSection = window.currentSection || 'abstract';
                const isLockedByOther = this.isLockedByOther(currentSection);
                if (isLockedByOther) {
                    editor.disabled = true;
                    editor.placeholder = 'This section is locked by another user...';
                    editor.style.background = 'var(--color-danger-subtle)';
                }
                else {
                    editor.disabled = false;
                    editor.placeholder = 'LaTeX code...';
                    editor.style.background = 'var(--color-canvas-subtle)';
                }
            };
            // Check lock status periodically
            setInterval(checkLockStatus, 1000);
        }
    }
    // ========================================================================
    // Public API
    // ========================================================================
    /**
     * Check if WebSocket is connected
     */
    isConnected() {
        return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
    }
}
// ============================================================================
// Global Export
// ============================================================================
// Export to global namespace
if (typeof window !== 'undefined') {
    window.WriterCollaboration = WriterCollaboration;
}
console.log('✓ Sprint 1.3: Basic Change Broadcasting loaded (TypeScript)');
//# sourceMappingURL=writer-collaboration.js.map