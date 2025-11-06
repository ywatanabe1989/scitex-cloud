/**
 * SciTeX Writer - Real-Time Collaboration
 * WebSocket client for collaborative editing
 *
 * @version 2.0.0 (TypeScript)
 * @author SciTeX Development Team
 */
// ============================================================================
// Type Definitions
// ============================================================================
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/static/ts/collaboration/writer-collaboration.ts loaded");
// ============================================================================
// WriterCollaboration Class
// ============================================================================
class WriterCollaboration {
    manuscriptId;
    userId;
    username;
    ws = null;
    reconnectAttempts = 0;
    maxReconnectAttempts = 5;
    reconnectDelay = 1000;
    collaborators = [];
    lockedSections = new Set();
    changeTimeout = null;
    lastContent = '';
    constructor(manuscriptId, userId, username) {
        this.manuscriptId = manuscriptId;
        this.userId = userId;
        this.username = username;
        this.init();
    }
    // ========================================================================
    // Initialization & Connection
    // ========================================================================
    init() {
        this.connect();
        this.setupEventListeners();
    }
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/writer/manuscript/${this.manuscriptId}/`;
        console.log(`[Collaboration] Connecting to WebSocket: ${wsUrl}`);
        this.ws = new WebSocket(wsUrl);
        this.ws.onopen = () => {
            console.log('[Collaboration] WebSocket connected');
            this.reconnectAttempts = 0;
            this.onConnected();
        };
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            }
            catch (error) {
                console.error('[Collaboration] Failed to parse message:', error);
            }
        };
        this.ws.onerror = (error) => {
            console.error('[Collaboration] WebSocket error:', error);
        };
        this.ws.onclose = (event) => {
            console.log(`[Collaboration] WebSocket closed: ${event.code} ${event.reason}`);
            this.onDisconnected();
            this.attemptReconnect();
        };
    }
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * this.reconnectAttempts;
            console.log(`[Collaboration] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            setTimeout(() => {
                this.connect();
            }, delay);
        }
        else {
            console.error('[Collaboration] Max reconnection attempts reached');
            this.showError('Connection lost. Please refresh the page.');
        }
    }
    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
        else {
            console.warn('[Collaboration] Cannot send message - WebSocket not open');
        }
    }
    // ========================================================================
    // Message Handling
    // ========================================================================
    handleMessage(data) {
        switch (data.type) {
            case 'collaborators_list':
                if (data.collaborators) {
                    this.updateCollaboratorsList(data.collaborators);
                }
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
                this.showError(data.message || 'Unknown error');
                break;
        }
    }
    // ========================================================================
    // Connection Status Handlers
    // ========================================================================
    onConnected() {
        const indicator = document.getElementById('collaboration-status');
        if (indicator) {
            indicator.innerHTML = '<i class="fas fa-circle text-success"></i> Connected';
        }
        // Enable change broadcasting
        this.enableChangeBroadcasting();
        console.log('[Collaboration] Real-time features enabled');
    }
    onDisconnected() {
        const indicator = document.getElementById('collaboration-status');
        if (indicator) {
            indicator.innerHTML = '<i class="fas fa-circle text-danger"></i> Disconnected';
        }
    }
    // ========================================================================
    // Collaborators Management
    // ========================================================================
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
                    ${this.escapeHtml(collab.username.charAt(0).toUpperCase())}
                </div>
                <span style="font-size: 0.85rem; color: var(--color-fg-default);">${this.escapeHtml(collab.username)}</span>
            </div>
        `).join('');
        const count = document.getElementById('collaborators-count');
        if (count) {
            count.textContent = String(collaborators.length);
        }
    }
    handleUserJoined(data) {
        if (!data.user_id || !data.username)
            return;
        console.log(`[Collaboration] User joined: ${data.username}`);
        if (!this.collaborators.find(c => c.user_id === data.user_id)) {
            this.collaborators.push({
                user_id: data.user_id,
                username: data.username,
                locked_sections: []
            });
            this.updateCollaboratorsList(this.collaborators);
        }
        if (window.showToast) {
            window.showToast(`${data.username} joined`, 'info');
        }
    }
    handleUserLeft(data) {
        if (!data.user_id || !data.username)
            return;
        console.log(`[Collaboration] User left: ${data.username}`);
        this.collaborators = this.collaborators.filter(c => c.user_id !== data.user_id);
        this.updateCollaboratorsList(this.collaborators);
        if (window.showToast) {
            window.showToast(`${data.username} left`, 'info');
        }
    }
    // ========================================================================
    // Section Locking
    // ========================================================================
    handleSectionLocked(data) {
        if (!data.section)
            return;
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
    handleSectionUnlocked(data) {
        if (!data.section)
            return;
        this.lockedSections.delete(data.section);
        this.updateSectionLockIndicator(data.section, false);
        // Update collaborator's locked sections
        const collab = this.collaborators.find(c => c.user_id === data.user_id);
        if (collab && collab.locked_sections) {
            collab.locked_sections = collab.locked_sections.filter(s => s !== data.section);
            this.updateCollaboratorsList(this.collaborators);
        }
    }
    updateSectionLockIndicator(section, locked, username) {
        const sectionCard = document.querySelector(`[data-section="${section}"]`);
        if (!sectionCard)
            return;
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
            lockIcon?.remove();
        }
    }
    requestSectionLock(section) {
        this.send({ type: 'section_locked', section });
    }
    releaseSectionLock(section) {
        this.send({ type: 'section_unlocked', section });
    }
    isLockedByOther(section) {
        const collaborator = this.collaborators.find(c => c.locked_sections && c.locked_sections.includes(section));
        return !!collaborator && collaborator.user_id !== this.userId;
    }
    // ========================================================================
    // Event Listeners
    // ========================================================================
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
    // Change Broadcasting
    // ========================================================================
    enableChangeBroadcasting() {
        const editor = document.getElementById('latex-editor-textarea');
        if (!editor)
            return;
        this.lastContent = editor.value;
        // Debounced change handler (500ms after typing stops)
        editor.addEventListener('input', () => {
            if (this.changeTimeout) {
                clearTimeout(this.changeTimeout);
            }
            this.changeTimeout = window.setTimeout(() => {
                const currentContent = editor.value;
                if (currentContent !== this.lastContent) {
                    const operation = this.calculateOperation(this.lastContent, currentContent);
                    this.lastContent = currentContent;
                    // Broadcast change
                    const currentSection = window.currentSection || 'abstract';
                    this.sendTextChange(currentSection, operation);
                    // Update sync indicator
                    this.updateSyncStatus('syncing');
                    setTimeout(() => this.updateSyncStatus('synced'), 500);
                }
            }, 500);
        });
        console.log('[Collaboration] Change broadcasting enabled');
    }
    calculateOperation(oldText, newText) {
        // Simple diff calculation (basic version, will be enhanced with OT)
        return {
            type: 'replace',
            old_text: oldText,
            new_text: newText,
            timestamp: Date.now()
        };
    }
    sendTextChange(section, operation) {
        this.send({
            type: 'text_change',
            section,
            operation
        });
    }
    handleTextChange(data) {
        if (!data.section || !data.operation)
            return;
        console.log('[Collaboration] Text change received from', data.username);
        this.applyRemoteChange(data.section, data.operation);
        this.updateSyncStatus('synced');
    }
    applyRemoteChange(section, operation) {
        const editor = document.getElementById('latex-editor-textarea');
        if (!editor)
            return;
        const currentSection = window.currentSection || 'abstract';
        // Only apply if not currently focused (prevent conflicts)
        if (section !== currentSection || document.activeElement !== editor) {
            console.log('[Collaboration] Applying remote change to', section);
            // If this is the current section, update editor
            if (section === currentSection && operation.new_text) {
                const cursorPosition = editor.selectionStart;
                editor.value = operation.new_text;
                // Restore cursor position (approximate)
                editor.setSelectionRange(cursorPosition, cursorPosition);
                // Update preview
                if (window.convertFromLatex && window.textPreview) {
                    const textContent = window.convertFromLatex(section, operation.new_text);
                    const preview = document.getElementById('text-preview');
                    if (preview) {
                        preview.textContent = textContent;
                    }
                }
                // Update word count
                if (window.updateWordCount) {
                    window.updateWordCount();
                }
            }
        }
        else {
            console.log('[Collaboration] Skipping remote change - user is actively editing');
            // TODO: Queue change for later application with OT
        }
    }
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
    integrateWithWriter() {
        // Store reference to original switchToSection
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
    isConnected() {
        return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
    }
    // ========================================================================
    // Utility Functions
    // ========================================================================
    showError(message) {
        if (window.showToast) {
            window.showToast(message, 'danger');
        }
        else {
            console.error('[Collaboration]', message);
        }
    }
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
// ============================================================================
// Global Export
// ============================================================================
window.WriterCollaboration = WriterCollaboration;
console.log('[Collaboration] Sprint 1.3: Basic Change Broadcasting loaded (TypeScript)');
export {};
//# sourceMappingURL=writer-collaboration.js.map