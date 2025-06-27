// SciTeX Cloud - Dropdown Menu JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Get all dropdown toggles
  const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
  
  // Handle click events for all devices
  dropdownToggles.forEach(toggle => {
    toggle.addEventListener('click', function(e) {
      e.preventDefault();
      const parent = this.parentNode;
      const menu = parent.querySelector('.dropdown-menu');
      
      // Close other open dropdowns
      document.querySelectorAll('.dropdown-menu.show').forEach(otherMenu => {
        if (otherMenu !== menu) {
          otherMenu.classList.remove('show');
        }
      });
      
      // Toggle the 'show' class
      menu.classList.toggle('show');
    });
  });
  
  // Close dropdowns when clicking outside
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.dropdown')) {
      document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
        menu.classList.remove('show');
      });
    }
  });
});