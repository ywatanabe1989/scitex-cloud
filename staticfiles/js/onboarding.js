/**
 * SciTeX Cloud - User Onboarding System
 * 
 * Interactive welcome flow and guided tours for new users
 */

class SciTeXOnboarding {
    constructor() {
        this.currentStep = 0;
        this.isActive = false;
        this.userData = {};
        this.tours = {
            dashboard: this.createDashboardTour(),
            scholar: this.createScholarTour(),
            writer: this.createWriterTour(),
            viz: this.createVizTour(),
            code: this.createCodeTour()
        };
        
        this.init();
    }
    
    init() {
        // Check if user needs onboarding
        if (this.shouldShowOnboarding()) {
            this.showWelcomeModal();
        }
        
        // Add help button to all pages
        this.addHelpButton();
        
        // Listen for tour triggers
        this.setupEventListeners();
    }
    
    shouldShowOnboarding() {
        // Check localStorage for onboarding status
        const onboardingStatus = localStorage.getItem('scitex_onboarding_completed');
        const userRegistrationDate = document.querySelector('meta[name="user-registration-date"]');
        
        // Show onboarding if not completed and user is new (registered within last 7 days)
        if (!onboardingStatus && userRegistrationDate) {
            const regDate = new Date(userRegistrationDate.content);
            const daysSinceReg = (Date.now() - regDate.getTime()) / (1000 * 60 * 60 * 24);
            return daysSinceReg <= 7;
        }
        
        return false;
    }
    
    showWelcomeModal() {
        const modal = this.createWelcomeModal();
        document.body.appendChild(modal);
        
        // Animate in
        setTimeout(() => {
            modal.classList.add('show');
        }, 100);
    }
    
    createWelcomeModal() {
        const modal = document.createElement('div');
        modal.className = 'onboarding-modal';
        modal.innerHTML = `
            <div class="onboarding-modal-content">
                <div class="onboarding-header">
                    <h2>🎉 Welcome to SciTeX Cloud!</h2>
                    <p>Let's get you started with your scientific research platform</p>
                </div>
                
                <div class="onboarding-body">
                    <div class="welcome-options">
                        <div class="option-card" data-action="quick-tour">
                            <div class="option-icon">🚀</div>
                            <h3>Quick Tour</h3>
                            <p>5-minute overview of all modules</p>
                        </div>
                        
                        <div class="option-card" data-action="create-project">
                            <div class="option-icon">📁</div>
                            <h3>Create Your First Project</h3>
                            <p>Start with a guided project setup</p>
                        </div>
                        
                        <div class="option-card" data-action="explore-scholar">
                            <div class="option-icon">🔍</div>
                            <h3>Explore Scholar</h3>
                            <p>Discover our literature search tool</p>
                        </div>
                        
                        <div class="option-card" data-action="skip">
                            <div class="option-icon">⏭️</div>
                            <h3>Skip for Now</h3>
                            <p>Explore on your own</p>
                        </div>
                    </div>
                </div>
                
                <div class="onboarding-footer">
                    <p><small>You can always access help and tours from the ? button in the top right</small></p>
                </div>
            </div>
        `;
        
        // Add event listeners
        modal.addEventListener('click', (e) => {
            const action = e.target.closest('[data-action]')?.dataset.action;
            if (action) {
                this.handleWelcomeAction(action);
                this.closeModal(modal);
            }
        });
        
        return modal;
    }
    
    handleWelcomeAction(action) {
        switch (action) {
            case 'quick-tour':
                this.startTour('dashboard');
                break;
            case 'create-project':
                this.showProjectCreationGuide();
                break;
            case 'explore-scholar':
                window.location.href = '/scholar/?tour=true';
                break;
            case 'skip':
                this.markOnboardingCompleted();
                break;
        }
    }
    
    startTour(tourType) {
        const tour = this.tours[tourType];
        if (!tour) return;
        
        this.currentTour = tour;
        this.currentStep = 0;
        this.isActive = true;
        
        this.showTourStep(tour[0]);
    }
    
    showTourStep(step) {
        // Remove existing tour elements
        this.removeTourElements();
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'tour-overlay';
        document.body.appendChild(overlay);
        
        // Create tour bubble
        const bubble = this.createTourBubble(step);
        document.body.appendChild(bubble);
        
        // Highlight target element
        if (step.target) {
            this.highlightElement(step.target);
        }
        
        // Position bubble
        this.positionTourBubble(bubble, step);
    }
    
