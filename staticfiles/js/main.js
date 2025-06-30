/**
 * SciTeX Web - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize the application
  initApp();
});

function initApp() {
  // Initialize mobile menu toggle
  initMobileMenu();
  
  // Add event listeners
  const getStartedBtn = document.querySelector('.btn-primary');
  if (getStartedBtn) {
    getStartedBtn.addEventListener('click', () => {
      // Add navigation or modal display logic here
    });
  }
}

function initMobileMenu() {
  const mobileToggle = document.querySelector('.mobile-menu-toggle');
  const siteNavigation = document.querySelector('.site-navigation');
  const headerActions = document.querySelector('.header-actions');
  
  if (mobileToggle && siteNavigation) {
    mobileToggle.addEventListener('click', () => {
      const isOpen = siteNavigation.classList.contains('open');
      
      if (isOpen) {
        siteNavigation.classList.remove('open');
        // Remove header actions from mobile menu if they were added
        const mobileActions = siteNavigation.querySelector('.header-actions');
        if (mobileActions) {
          mobileActions.remove();
        }
      } else {
        siteNavigation.classList.add('open');
        
        // Clone header actions into mobile menu on small screens
        if (window.innerWidth <= 576 && headerActions) {
          const mobileActions = headerActions.cloneNode(true);
          mobileActions.style.display = 'flex';
          siteNavigation.appendChild(mobileActions);
        }
      }
    });
    
    // Handle window resize
    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        siteNavigation.classList.remove('open');
        // Remove cloned actions if they exist
        const mobileActions = siteNavigation.querySelector('.header-actions');
        if (mobileActions) {
          mobileActions.remove();
        }
      }
    });
  }
}
