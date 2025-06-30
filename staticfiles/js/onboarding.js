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
        this.achievements = this.loadAchievements();
        this.progressTracker = new OnboardingProgressTracker();
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
        // Check if user needs onboarding - DISABLED as per user request
        // if (this.shouldShowOnboarding()) {
        //     this.showWelcomeModal();
        // }
        
        // Add help button to all pages - DISABLED as per user request
        // this.addHelpButton();
        
        // Listen for tour triggers
        this.setupEventListeners();
    }
    
    shouldShowOnboarding() {
        // Check localStorage for onboarding status
        const onboardingStatus = localStorage.getItem('scitex_onboarding_completed');
        const userRegistrationDate = document.querySelector('meta[name="user-registration-date"]');
        
        // Extended engagement window: 30 days for new users, re-engagement for returning users
        if (!onboardingStatus && userRegistrationDate) {
            const regDate = new Date(userRegistrationDate.content);
            const daysSinceReg = (Date.now() - regDate.getTime()) / (1000 * 60 * 60 * 24);
            return daysSinceReg <= 30; // Extended from 7 to 30 days
        }
        
        // Re-engagement for returning users who haven't been active
        const lastVisit = localStorage.getItem('scitex_last_visit');
        if (onboardingStatus && lastVisit) {
            const lastVisitDate = new Date(lastVisit);
            const daysSinceLastVisit = (Date.now() - lastVisitDate.getTime()) / (1000 * 60 * 60 * 24);
            if (daysSinceLastVisit >= 14) {
                return this.shouldShowReEngagement();
            }
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
        
        // Track tour completion
        const tourType = this.detectPageType() || 'dashboard';
        this.progressTracker.recordAction('tour_completed', { tourType });
        this.achievements.unlockAchievement('tour_complete');
        
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
        // Enhanced guided project creation with sample projects
        const modal = this.createProjectGuideModal();
        document.body.appendChild(modal);
        setTimeout(() => modal.classList.add('show'), 100);
    }
    
    createProjectGuideModal() {
        const modal = document.createElement('div');
        modal.className = 'onboarding-modal project-guide-modal';
        modal.innerHTML = `
            <div class="onboarding-modal-content">
                <div class="onboarding-header">
                    <h2>🚀 Create Your First Project</h2>
                    <p>Choose a template to get started with your research</p>
                </div>
                
                <div class="project-templates">
                    <div class="template-card" data-template="literature-review">
                        <div class="template-icon">📚</div>
                        <h3>Literature Review</h3>
                        <p>Systematic literature analysis template with Scholar integration</p>
                        <div class="template-features">
                            <span>✓ Paper tracking</span>
                            <span>✓ Citation management</span>
                            <span>✓ Analysis framework</span>
                        </div>
                    </div>
                    
                    <div class="template-card" data-template="research-paper">
                        <div class="template-icon">📄</div>
                        <h3>Research Paper</h3>
                        <p>Complete manuscript template with IMRD structure</p>
                        <div class="template-features">
                            <span>✓ LaTeX template</span>
                            <span>✓ Reference management</span>
                            <span>✓ Collaboration tools</span>
                        </div>
                    </div>
                    
                    <div class="template-card" data-template="data-analysis">
                        <div class="template-icon">📊</div>
                        <h3>Data Analysis</h3>
                        <p>Statistical analysis project with visualization tools</p>
                        <div class="template-features">
                            <span>✓ Jupyter notebooks</span>
                            <span>✓ Visualization templates</span>
                            <span>✓ Statistical workflows</span>
                        </div>
                    </div>
                    
                    <div class="template-card" data-template="blank">
                        <div class="template-icon">📁</div>
                        <h3>Blank Project</h3>
                        <p>Start from scratch with basic structure</p>
                        <div class="template-features">
                            <span>✓ Flexible structure</span>
                            <span>✓ All modules available</span>
                            <span>✓ Custom workflow</span>
                        </div>
                    </div>
                </div>
                
                <div class="modal-actions">
                    <button class="btn-secondary" data-action="cancel">Cancel</button>
                    <button class="btn-primary" data-action="continue" disabled>Continue with Selected Template</button>
                </div>
            </div>
        `;
        
        let selectedTemplate = null;
        
        modal.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            const template = e.target.closest('[data-template]')?.dataset.template;
            
            if (template) {
                // Select template
                modal.querySelectorAll('.template-card').forEach(card => card.classList.remove('selected'));
                e.target.closest('.template-card').classList.add('selected');
                selectedTemplate = template;
                modal.querySelector('[data-action="continue"]').disabled = false;
            } else if (action === 'continue' && selectedTemplate) {
                this.createSampleProject(selectedTemplate);
                this.closeModal(modal);
            } else if (action === 'cancel') {
                this.closeModal(modal);
            }
        });
        
        return modal;
    }
    
    createSampleProject(template) {
        // Track achievement
        this.achievements.unlockAchievement('first_project');
        this.progressTracker.recordAction('project_created', { template });
        
        // Create project based on template
        const projectData = this.getTemplateData(template);
        
        // For now, redirect to dashboard with project creation
        const params = new URLSearchParams({
            template: template,
            guided: 'true',
            achievement: 'first_project'
        });
        
        window.location.href = `/core/dashboard/?${params.toString()}`;
    }
    
    getTemplateData(template) {
        const templates = {
            'literature-review': {
                name: 'My Literature Review',
                description: 'Systematic analysis of research literature',
                structure: ['references/', 'analysis/', 'notes/', 'synthesis/'],
                defaultFiles: ['methodology.md', 'search_terms.md', 'paper_matrix.xlsx']
            },
            'research-paper': {
                name: 'My Research Paper',
                description: 'Academic manuscript with full IMRD structure',
                structure: ['manuscript/', 'data/', 'figures/', 'references/'],
                defaultFiles: ['main.tex', 'abstract.tex', 'introduction.tex', 'methods.tex', 'results.tex', 'discussion.tex']
            },
            'data-analysis': {
                name: 'Data Analysis Project',
                description: 'Statistical analysis with visualization',
                structure: ['data/', 'notebooks/', 'figures/', 'results/'],
                defaultFiles: ['analysis.ipynb', 'data_exploration.ipynb', 'visualization.py']
            },
            'blank': {
                name: 'New Research Project',
                description: 'Flexible project structure',
                structure: ['documents/', 'data/', 'analysis/', 'output/'],
                defaultFiles: ['README.md', 'project_plan.md']
            }
        };
        
        return templates[template] || templates.blank;
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
        localStorage.setItem('scitex_last_visit', new Date().toISOString());
        
        // Track completion achievement
        this.achievements.unlockAchievement('onboarding_completed');
    }
    
    shouldShowReEngagement() {
        // Check if user has made any progress since last visit
        const userProgress = this.progressTracker.getUserProgress();
        if (userProgress.totalActions < 5) {
            return true; // Show re-engagement if minimal activity
        }
        return false;
    }
    
    loadAchievements() {
        return new UserAchievements();
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

/**
 * Progress Tracking System for User Onboarding
 */
class OnboardingProgressTracker {
    constructor() {
        this.storageKey = 'scitex_user_progress';
        this.initializeProgress();
    }
    
    initializeProgress() {
        if (!localStorage.getItem(this.storageKey)) {
            const initialProgress = {
                totalActions: 0,
                completedTours: [],
                projectsCreated: 0,
                modulesExplored: [],
                achievements: [],
                milestones: [],
                firstVisit: new Date().toISOString(),
                lastAction: new Date().toISOString()
            };
            localStorage.setItem(this.storageKey, JSON.stringify(initialProgress));
        }
    }
    
    recordAction(actionType, data = {}) {
        const progress = this.getUserProgress();
        progress.totalActions++;
        progress.lastAction = new Date().toISOString();
        
        switch (actionType) {
            case 'tour_completed':
                if (!progress.completedTours.includes(data.tourType)) {
                    progress.completedTours.push(data.tourType);
                }
                break;
            case 'project_created':
                progress.projectsCreated++;
                break;
            case 'module_explored':
                if (!progress.modulesExplored.includes(data.module)) {
                    progress.modulesExplored.push(data.module);
                }
                break;
        }
        
        this.saveProgress(progress);
        this.checkMilestones(progress);
    }
    
    checkMilestones(progress) {
        const milestones = [
            { id: 'first_tour', condition: () => progress.completedTours.length >= 1, message: 'Completed first tour!' },
            { id: 'tour_master', condition: () => progress.completedTours.length >= 3, message: 'Tour master! You\'ve explored multiple modules.' },
            { id: 'project_creator', condition: () => progress.projectsCreated >= 1, message: 'Created your first project!' },
            { id: 'explorer', condition: () => progress.modulesExplored.length >= 2, message: 'Research explorer! You\'ve tried multiple tools.' },
            { id: 'power_user', condition: () => progress.totalActions >= 20, message: 'Power user! You\'re really getting the hang of SciTeX.' }
        ];
        
        milestones.forEach(milestone => {
            if (!progress.milestones.includes(milestone.id) && milestone.condition()) {
                progress.milestones.push(milestone.id);
                this.showMilestoneNotification(milestone.message);
            }
        });
        
        this.saveProgress(progress);
    }
    
    showMilestoneNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'milestone-notification';
        notification.innerHTML = `
            <div class="milestone-content">
                <div class="milestone-icon">🎉</div>
                <div class="milestone-text">
                    <strong>Milestone Unlocked!</strong>
                    <p>${message}</p>
                </div>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            z-index: 2001;
            animation: milestoneSlideIn 0.5s ease;
            max-width: 300px;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'milestoneSlideOut 0.5s ease forwards';
            setTimeout(() => notification.remove(), 500);
        }, 4000);
    }
    
    getUserProgress() {
        return JSON.parse(localStorage.getItem(this.storageKey) || '{}');
    }
    
    saveProgress(progress) {
        localStorage.setItem(this.storageKey, JSON.stringify(progress));
    }
    
    getProgressSummary() {
        const progress = this.getUserProgress();
        return {
            completionPercentage: this.calculateCompletionPercentage(progress),
            nextSuggestion: this.getNextSuggestion(progress),
            recentActivity: progress.totalActions,
            daysSinceStart: Math.floor((Date.now() - new Date(progress.firstVisit).getTime()) / (1000 * 60 * 60 * 24))
        };
    }
    
    calculateCompletionPercentage(progress) {
        const maxScore = 100;
        let score = 0;
        
        score += Math.min(progress.completedTours.length * 15, 75); // Max 75 for tours
        score += Math.min(progress.projectsCreated * 10, 20); // Max 20 for projects
        score += Math.min(progress.modulesExplored.length * 5, 20); // Max 20 for modules
        
        return Math.min(score, maxScore);
    }
    
    getNextSuggestion(progress) {
        if (progress.completedTours.length === 0) {
            return 'Take your first tour to learn about SciTeX modules';
        }
        if (progress.projectsCreated === 0) {
            return 'Create your first project to start organizing your research';
        }
        if (progress.modulesExplored.length < 2) {
            return 'Explore more research modules to discover new capabilities';
        }
        return 'Keep exploring and building your research workflow!';
    }
}

/**
 * User Achievement System
 */
class UserAchievements {
    constructor() {
        this.storageKey = 'scitex_achievements';
        this.achievements = {
            'first_visit': { name: 'Welcome Aboard', description: 'Visited SciTeX for the first time', icon: '👋' },
            'onboarding_completed': { name: 'Quick Learner', description: 'Completed the onboarding process', icon: '🎓' },
            'first_project': { name: 'Project Pioneer', description: 'Created your first research project', icon: '🚀' },
            'first_search': { name: 'Literature Explorer', description: 'Performed your first Scholar search', icon: '🔍' },
            'first_compilation': { name: 'Document Creator', description: 'Compiled your first LaTeX document', icon: '📝' },
            'tour_complete': { name: 'Guided Explorer', description: 'Completed a guided tour', icon: '🗺️' },
            'power_user': { name: 'Research Pro', description: 'Performed 50+ actions in SciTeX', icon: '⭐' },
            'collaborator': { name: 'Team Player', description: 'Shared or collaborated on a project', icon: '🤝' },
            'data_analyst': { name: 'Data Wizard', description: 'Created your first visualization', icon: '📊' },
            'code_runner': { name: 'Code Executor', description: 'Ran your first code analysis', icon: '💻' }
        };
        this.initializeAchievements();
    }
    
    initializeAchievements() {
        if (!localStorage.getItem(this.storageKey)) {
            localStorage.setItem(this.storageKey, JSON.stringify({}));
        }
    }
    
    unlockAchievement(achievementId) {
        const unlockedAchievements = this.getUnlockedAchievements();
        
        if (!unlockedAchievements[achievementId] && this.achievements[achievementId]) {
            unlockedAchievements[achievementId] = {
                unlockedAt: new Date().toISOString(),
                ...this.achievements[achievementId]
            };
            
            localStorage.setItem(this.storageKey, JSON.stringify(unlockedAchievements));
            this.showAchievementNotification(this.achievements[achievementId]);
        }
    }
    
    showAchievementNotification(achievement) {
        const notification = document.createElement('div');
        notification.className = 'achievement-notification';
        notification.innerHTML = `
            <div class="achievement-content">
                <div class="achievement-icon">${achievement.icon}</div>
                <div class="achievement-text">
                    <strong>Achievement Unlocked!</strong>
                    <h4>${achievement.name}</h4>
                    <p>${achievement.description}</p>
                </div>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
            color: #2d3436;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            z-index: 2000;
            animation: achievementBounce 0.6s ease;
            max-width: 300px;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'achievementSlideOut 0.5s ease forwards';
            setTimeout(() => notification.remove(), 500);
        }, 5000);
    }
    
    getUnlockedAchievements() {
        return JSON.parse(localStorage.getItem(this.storageKey) || '{}');
    }
    
    getAchievementProgress() {
        const unlocked = Object.keys(this.getUnlockedAchievements()).length;
        const total = Object.keys(this.achievements).length;
        return { unlocked, total, percentage: Math.round((unlocked / total) * 100) };
    }
}

