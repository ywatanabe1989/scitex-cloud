/**
 * SciTeX Gradient Switcher - Dynamic gradient switching system
 * Allows real-time switching between gradient variants across all pages
 */

class GradientSwitcher {
    constructor() {
        this.gradients = {
            'light': 'hero-silverish-ai-light',
            'radial': 'hero-silverish-ai-radial', 
            'soft': 'hero-silverish-ai-soft',
            'subtle': 'hero-silverish-ai-subtle'
        };
        
        this.currentGradient = this.loadGradientPreference();
        this.init();
    }
    
    init() {
        this.createSwitcher();
        this.applyGradient(this.currentGradient);
        this.bindEvents();
    }
    
    createSwitcher() {
        // Create floating gradient switcher widget
        const switcher = document.createElement('div');
        switcher.id = 'gradient-switcher';
        switcher.innerHTML = `
            <div class="gradient-switcher-toggle" title="Change Gradient Theme">
                🎨
            </div>
            <div class="gradient-switcher-panel">
                <h6>Hero Gradient</h6>
                <div class="gradient-options">
                    <button class="gradient-option" data-gradient="light" title="Light - Soft and approachable">
                        <div class="gradient-preview gradient-preview-light"></div>
                        Light
                    </button>
                    <button class="gradient-option" data-gradient="radial" title="Radial - Focal point effect">
                        <div class="gradient-preview gradient-preview-radial"></div>
                        Radial
                    </button>
                    <button class="gradient-option" data-gradient="soft" title="Soft - Gentle transitions">
                        <div class="gradient-preview gradient-preview-soft"></div>
                        Soft
                    </button>
                    <button class="gradient-option" data-gradient="subtle" title="Subtle - Minimal aesthetic">
                        <div class="gradient-preview gradient-preview-subtle"></div>
                        Subtle
                    </button>
                </div>
                <div class="gradient-info">
                    <small>Current: <span id="current-gradient-name">${this.currentGradient}</span></small>
                </div>
            </div>
        `;
        
        document.body.appendChild(switcher);
        this.addSwitcherStyles();
    }
    