    createTourBubble(step) {
        const bubble = document.createElement('div');
        bubble.className = 'tour-bubble';
        bubble.innerHTML = `
            <div class=\"tour-content\">
                <h4>${step.title}</h4>
                <p>${step.content}</p>
                ${step.image ? `<img src=\"${step.image}\" alt=\"Tour step\" class=\"tour-image\">` : ''}
            </div>
            <div class=\"tour-controls\">
                <button class=\"tour-btn tour-btn-secondary\" data-action=\"skip\">Skip Tour</button>
                <div class=\"tour-progress\">
                    <span>${this.currentStep + 1} of ${this.currentTour.length}</span>
                </div>
                <div class=\"tour-navigation\">
                    ${this.currentStep > 0 ? '<button class=\"tour-btn tour-btn-outline\" data-action=\"prev\">Previous</button>' : ''}
                    <button class=\"tour-btn tour-btn-primary\" data-action=\"next\">
                        ${this.currentStep < this.currentTour.length - 1 ? 'Next' : 'Finish'}
                    </button>
                </div>
            </div>
        `;
        
        // Add event listeners
        bubble.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            if (action) {
                this.handleTourAction(action);
                e.stopPropagation();
            }
        });
        
        return bubble;
    }
    
    handleTourAction(action) {
        switch (action) {
            case 'next':
                if (this.currentStep < this.currentTour.length - 1) {
                    this.currentStep++;
                    this.showTourStep(this.currentTour[this.currentStep]);
                } else {
                    this.finishTour();
                }
                break;
            case 'prev':
                if (this.currentStep > 0) {
                    this.currentStep--;
                    this.showTourStep(this.currentTour[this.currentStep]);
                }
                break;
            case 'skip':
                this.finishTour();
                break;
        }
    }
    
    finishTour() {
        this.removeTourElements();
        this.isActive = false;
        this.markOnboardingCompleted();
        
        // Show completion message
        this.showNotification('Tour completed! You can restart any tour from the help menu.', 'success');
    }
    
    createDashboardTour() {
        return [
            {
                title: 'Welcome to Your Dashboard',
                content: 'This is your central hub for managing all your research projects. From here you can access all SciTeX modules.',
                target: '.dashboard-header'
            },
            {
                title: 'Your Projects',
                content: 'View and manage all your research projects. Click on any project to see its file structure and details.',
                target: '.projects-section'
            },
            {
                title: 'Research Modules',
                content: 'Access Scholar for literature search, Writer for document creation, and other research tools.',
                target: '.modules-grid'
            },
            {
                title: 'Quick Actions',
                content: 'Create new projects, upload files, or start working with our research tools directly from here.',
                target: '.quick-actions'
            }
        ];
    }
    
    createScholarTour() {
        return [
            {
                title: 'SciTeX Scholar',
                content: 'Your intelligent literature discovery platform. Search across millions of scientific papers.',
                target: '.hero-section'
            },
            {
                title: 'Smart Search',
                content: 'Enter your research query here. Scholar uses AI to understand context and find relevant papers.',
                target: '.search-input'
            },
            {
                title: 'Search Options',
                content: 'Customize your search with filters for date range, publication type, and access level.',
                target: '.search-options'
            },
            {
                title: 'Results Analysis',
                content: 'View comprehensive paper details, abstracts, and citation information for informed research.',
                target: '.results-preview'
            }
        ];
    }
    
    createWriterTour() {
        return [
            {
                title: 'SciTeX Writer',
                content: 'Professional LaTeX editor designed specifically for scientific writing and publication.',
                target: '.hero-section'
            },
            {
                title: 'Live Editor',
                content: 'Write your LaTeX code here with intelligent autocompletion and scientific libraries support.',
                target: '.doc-source'
            },
            {
                title: 'Real-time Preview',
                content: 'See your document rendered in real-time as you type. Perfect for immediate feedback.',
                target: '.doc-preview'
            },
            {
                title: 'Compilation Tools',
                content: 'Compile your document to PDF, manage references, and export in various formats.',
                target: '.doc-toolbar'
            }
        ];
    }
    
    createVizTour() {
        return [
            {
                title: 'SciTeX Viz',
                content: 'Create publication-ready scientific visualizations and interactive plots.',
                target: '.hero-section'
            },
            {
                title: 'Visualization Types',
                content: 'Choose from various scientific plot types optimized for research publications.',
                target: '.row.g-4'
            }
        ];
    }
    
    createCodeTour() {
        return [
            {
                title: 'SciTeX Code',
                content: 'Reproducible scientific computing environment with integrated data analysis tools.',
                target: '.hero-section'
            },
            {
                title: 'Key Features',
                content: 'Explore intelligent code completion, integrated visualization, and reproducible research tools.',
                target: '.row.g-4'
            }
        ];
    }
    
    addHelpButton() {
        // Check if help button already exists
        if (document.querySelector('.help-button')) return;
        
        const helpButton = document.createElement('button');
        helpButton.className = 'help-button';
        helpButton.innerHTML = '?';
        helpButton.title = 'Help & Tours';
        
        helpButton.addEventListener('click', () => {
            this.showHelpMenu();
        });
        
        // Position in top right corner
        helpButton.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            background: var(--primary-color, #007bff);
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        `;
        
        document.body.appendChild(helpButton);
    }
    
