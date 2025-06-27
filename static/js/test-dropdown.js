// Test dropdown visibility
document.addEventListener('DOMContentLoaded', function() {
    const dropdowns = document.querySelectorAll('.dropdown');
    console.log('Found', dropdowns.length, 'dropdowns');
    
    dropdowns.forEach((dropdown, index) => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        if (toggle && menu) {
            const items = menu.querySelectorAll('.dropdown-item');
            console.log(`Dropdown ${index + 1}: "${toggle.textContent.trim()}" has ${items.length} items`);
            items.forEach(item => {
                console.log(`  - ${item.textContent.trim()}`);
            });
        }
    });
});