/**
 * Collaborative Editor WebSocket Client
 * Real-time collaborative editing for SciTeX Writer
 */

class CollaborativeEditor {
    constructor(manuscriptId, userId, username) {
        this.manuscriptId = manuscriptId;
        this.userId = userId;
        this.username = username;
        this.socket = null;
        this.isConnected = false;
        this.activeUsers = new Map();
        this.userCursors = new Map();
        this.userSelections = new Map();
        this.typingIndicators = new Map();
        this.lockedSections = new Set();
        this.currentSection = null;
        
        // Editor state
        this.pendingOperations = [];
        this.lastKnownContent = {};
        this.debounceTimers = {};
        
        // UI colors for users
        this.userColors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
        ];
        
        this.init();
    }
    
    init() {
        this.connectWebSocket();
        this.setupEventListeners();
        this.createPresenceIndicator();
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/writer/manuscript/${this.manuscriptId}/`;
        
        try {
            this.socket = new WebSocket(wsUrl);
            this.setupWebSocketHandlers();
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.showConnectionError();
        }
    }
    
    setupWebSocketHandlers() {
        this.socket.onopen = (event) => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.showConnectionStatus('Connected');
            this.hideConnectionError();
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.socket.onclose = (event) => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.showConnectionStatus('Disconnected');
            
            // Attempt to reconnect after delay
            setTimeout(() => {
                if (!this.isConnected) {
                    this.connectWebSocket();
                }
            }, 3000);
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showConnectionError();
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'user_joined':
                this.handleUserJoined(data);
                break;
            case 'user_left':
                this.handleUserLeft(data);
                break;
            case 'document_changed':
                this.handleDocumentChanged(data);
                break;
            case 'cursor_moved':
                this.handleCursorMoved(data);
                break;
            case 'selection_changed':
                this.handleSelectionChanged(data);
                break;
            case 'section_locked':
                this.handleSectionLocked(data);
                break;
            case 'section_unlocked':
                this.handleSectionUnlocked(data);
                break;
            case 'user_typing':
                this.handleUserTyping(data);
                break;
            case 'active_users':
                this.handleActiveUsers(data);
                break;
            case 'error':
                console.error('Server error:', data.message);
                break;
        }
    }
    
    handleUserJoined(data) {
        this.activeUsers.set(data.user_id, {
            username: data.username,
            joinedAt: data.timestamp,
            color: this.getUserColor(data.user_id)
        });
        this.updatePresenceIndicator();
        this.showNotification(`${data.username} joined the collaboration`);
    }
    
    handleUserLeft(data) {
        this.activeUsers.delete(data.user_id);
        this.userCursors.delete(data.user_id);
        this.userSelections.delete(data.user_id);
        this.typingIndicators.delete(data.user_id);
        this.updatePresenceIndicator();
        this.clearUserIndicators(data.user_id);
        this.showNotification(`${data.username} left the collaboration`);
    }
    
    handleDocumentChanged(data) {
        const sectionElement = document.getElementById(`section-${data.section_id}`);
        if (!sectionElement) return;
        
        // Apply the operation to the text area
        this.applyOperation(sectionElement, data.operation);
        
        // Update last known content
        this.lastKnownContent[data.section_id] = sectionElement.value;
        
        // Show user indicator
        this.showEditIndicator(data.section_id, data.username, data.user_id);
    }
    
    handleCursorMoved(data) {
        if (data.user_id === this.userId) return;
        
        this.userCursors.set(data.user_id, {
            sectionId: data.section_id,
            position: data.position,
            username: data.username,
            color: data.user_color
        });
        
        this.updateCursorDisplay(data.user_id);
    }
    
    handleSelectionChanged(data) {
        if (data.user_id === this.userId) return;
        
        this.userSelections.set(data.user_id, {
            sectionId: data.section_id,
            start: data.start,
            end: data.end,
            username: data.username,
            color: data.user_color
        });
        
        this.updateSelectionDisplay(data.user_id);
    }
    
    handleSectionLocked(data) {
        this.lockedSections.add(data.section_id);
        this.updateSectionLockStatus(data.section_id, true, data.username);
    }
    
    handleSectionUnlocked(data) {
        this.lockedSections.delete(data.section_id);
        this.updateSectionLockStatus(data.section_id, false);
    }
    
    handleUserTyping(data) {
        if (data.user_id === this.userId) return;
        
        if (data.is_typing) {
            this.typingIndicators.set(data.user_id, {
                sectionId: data.section_id,
                username: data.username
            });
        } else {
            this.typingIndicators.delete(data.user_id);
        }
        
        this.updateTypingIndicators(data.section_id);
    }
    
    handleActiveUsers(data) {
        this.activeUsers.clear();
        data.users.forEach(user => {
            this.activeUsers.set(user.user_id, {
                username: user.username,
                joinedAt: user.started_at,
                color: this.getUserColor(user.user_id),
                lockedSections: user.locked_sections || []
            });
        });
        this.updatePresenceIndicator();
    }
    
    // Editor integration methods
    setupEventListeners() {
        // Listen for text changes in all section textareas
        document.addEventListener('input', (event) => {
            if (event.target.matches('[id^="section-"]')) {
                this.handleTextChange(event.target);
            }
        });
        
        // Listen for cursor/selection changes
        document.addEventListener('selectionchange', () => {
            const activeElement = document.activeElement;
            if (activeElement && activeElement.matches('[id^="section-"]')) {
                this.handleSelectionChange(activeElement);
            }
        });
        
        // Listen for focus/blur events for section locking
        document.addEventListener('focus', (event) => {
            if (event.target.matches('[id^="section-"]')) {
                this.handleSectionFocus(event.target);
            }
        }, true);
        
        document.addEventListener('blur', (event) => {
            if (event.target.matches('[id^="section-"]')) {
                this.handleSectionBlur(event.target);
            }
        }, true);
    }
    
    handleTextChange(element) {
        const sectionId = this.getSectionId(element);
        if (!sectionId) return;
        
        // Clear existing debounce timer
        if (this.debounceTimers[sectionId]) {
            clearTimeout(this.debounceTimers[sectionId]);
        }
        
        // Debounce the operation sending
        this.debounceTimers[sectionId] = setTimeout(() => {
            this.sendTextChangeOperation(element, sectionId);
        }, 300);
        
        // Send typing indicator immediately
        this.sendTypingIndicator(sectionId, true);
        
        // Clear typing indicator after delay
        setTimeout(() => {
            this.sendTypingIndicator(sectionId, false);
        }, 1000);
    }
    
    handleSelectionChange(element) {
        const sectionId = this.getSectionId(element);
        if (!sectionId) return;
        
        const selectionStart = element.selectionStart;
        const selectionEnd = element.selectionEnd;
        
        if (selectionStart === selectionEnd) {
            // Cursor position
            this.sendCursorPosition(sectionId, selectionStart);
        } else {
            // Text selection
            this.sendSelection(sectionId, selectionStart, selectionEnd);
        }
    }
    
    handleSectionFocus(element) {
        const sectionId = this.getSectionId(element);
        if (!sectionId) return;
        
        this.currentSection = sectionId;
        
        // Check if section is locked by another user
        if (this.lockedSections.has(sectionId)) {
            this.showSectionLockedWarning(sectionId);
            return;
        }
        
        // Lock the section
        this.sendSectionLock(sectionId);
    }
    
    handleSectionBlur(element) {
        const sectionId = this.getSectionId(element);
        if (!sectionId) return;
        
        // Unlock the section
        this.sendSectionUnlock(sectionId);
        this.currentSection = null;
    }
    
    // WebSocket message sending methods
    sendTextChangeOperation(element, sectionId) {
        const currentContent = element.value;
        const lastContent = this.lastKnownContent[sectionId] || '';
        
        // Generate operation (simple diff for now)
        const operation = this.generateOperation(lastContent, currentContent);
        if (!operation) return;
        
        this.sendMessage({
            type: 'document_change',
            section_id: sectionId,
            operation: operation
        });
        
        this.lastKnownContent[sectionId] = currentContent;
    }
    
    sendCursorPosition(sectionId, position) {
        this.sendMessage({
            type: 'cursor_position',
            section_id: sectionId,
            position: position
        });
    }
    
    sendSelection(sectionId, start, end) {
        this.sendMessage({
            type: 'selection_change',
            section_id: sectionId,
            start: start,
            end: end
        });
    }
    
    sendSectionLock(sectionId) {
        this.sendMessage({
            type: 'section_lock',
            section_id: sectionId
        });
    }
    
    sendSectionUnlock(sectionId) {
        this.sendMessage({
            type: 'section_unlock',
            section_id: sectionId
        });
    }
    
    sendTypingIndicator(sectionId, isTyping) {
        this.sendMessage({
            type: 'typing_indicator',
            section_id: sectionId,
            is_typing: isTyping
        });
    }
    
    sendMessage(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        }
    }
    
    // UI update methods
    createPresenceIndicator() {
        if (document.getElementById('collaboration-presence')) return;
        
        const indicator = document.createElement('div');
        indicator.id = 'collaboration-presence';
        indicator.className = 'collaboration-presence';
        indicator.innerHTML = `
            <div class="presence-header">
                <i class="fas fa-users"></i>
                <span class="connection-status">Connecting...</span>
            </div>
            <div class="active-users-list"></div>
        `;
        
        // Insert at the top of the editor
        const editorContainer = document.querySelector('.editor-container, .main-content');
        if (editorContainer) {
            editorContainer.insertBefore(indicator, editorContainer.firstChild);
        }
    }
    
    updatePresenceIndicator() {
        const usersList = document.querySelector('.active-users-list');
        if (!usersList) return;
        
        usersList.innerHTML = '';
        
        this.activeUsers.forEach((user, userId) => {
            const userElement = document.createElement('div');
            userElement.className = 'active-user';
            userElement.innerHTML = `
                <div class="user-avatar" style="background-color: ${user.color}">
                    ${user.username.charAt(0).toUpperCase()}
                </div>
                <span class="user-name">${user.username}</span>
                ${userId === this.userId ? '<span class="user-label">(You)</span>' : ''}
            `;
            usersList.appendChild(userElement);
        });
    }
    
    showConnectionStatus(status) {
        const statusElement = document.querySelector('.connection-status');
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `connection-status ${status.toLowerCase()}`;
        }
    }
    
    showConnectionError() {
        const indicator = document.getElementById('collaboration-presence');
        if (indicator) {
            indicator.classList.add('connection-error');
        }
    }
    
    hideConnectionError() {
        const indicator = document.getElementById('collaboration-presence');
        if (indicator) {
            indicator.classList.remove('connection-error');
        }
    }
    
    showNotification(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'collaboration-toast';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
    
    // Utility methods
    getSectionId(element) {
        const match = element.id.match(/section-(.+)/);
        return match ? match[1] : null;
    }
    
    getUserColor(userId) {
        return this.userColors[userId % this.userColors.length];
    }
    
    generateOperation(oldText, newText) {
        // Simple diff implementation - in production, use a proper diff library
        if (oldText === newText) return null;
        
        // Find common prefix and suffix
        let start = 0;
        while (start < oldText.length && start < newText.length && 
               oldText[start] === newText[start]) {
            start++;
        }
        
        let oldEnd = oldText.length - 1;
        let newEnd = newText.length - 1;
        while (oldEnd >= start && newEnd >= start && 
               oldText[oldEnd] === newText[newEnd]) {
            oldEnd--;
            newEnd--;
        }
        
        const deletedText = oldText.slice(start, oldEnd + 1);
        const insertedText = newText.slice(start, newEnd + 1);
        
        if (deletedText.length === 0 && insertedText.length > 0) {
            return {
                type: 'insert',
                position: start,
                text: insertedText
            };
        } else if (deletedText.length > 0 && insertedText.length === 0) {
            return {
                type: 'delete',
                start: start,
                end: oldEnd + 1
            };
        } else if (deletedText.length > 0 && insertedText.length > 0) {
            return {
                type: 'replace',
                start: start,
                end: oldEnd + 1,
                text: insertedText
            };
        }
        
        return null;
    }
    
    applyOperation(element, operation) {
        const currentValue = element.value;
        
        switch (operation.type) {
            case 'insert':
                element.value = currentValue.slice(0, operation.position) + 
                               operation.text + 
                               currentValue.slice(operation.position);
                break;
            case 'delete':
                element.value = currentValue.slice(0, operation.start) + 
                               currentValue.slice(operation.end);
                break;
            case 'replace':
                element.value = currentValue.slice(0, operation.start) + 
                               operation.text + 
                               currentValue.slice(operation.end);
                break;
        }
        
        // Trigger input event to update word counts, etc.
        element.dispatchEvent(new Event('input', { bubbles: true }));
    }
    
    // Cleanup
    destroy() {
        if (this.socket) {
            this.socket.close();
        }
        
        Object.values(this.debounceTimers).forEach(timer => clearTimeout(timer));
        
        const indicator = document.getElementById('collaboration-presence');
        if (indicator) {
            indicator.remove();
        }
    }
}

// Initialize collaborative editing when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a writer page with collaboration support
    const manuscriptIdElement = document.querySelector('[data-manuscript-id]');
    const userIdElement = document.querySelector('[data-user-id]');
    const usernameElement = document.querySelector('[data-username]');
    
    if (manuscriptIdElement && userIdElement && usernameElement) {
        const manuscriptId = manuscriptIdElement.dataset.manuscriptId;
        const userId = userIdElement.dataset.userId;
        const username = usernameElement.dataset.username;
        
        // Initialize collaborative editor
        window.collaborativeEditor = new CollaborativeEditor(manuscriptId, userId, username);
    }
});