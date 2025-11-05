/**
 * SciTeX Gradient Symlink System - URL-based gradient switching
 * Usage: Add ?gradient=light|radial|soft|subtle to any URL
 * Example: https://scitex.ai/scholar/?gradient=radial
 */

(function() {
    'use strict';
    
    const GRADIENTS = {
        'light': 'hero-silverish-ai-light',
        'radial': 'hero-silverish-ai-radial', 
        'soft': 'hero-silverish-ai-soft',
        'subtle': 'hero-silverish-ai-subtle'
    };
    
    function getGradientFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const gradient = urlParams.get('gradient');
        return GRADIENTS[gradient] ? gradient : 'light'; // Default to 'light'
    }
    
    function applyGradient(gradientName) {
        const gradientClass = GRADIENTS[gradientName];
        if (!gradientClass) return;
        
        const heroElements = document.querySelectorAll('.hero-section');
        
        heroElements.forEach(hero => {
            // Remove all gradient classes
            Object.values(GRADIENTS).forEach(className => {
                hero.classList.remove(className);
            });
            
            // Add the selected gradient class
            hero.classList.add(gradientClass);
        });
        
        console.log(`🎨 Gradient switched to: ${gradientName} (${gradientClass})`);
    }
    
    function addGradientLinks() {
        // Only add in development or when explicitly requested
        if (window.location.hostname === 'localhost' || 
            window.location.hostname === '127.0.0.1' ||
            window.location.search.includes('dev=true')) {
            
            const quickLinks = document.createElement('div');
            quickLinks.id = 'gradient-symlinks';
            quickLinks.innerHTML = `
                <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; background: rgba(26, 35, 50, 0.9); padding: 10px; border-radius: 8px; font-family: monospace; font-size: 12px;">
                    <div style="color: #b5c7d1; margin-bottom: 5px;">🎨 Gradient Symlinks:</div>
                    <a href="?gradient=light" style="color: #8fa4b0; text-decoration: none; margin-right: 8px;">light</a>
                    <a href="?gradient=radial" style="color: #8fa4b0; text-decoration: none; margin-right: 8px;">radial</a>
                    <a href="?gradient=soft" style="color: #8fa4b0; text-decoration: none; margin-right: 8px;">soft</a>
                    <a href="?gradient=subtle" style="color: #8fa4b0; text-decoration: none; margin-right: 8px;">subtle</a>
                    <a href="${window.location.pathname}" style="color: #d4e1e8; text-decoration: none;">reset</a>
                </div>
            `;
            document.body.appendChild(quickLinks);
        }
    }
    
    // Auto-apply gradient on page load
    document.addEventListener('DOMContentLoaded', function() {
        const gradientName = getGradientFromURL();
        if (gradientName) {
            applyGradient(gradientName);
        }
        
        // Add development links
        addGradientLinks();
    });
    
    // Global function for manual switching
    window.setGradient = function(gradientName) {
        if (GRADIENTS[gradientName]) {
            const url = new URL(window.location);
            url.searchParams.set('gradient', gradientName);
            window.location.href = url.toString();
        }
    };
    
    // Global function to reset gradient
    window.resetGradient = function() {
        const url = new URL(window.location);
        url.searchParams.delete('gradient');
        window.location.href = url.toString();
    };
    
})();