    addSwitcherStyles() {
        const style = document.createElement('style');
        style.textContent = `
            #gradient-switcher {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            .gradient-switcher-toggle {
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, #1a2332 0%, #34495e 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                font-size: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                border: 2px solid rgba(255,255,255,0.1);
            }
            
            .gradient-switcher-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }
            
            .gradient-switcher-panel {
                position: absolute;
                top: 60px;
                right: 0;
                background: white;
                border-radius: 12px;
                padding: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                min-width: 200px;
                opacity: 0;
                visibility: hidden;
                transform: translateY(-10px);
                transition: all 0.3s ease;
                border: 1px solid rgba(0,0,0,0.1);
            }
            
            .gradient-switcher-panel.active {
                opacity: 1;
                visibility: visible;
                transform: translateY(0);
            }
            
            .gradient-switcher-panel h6 {
                margin: 0 0 10px 0;
                font-size: 14px;
                font-weight: 600;
                color: #1a2332;
                text-align: center;
            }
            
            .gradient-options {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                margin-bottom: 10px;
            }
            
            .gradient-option {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 8px;
                border: 2px solid transparent;
                border-radius: 8px;
                background: #f8f9fa;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 11px;
                font-weight: 500;
                color: #1a2332;
            }
            
            .gradient-option:hover {
                border-color: #506b7a;
                background: #e9ecef;
            }
            
            .gradient-option.active {
                border-color: #1a2332;
                background: #d4e1e8;
            }
            
            .gradient-preview {
                width: 30px;
                height: 20px;
                border-radius: 4px;
                margin-bottom: 4px;
                border: 1px solid rgba(0,0,0,0.1);
            }
            
            .gradient-preview-light {
                background: linear-gradient(135deg, #506b7a 0%, #6c8ba0 30%, #8fa4b0 60%, #b5c7d1 100%);
            }
            
            .gradient-preview-radial {
                background: radial-gradient(ellipse at center, #8fa4b0 0%, #6c8ba0 30%, #506b7a 60%, #34495e 80%, #1a2332 100%);
            }
            
            .gradient-preview-soft {
                background: linear-gradient(135deg, #6c8ba0 0%, #8fa4b0 35%, #b5c7d1 65%, #d4e1e8 100%);
            }
            
            .gradient-preview-subtle {
                background: linear-gradient(135deg, #8fa4b0 0%, #b5c7d1 50%, #d4e1e8 100%);
            }
            
            .gradient-info {
                text-align: center;
                color: #6c757d;
                border-top: 1px solid #e9ecef;
                padding-top: 8px;
            }
            
            #current-gradient-name {
                font-weight: 600;
                color: #1a2332;
                text-transform: capitalize;
            }
            
            /* Responsive adjustments */
            @media (max-width: 768px) {
                #gradient-switcher {
                    top: 10px;
                    right: 10px;
                }
                
                .gradient-switcher-toggle {
                    width: 40px;
                    height: 40px;
                    font-size: 16px;
                }
                
                .gradient-switcher-panel {
                    min-width: 180px;
                    padding: 12px;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    bindEvents() {
        const toggle = document.querySelector('.gradient-switcher-toggle');
        const panel = document.querySelector('.gradient-switcher-panel');
        const options = document.querySelectorAll('.gradient-option');
        
        // Toggle panel
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            panel.classList.toggle('active');
        });
        
        // Close panel when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#gradient-switcher')) {
                panel.classList.remove('active');
            }
        });
        
        // Gradient selection
        options.forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                const gradient = option.dataset.gradient;
                this.switchGradient(gradient);
                panel.classList.remove('active');
            });
        });
        
        // Update active state
        this.updateActiveOption();
    }
    
    switchGradient(gradientName) {
        if (!this.gradients[gradientName]) return;
        
        this.currentGradient = gradientName;
        this.applyGradient(gradientName);
        this.saveGradientPreference(gradientName);
        this.updateActiveOption();
        this.updateCurrentGradientDisplay();
        
        // Trigger custom event for other components
        window.dispatchEvent(new CustomEvent('gradientChanged', {
            detail: { gradient: gradientName, className: this.gradients[gradientName] }
        }));
    }
    
    applyGradient(gradientName) {
        const heroElements = document.querySelectorAll('.hero-section');
        const gradientClass = this.gradients[gradientName];
        
        if (!gradientClass) return;
        
        heroElements.forEach(hero => {
            // Remove all gradient classes
            Object.values(this.gradients).forEach(className => {
                hero.classList.remove(className);
            });
            
            // Add the selected gradient class
            hero.classList.add(gradientClass);
        });
    }
    
    updateActiveOption() {
        const options = document.querySelectorAll('.gradient-option');
        options.forEach(option => {
            option.classList.toggle('active', option.dataset.gradient === this.currentGradient);
        });
    }
    
    updateCurrentGradientDisplay() {
        const display = document.getElementById('current-gradient-name');
        if (display) {
            display.textContent = this.currentGradient;
        }
    }
    
    saveGradientPreference(gradientName) {
        try {
            localStorage.setItem('scitex-gradient-preference', gradientName);
        } catch (e) {
            // Fallback to cookie if localStorage is not available
            document.cookie = `scitex-gradient=${gradientName}; path=/; max-age=31536000`;
        }
    }
    
    loadGradientPreference() {
        try {
            const saved = localStorage.getItem('scitex-gradient-preference');
            if (saved && this.gradients[saved]) {
                return saved;
            }
        } catch (e) {
            // Fallback to cookie
            const match = document.cookie.match(/scitex-gradient=([^;]+)/);
            if (match && this.gradients[match[1]]) {
                return match[1];
            }
        }
        
        // Default to 'light' as first choice
        return 'light';
    }
    
    // Public API methods
    getCurrentGradient() {
        return this.currentGradient;
    }
    
    getAvailableGradients() {
        return Object.keys(this.gradients);
    }
    
    setGradient(gradientName) {
        this.switchGradient(gradientName);
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're not on the design page (to avoid conflicts)
    if (!window.location.pathname.includes('/design/')) {
        window.scitexGradientSwitcher = new GradientSwitcher();
    }
});

// Export for manual initialization
window.GradientSwitcher = GradientSwitcher;