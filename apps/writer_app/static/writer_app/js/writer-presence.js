/**
 * Writer Presence Manager
 * Tracks and displays who's online and which section they're editing
 * Uses polling (30s interval) for simplicity
 */

import { getCsrfToken } from '@/utils/csrf.js';

export class PresenceManager {
    constructor(projectId, userId) {
        this.projectId = projectId;
        this.userId = userId;
        this.currentSection = null;
        this.updateInterval = null;
        this.fetchInterval = null;
        this.onlineUsers = [];
    }

    /**
     * Start presence tracking
     */
    start() {
        if (!this.projectId) {
            console.warn('[Presence] No project ID, presence tracking disabled');
            return;
        }

        // Update our presence every 30 seconds
        this.updateInterval = setInterval(() => {
            this.updatePresence();
        }, 30000);

        // Fetch others' presence every 30 seconds
        this.fetchInterval = setInterval(() => {
            this.fetchPresence();
        }, 30000);

        // Initial update
        this.updatePresence();
        this.fetchPresence();

        console.log('[Presence] Tracking started');
    }

    /**
     * Stop presence tracking
     */
    stop() {
        clearInterval(this.updateInterval);
        clearInterval(this.fetchInterval);

        // Mark as inactive
        this.markInactive();

        console.log('[Presence] Tracking stopped');
    }

    /**
     * Set current section (triggers immediate update)
     */
    setSection(sectionId) {
        if (this.currentSection === sectionId) return;

        this.currentSection = sectionId;
        this.updatePresence(); // Immediate update on section change

        console.log(`[Presence] Section changed to: ${sectionId}`);
    }

    /**
     * Update our presence on server
     */
    async updatePresence() {
        if (!this.currentSection) return;

        try {
            const response = await fetch(
                `/writer/api/project/${this.projectId}/presence/update/`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        section: this.currentSection
                    })
                }
            );

            if (!response.ok) {
                console.warn('[Presence] Update failed:', response.status);
            }
        } catch (error) {
            console.error('[Presence] Update error:', error);
        }
    }

    /**
     * Fetch other users' presence
     */
    async fetchPresence() {
        try {
            const response = await fetch(
                `/writer/api/project/${this.projectId}/presence/list/`
            );

            if (!response.ok) {
                console.warn('[Presence] Fetch failed:', response.status);
                return;
            }

            const data = await response.json();

            if (data.success) {
                // Filter out current user
                this.onlineUsers = data.users.filter(u => u.user_id !== this.userId);
                this.updateUI();

                console.log(`[Presence] ${this.onlineUsers.length} other users online`);
            }
        } catch (error) {
            console.error('[Presence] Fetch error:', error);
        }
    }

    /**
     * Mark user as inactive (called on stop)
     */
    async markInactive() {
        try {
            await fetch(
                `/writer/api/project/${this.projectId}/presence/update/`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        section: '',
                        is_active: false
                    })
                }
            );
        } catch (error) {
            // Silent fail - user is leaving anyway
        }
    }

    /**
     * Update UI with presence information
     */
    updateUI() {
        // Update section dropdown badge
        this.updatePresenceBadge();

        // Update tooltip with user list
        this.updatePresenceTooltip();
    }

    /**
     * Update presence badge (shows count)
     */
    updatePresenceBadge() {
        let badge = document.getElementById('presence-badge');

        // Create badge if it doesn't exist
        if (!badge) {
            const dropdown = document.getElementById('texfile-selector');
            if (!dropdown) return;

            badge = document.createElement('span');
            badge.id = 'presence-badge';
            badge.style.cssText = 'margin-left: 8px; font-size: 14px; opacity: 0.7;';
            dropdown.parentNode.appendChild(badge);
        }

        // Update badge content
        if (this.onlineUsers.length > 0) {
            badge.textContent = `📝 ${this.onlineUsers.length}`;
            badge.style.display = 'inline';
            badge.title = this.getPresenceTooltipText();
        } else {
            badge.style.display = 'none';
        }
    }

    /**
     * Update presence tooltip
     */
    updatePresenceTooltip() {
        const badge = document.getElementById('presence-badge');
        if (badge) {
            badge.title = this.getPresenceTooltipText();
        }
    }

    /**
     * Get tooltip text showing online users
     */
    getPresenceTooltipText() {
        if (this.onlineUsers.length === 0) {
            return 'No other users online';
        }

        const sectionLabels = {
            'manuscript/abstract': 'Abstract',
            'manuscript/introduction': 'Introduction',
            'manuscript/methods': 'Methods',
            'manuscript/results': 'Results',
            'manuscript/discussion': 'Discussion',
            'manuscript/compiled_pdf': 'Compiled PDF'
        };

        const userList = this.onlineUsers
            .map(u => {
                const section = sectionLabels[u.section] || u.section;
                return `• ${u.username} (${section})`;
            })
            .join('\n');

        return `Online (${this.onlineUsers.length}):\n${userList}`;
    }

    /**
     * Check if current section has conflict
     */
    hasConflict() {
        if (!this.currentSection) return false;

        return this.onlineUsers.some(u => u.section === this.currentSection);
    }

    /**
     * Get users in current section
     */
    getUsersInSection(sectionId) {
        return this.onlineUsers.filter(u => u.section === sectionId);
    }
}
