/**
 * SciTeX Writer - Real-Time Collaboration
 * WebSocket client for collaborative editing
 */

class WriterCollaboration {
    constructor(manuscriptId, userId, username) {
        this.manuscriptId = manuscriptId;
        this.userId = userId;
        this.username = username;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.collaborators = [];
        this.lockedSections = new Set();

        this.init();
    }

    init() {
        this.connect();
        this.setupEventListeners();
    }

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
            this.handleMessage(JSON.parse(event.data));
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

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * this.reconnectAttempts;
            console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
                this.connect();
            }, delay);
        } else {
            console.error('Max reconnection attempts reached');
            this.showError('Connection lost. Please refresh the page.');
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

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
            case 'error':
                this.showError(data.message);
                break;
        }
    }

    // Event handlers

    onConnected() {
        const indicator = document.getElementById('collaboration-status');
        if (indicator) {
            indicator.innerHTML = '<i class="fas fa-circle text-success"></i> Connected';
        }
    }

    onDisconnected() {
        const indicator = document.getElementById('collaboration-status');
        if (indicator) {
            indicator.innerHTML = '<i class="fas fa-circle text-danger"></i> Disconnected';
        }
    }

    updateCollaboratorsList(collaborators) {
        this.collaborators = collaborators;
        const container = document.getElementById('collaborators-list');
        if (!container) return;

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
            count.textContent = collaborators.length;
        }
    }

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
        if (typeof showToast === 'function') {
            showToast(`${data.username} joined`, 'info');
        }
    }

    handleUserLeft(data) {
        console.log(`User left: ${data.username}`);
        this.collaborators = this.collaborators.filter(c => c.user_id !== data.user_id);
        this.updateCollaboratorsList(this.collaborators);
        if (typeof showToast === 'function') {
            showToast(`${data.username} left`, 'info');
        }
    }

    handleSectionLocked(data) {
        this.lockedSections.add(data.section);
        const sectionElement = document.querySelector(`[data-section="${data.section}"]`);
        if (sectionElement && data.user_id !== this.userId) {
            sectionElement.style.opacity = '0.6';
            sectionElement.setAttribute('title', `Locked by ${data.username}`);
        }
    }

    handleSectionUnlocked(data) {
        this.lockedSections.delete(data.section);
        const sectionElement = document.querySelector(`[data-section="${data.section}"]`);
        if (sectionElement) {
            sectionElement.style.opacity = '1';
            sectionElement.removeAttribute('title');
        }
    }

    showError(message) {
        if (typeof showToast === 'function') {
            showToast(message, 'danger');
        } else {
            console.error(message);
        }
    }

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

    requestSectionLock(section) {
        this.send({type: 'section_lock', section: section});
    }

    releaseSectionLock(section) {
        this.send({type: 'section_unlock', section: section});
    }
}

window.WriterCollaboration = WriterCollaboration;
