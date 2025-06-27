/**
 * Profile Manager JavaScript Module
 * Handles user profile management with API integration
 * Following clean code principles and TDD-driven design
 */

class ProfileManager {
    constructor() {
        this.apiBaseUrl = '/core/api/v1/profile/';
        this.currentProfile = null;
        
        this.initializeEventListeners();
        this.loadProfile();
    }
    
    /**
     * Initialize event listeners for profile management
     */
    initializeEventListeners() {
        // Form submission
        const profileForm = document.getElementById('profile-form');
        if (profileForm) {
            profileForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit();
            });
        }
        
        // Character counters for text areas
        this.initializeCharacterCounters();
        
        // ORCID validation
        const orcidField = document.getElementById('orcid');
        if (orcidField) {
            orcidField.addEventListener('blur', (e) => {
                this.validateOrcid(e.target.value);
            });
        }
        
        // Twitter handle formatting
        const twitterField = document.getElementById('twitter');
        if (twitterField) {
            twitterField.addEventListener('input', (e) => {
                this.formatTwitterHandle(e.target);
            });
        }
        
        // Profile completion checker
        const requiredFields = ['bio', 'institution', 'research_interests'];
        requiredFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('input', () => {
                    this.updateProfileCompletion();
                });
            }
        });
    }
    
    /**
     * Initialize character counters for text areas
     */
    initializeCharacterCounters() {
        const textAreas = document.querySelectorAll('textarea[maxlength]');
        textAreas.forEach(textarea => {
            this.createCharacterCounter(textarea);
            textarea.addEventListener('input', () => {
                this.updateCharacterCounter(textarea);
            });
        });
    }
    
    /**
     * Create character counter for a text area
     */
    createCharacterCounter(textarea) {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('div');
        counter.className = 'character-counter';
        counter.id = `${textarea.id}-counter`;
        
        const parent = textarea.parentNode;
        parent.appendChild(counter);
        
        this.updateCharacterCounter(textarea);
    }
    
    /**
     * Update character counter
     */
    updateCharacterCounter(textarea) {
        const counter = document.getElementById(`${textarea.id}-counter`);
        if (!counter) return;
        
        const maxLength = parseInt(textarea.getAttribute('maxlength'));
        const currentLength = textarea.value.length;
        const remaining = maxLength - currentLength;
        
        counter.textContent = `${currentLength}/${maxLength}`;
        
        // Update counter styling based on remaining characters
        counter.className = 'character-counter';
        if (remaining < 50) {
            counter.classList.add('warning');
        }
        if (remaining < 20) {
            counter.classList.add('danger');
        }
    }
    
    /**
     * Load profile data from API
     */
    async loadProfile() {
        try {
            this.showLoading(true);
            
            const response = await fetch(this.apiBaseUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentProfile = data.profile;
                this.populateForm(data.profile);
                this.updateProfileDisplay(data.profile);
                this.updateProfileCompletion();
            } else {
                this.showError('Failed to load profile: ' + data.error);
            }
        } catch (error) {
            this.showError('Error loading profile: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }
    
    /**
     * Handle form submission
     */
    async handleFormSubmit() {
        try {
            const form = document.getElementById('profile-form');
            const formData = new FormData(form);
            
            // Convert FormData to JSON
            const data = {};
            for (let [key, value] of formData.entries()) {
                // Handle checkboxes
                if (form[key] && form[key].type === 'checkbox') {
                    data[key] = form[key].checked;
                } else {
                    data[key] = value;
                }
            }
            
            // Validate required fields
            if (!this.validateForm(data)) {
                return;
            }
            
            const response = await fetch(this.apiBaseUrl, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(data),
                credentials: 'same-origin'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentProfile = result.profile;
                this.showSuccess('Profile updated successfully!');
                this.updateProfileDisplay(result.profile);
                this.updateProfileCompletion();
            } else {
                this.showError('Error updating profile: ' + result.error);
            }
        } catch (error) {
            this.showError('Error updating profile: ' + error.message);
        }
    }
    
    /**
     * Validate form data
     */
    validateForm(data) {
        // Validate email format
        if (data.email && !this.validateEmail(data.email)) {
            this.showError('Please enter a valid email address');
            return false;
        }
        
        // Validate ORCID format
        if (data.orcid && !this.validateOrcidFormat(data.orcid)) {
            this.showError('Please enter a valid ORCID ID (format: 0000-0000-0000-0000)');
            return false;
        }
        
        // Validate URLs
        const urlFields = ['website', 'google_scholar', 'linkedin', 'researchgate'];
        for (let field of urlFields) {
            if (data[field] && !this.validateUrl(data[field])) {
                this.showError(`Please enter a valid URL for ${field.replace('_', ' ')}`);
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Validate email format
     */
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    /**
     * Validate ORCID format
     */
    validateOrcidFormat(orcid) {
        const re = /^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$/;
        return re.test(orcid);
    }
    
    /**
     * Validate URL format
     */
    validateUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }
    
    /**
     * Validate ORCID field with visual feedback
     */
    validateOrcid(orcid) {
        const orcidField = document.getElementById('orcid');
        const feedback = document.getElementById('orcid-feedback') || this.createOrcidFeedback();
        
        if (!orcid) {
            feedback.textContent = '';
            orcidField.classList.remove('valid', 'invalid');
            return;
        }
        
        if (this.validateOrcidFormat(orcid)) {
            feedback.textContent = '✓ Valid ORCID format';
            feedback.className = 'field-feedback valid';
            orcidField.classList.add('valid');
            orcidField.classList.remove('invalid');
        } else {
            feedback.textContent = '✗ Invalid ORCID format (use: 0000-0000-0000-0000)';
            feedback.className = 'field-feedback invalid';
            orcidField.classList.add('invalid');
            orcidField.classList.remove('valid');
        }
    }
    
    /**
     * Create ORCID feedback element
     */
    createOrcidFeedback() {
        const orcidField = document.getElementById('orcid');
        const feedback = document.createElement('div');
        feedback.id = 'orcid-feedback';
        feedback.className = 'field-feedback';
        
        orcidField.parentNode.appendChild(feedback);
        return feedback;
    }
    
    /**
     * Format Twitter handle input
     */
    formatTwitterHandle(input) {
        let value = input.value;
        
        // Remove @ if user types it
        if (value.startsWith('@')) {
            value = value.substring(1);
            input.value = value;
        }
        
        // Show preview
        const preview = document.getElementById('twitter-preview') || this.createTwitterPreview();
        if (value) {
            preview.textContent = `Preview: @${value}`;
            preview.style.display = 'block';
        } else {
            preview.style.display = 'none';
        }
    }
    
    /**
     * Create Twitter preview element
     */
    createTwitterPreview() {
        const twitterField = document.getElementById('twitter');
        const preview = document.createElement('div');
        preview.id = 'twitter-preview';
        preview.className = 'field-preview';
        
        twitterField.parentNode.appendChild(preview);
        return preview;
    }
    
    /**
     * Populate form with profile data
     */
    populateForm(profile) {
        const form = document.getElementById('profile-form');
        if (!form) return;
        
        // User fields
        const userFields = ['first_name', 'last_name', 'email'];
        userFields.forEach(field => {
            const element = document.getElementById(field);
            if (element && profile.user[field]) {
                element.value = profile.user[field];
            }
        });
        
        // Profile fields
        const profileFields = [
            'bio', 'institution', 'research_interests', 'website',
            'orcid', 'academic_title', 'department',
            'google_scholar', 'linkedin', 'researchgate', 'twitter',
            'profile_visibility'
        ];
        
        profileFields.forEach(field => {
            const element = document.getElementById(field);
            if (element && profile[field]) {
                element.value = profile[field];
            }
        });
        
        // Boolean fields
        const booleanFields = ['show_email', 'allow_collaboration'];
        booleanFields.forEach(field => {
            const element = document.getElementById(field);
            if (element) {
                element.checked = profile[field] || false;
            }
        });
        
        // Update character counters
        const textAreas = form.querySelectorAll('textarea[maxlength]');
        textAreas.forEach(textarea => {
            this.updateCharacterCounter(textarea);
        });
        
        // Validate ORCID if present
        if (profile.orcid) {
            this.validateOrcid(profile.orcid);
        }
        
        // Format Twitter handle if present
        if (profile.twitter) {
            this.formatTwitterHandle(document.getElementById('twitter'));
        }
    }
    
    /**
     * Update profile display
     */
    updateProfileDisplay(profile) {
        const displayContainer = document.getElementById('profile-display');
        if (!displayContainer) return;
        
        displayContainer.innerHTML = `
            <div class="profile-header">
                <h2>${this.escapeHtml(profile.full_title || profile.display_name)}</h2>
                ${profile.academic_title ? `<p class="academic-title">${this.escapeHtml(profile.academic_title)}</p>` : ''}
                ${profile.institution ? `<p class="institution">${this.escapeHtml(profile.institution)}</p>` : ''}
                ${profile.department ? `<p class="department">${this.escapeHtml(profile.department)}</p>` : ''}
            </div>
            ${profile.bio ? `
                <div class="profile-bio">
                    <h4>About</h4>
                    <p>${this.escapeHtml(profile.bio)}</p>
                </div>
            ` : ''}
            ${profile.research_interests ? `
                <div class="research-interests">
                    <h4>Research Interests</h4>
                    <p>${this.escapeHtml(profile.research_interests)}</p>
                </div>
            ` : ''}
            ${profile.social_links && profile.social_links.length > 0 ? `
                <div class="social-links">
                    <h4>Professional Links</h4>
                    <ul>
                        ${profile.social_links.map(([name, url]) => `
                            <li><a href="${url}" target="_blank" rel="noopener">${name}</a></li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
            ${profile.orcid ? `
                <div class="orcid-info">
                    <strong>ORCID:</strong> 
                    <a href="https://orcid.org/${profile.orcid}" target="_blank" rel="noopener">
                        ${profile.orcid}
                    </a>
                </div>
            ` : ''}
        `;
    }
    
    /**
     * Update profile completion indicator
     */
    updateProfileCompletion() {
        const completionIndicator = document.getElementById('profile-completion');
        if (!completionIndicator) return;
        
        const requiredFields = ['bio', 'institution', 'research_interests'];
        const completedFields = requiredFields.filter(field => {
            const element = document.getElementById(field);
            return element && element.value.trim();
        });
        
        const percentage = Math.round((completedFields.length / requiredFields.length) * 100);
        
        completionIndicator.innerHTML = `
            <div class="completion-bar">
                <div class="completion-progress" style="width: ${percentage}%"></div>
            </div>
            <span class="completion-text">Profile ${percentage}% complete</span>
        `;
        
        if (percentage === 100) {
            completionIndicator.classList.add('complete');
        } else {
            completionIndicator.classList.remove('complete');
        }
    }
    
    /**
     * Utility functions
     */
    showSuccess(message) {
        this.showMessage(message, 'success');
    }
    
    showError(message) {
        this.showMessage(message, 'error');
    }
    
    showMessage(message, type) {
        const container = document.getElementById('status-message');
        if (!container) return;
        
        container.className = `status-message ${type}`;
        container.textContent = message;
        container.style.display = 'block';
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            container.style.display = 'none';
        }, 5000);
    }
    
    showLoading(show) {
        const loader = document.getElementById('loading-indicator');
        if (loader) {
            loader.style.display = show ? 'block' : 'none';
        }
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Initialize profile manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.profileManager = new ProfileManager();
});