    showHelpMenu() {
        const menu = document.createElement('div');
        menu.className = 'help-menu';
        menu.innerHTML = `
            <div class=\"help-menu-content\">
                <h3>Help & Tours</h3>
                <div class=\"help-options\">
                    <button data-action=\"tour-dashboard\">📊 Dashboard Tour</button>
                    <button data-action=\"tour-scholar\">🔍 Scholar Tour</button>
                    <button data-action=\"tour-writer\">📝 Writer Tour</button>
                    <button data-action=\"tour-viz\">📈 Viz Tour</button>
                    <button data-action=\"tour-code\">💻 Code Tour</button>
                    <hr>
                    <button data-action=\"documentation\">📚 Documentation</button>
                    <button data-action=\"video-tutorials\">🎥 Video Tutorials</button>
                    <button data-action=\"contact-support\">💬 Contact Support</button>
                </div>
                <button class=\"help-close\" data-action=\"close\">×</button>
            </div>
        `;
        
        menu.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            if (action) {
                this.handleHelpAction(action);
                document.body.removeChild(menu);
            }
        });
        
        document.body.appendChild(menu);
        
        // Position near help button
        const helpButton = document.querySelector('.help-button');
        const rect = helpButton.getBoundingClientRect();
        menu.style.cssText = `
            position: fixed;
            top: ${rect.bottom + 10}px;
            right: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            z-index: 1001;
            padding: 20px;
            min-width: 200px;
        `;
    }
    
    handleHelpAction(action) {
        switch (action) {
            case 'tour-dashboard':
                this.startTour('dashboard');
                break;
            case 'tour-scholar':
                window.location.href = '/scholar/?tour=true';
                break;
            case 'tour-writer':
                window.location.href = '/writer/?tour=true';
                break;
            case 'tour-viz':
                window.location.href = '/viz/?tour=true';
                break;
            case 'tour-code':
                window.location.href = '/code/?tour=true';
                break;
            case 'documentation':
                window.open('/api-docs/', '_blank');
                break;
            case 'video-tutorials':
                this.showComingSoon('Video tutorials');
                break;
            case 'contact-support':
                window.location.href = 'mailto:support@scitex.ai';
                break;
        }
    }
    
    showProjectCreationGuide() {
        // Implementation for guided project creation
        this.showNotification('Project creation guide coming soon!', 'info');
    }
    
    showComingSoon(feature) {
        this.showNotification(`${feature} coming soon!`, 'info');
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class=\"notification-content\">
                <span>${message}</span>
                <button class=\"notification-close\" onclick=\"this.parentElement.parentElement.remove()\">×</button>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1'};
            color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#0c5460'};
            padding: 12px 20px;
            border-radius: 6px;
            border: 1px solid ${type === 'success' ? '#c3e6cb' : type === 'error' ? '#f5c6cb' : '#bee5eb'};
            z-index: 2000;
            animation: slideDown 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    markOnboardingCompleted() {
        localStorage.setItem('scitex_onboarding_completed', 'true');
        localStorage.setItem('scitex_onboarding_date', new Date().toISOString());
    }
    
    // Utility methods
    highlightElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.classList.add('tour-highlight');
        }
    }
    
    positionTourBubble(bubble, step) {
        if (!step.target) {
            // Center the bubble if no target
            bubble.style.cssText += `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
            `;
            return;
        }
        
        const target = document.querySelector(step.target);
        if (target) {
            const rect = target.getBoundingClientRect();
            bubble.style.cssText += `
                position: fixed;
                top: ${rect.bottom + 20}px;
                left: ${Math.max(20, rect.left)}px;
                max-width: 300px;
            `;
        }
    }
    
    removeTourElements() {
        // Remove tour overlay
        const overlay = document.querySelector('.tour-overlay');
        if (overlay) overlay.remove();
        
        // Remove tour bubble
        const bubble = document.querySelector('.tour-bubble');
        if (bubble) bubble.remove();
        
        // Remove highlights
        document.querySelectorAll('.tour-highlight').forEach(el => {
            el.classList.remove('tour-highlight');
        });
    }
    
    closeModal(modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            if (modal.parentElement) {
                modal.remove();
            }
        }, 300);
    }
    
    setupEventListeners() {
        // Listen for URL parameters to start tours
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('tour')) {
            const tourType = this.detectPageType();
            if (tourType) {
                setTimeout(() => this.startTour(tourType), 1000);
            }
        }
    }
    
    detectPageType() {
        const path = window.location.pathname;
        if (path.includes('/scholar/')) return 'scholar';
        if (path.includes('/writer/')) return 'writer';
        if (path.includes('/viz/')) return 'viz';
        if (path.includes('/code/')) return 'code';
        if (path.includes('/dashboard/')) return 'dashboard';
        return null;
    }
}