// Initialize onboarding when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.sciTexOnboarding = new SciTeXOnboarding();
    
    // Track visit
    localStorage.setItem('scitex_last_visit', new Date().toISOString());
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

.project-templates {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    margin-bottom: 30px;
}

.template-card {
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;
}

.template-card:hover {
    border-color: var(--primary-color, #007bff);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.template-card.selected {
    border-color: var(--primary-color, #007bff);
    background: rgba(0, 123, 255, 0.05);
}

.template-icon {
    font-size: 36px;
    margin-bottom: 15px;
}

.template-card h3 {
    margin-bottom: 10px;
    color: #1a2332;
}

.template-features {
    display: flex;
    flex-direction: column;
    gap: 5px;
    margin-top: 15px;
    font-size: 14px;
    color: #6c757d;
}

.template-features span {
    text-align: left;
}

.modal-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #e9ecef;
}

.btn-primary, .btn-secondary {
    padding: 10px 20px;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;
}

.btn-primary {
    background: var(--primary-color, #007bff);
    color: white;
}

.btn-primary:disabled {
    background: #6c757d;
    cursor: not-allowed;
}

.btn-secondary {
    background: #f8f9fa;
    color: #6c757d;
    border: 1px solid #e9ecef;
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.btn-secondary:hover {
    background: #e9ecef;
}

.achievement-notification, .milestone-notification {
    border-left: 4px solid #ffd700;
}

.achievement-content, .milestone-content {
    display: flex;
    align-items: center;
    gap: 15px;
}

.achievement-icon, .milestone-icon {
    font-size: 24px;
    flex-shrink: 0;
}

.achievement-text h4, .milestone-text strong {
    margin: 0 0 5px 0;
    font-size: 16px;
}

.achievement-text p, .milestone-text p {
    margin: 0;
    font-size: 14px;
    opacity: 0.9;
}

@keyframes achievementBounce {
    0% { transform: translateX(100%); opacity: 0; }
    50% { transform: translateX(-10px); opacity: 1; }
    100% { transform: translateX(0); opacity: 1; }
}

@keyframes achievementSlideOut {
    to { transform: translateX(100%); opacity: 0; }
}

@keyframes milestoneSlideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes milestoneSlideOut {
    to { transform: translateX(100%); opacity: 0; }
}

@media (max-width: 768px) {
    .welcome-options {
        grid-template-columns: 1fr;
    }
    
    .project-templates {
        grid-template-columns: 1fr;
    }
    
    .tour-bubble {
        max-width: 90%;
        left: 5% !important;
        right: 5% !important;
    }
    
    .achievement-notification, .milestone-notification {
        right: 10px;
        left: 10px;
        max-width: none;
    }
    
    .modal-actions {
        flex-direction: column;
        gap: 10px;
    }
    
    .btn-primary, .btn-secondary {
        width: 100%;
    }
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', onboardingStyles);