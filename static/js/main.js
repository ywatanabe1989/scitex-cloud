/**
 * SciTeX Web - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize the application
  initApp();
});

function initApp() {
  // Initialize the application
  
  // Add event listeners
  const getStartedBtn = document.querySelector('.btn-primary');
  if (getStartedBtn) {
    getStartedBtn.addEventListener('click', () => {
      // Add navigation or modal display logic here
    });
  }
}