// Initialize onboarding when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.sciTexOnboarding = new SciTeXOnboarding();
});

// CSS Styles for onboarding system
const onboardingStyles = `
<style>
.onboarding-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.onboarding-modal.show {
    opacity: 1;
}

.onboarding-modal-content {
    background: white;
    border-radius: 12px;
    padding: 40px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
}

.onboarding-header {
    text-align: center;
    margin-bottom: 30px;
}

.onboarding-header h2 {
    color: #1a2332;
    margin-bottom: 10px;
}

.welcome-options {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-bottom: 30px;
}

.option-card {
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.option-card:hover {
    border-color: var(--primary-color, #007bff);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.option-icon {
    font-size: 32px;
    margin-bottom: 10px;
}

.option-card h3 {
    margin-bottom: 8px;
    color: #1a2332;
}

.tour-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 8000;
}

.tour-bubble {
    position: fixed;
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    z-index: 8001;
    max-width: 350px;
    animation: tourBubbleIn 0.3s ease;
}

.tour-content h4 {
    margin-bottom: 10px;
    color: #1a2332;
}

.tour-content p {
    margin-bottom: 15px;
    line-height: 1.5;
}

.tour-image {
    width: 100%;
    max-width: 200px;
    border-radius: 6px;
    margin: 10px 0;
}

.tour-controls {
    border-top: 1px solid #e9ecef;
    padding-top: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.tour-navigation {
    display: flex;
    gap: 10px;
}

.tour-btn {
    padding: 8px 16px;
    border-radius: 6px;
    border: 1px solid #e9ecef;
    background: white;
    cursor: pointer;
    transition: all 0.2s ease;
}

.tour-btn-primary {
    background: var(--primary-color, #007bff);
    color: white;
    border-color: var(--primary-color, #007bff);
}

.tour-btn-secondary {
    color: #6c757d;
}

.tour-btn:hover {
    transform: translateY(-1px);
}

.tour-highlight {
    position: relative;
    z-index: 8002;
    box-shadow: 0 0 0 4px var(--primary-color, #007bff);
    border-radius: 4px;
}

.help-menu-content {
    position: relative;
}

.help-menu-content h3 {
    margin-bottom: 15px;
    color: #1a2332;
}

.help-options button {
    display: block;
    width: 100%;
    padding: 10px;
    margin-bottom: 8px;
    border: none;
    background: #f8f9fa;
    border-radius: 6px;
    cursor: pointer;
    text-align: left;
    transition: background 0.2s ease;
}

.help-options button:hover {
    background: #e9ecef;
}

.help-close {
    position: absolute;
    top: -10px;
    right: -10px;
    width: 30px;
    height: 30px;
    border: none;
    background: #dc3545;
    color: white;
    border-radius: 50%;
    cursor: pointer;
    font-size: 16px;
    line-height: 1;
}

@keyframes tourBubbleIn {
    from {
        opacity: 0;
        transform: scale(0.8);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateX(-50%) translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
    }
}

.notification {
    animation: slideDown 0.3s ease;
}

.notification-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}

.notification-close {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

@media (max-width: 768px) {
    .welcome-options {
        grid-template-columns: 1fr;
    }
    
    .tour-bubble {
        max-width: 90%;
        left: 5% !important;
        right: 5% !important;
    }
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', onboardingStyles);