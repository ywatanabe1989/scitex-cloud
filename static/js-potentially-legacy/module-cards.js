// // Enhanced module cards with hover effects
// document.addEventListener('DOMContentLoaded', function() {
//     const moduleCards = document.querySelectorAll('.module-card-compact');

//     // Add touch support for mobile devices
//     moduleCards.forEach(card => {
//         let touchTimeout;

//         // Mouse events for desktop
//         card.addEventListener('mouseenter', function() {
//             this.classList.add('expanded');
//         });

//         card.addEventListener('mouseleave', function() {
//             this.classList.remove('expanded');
//         });

//         // Touch events for mobile
//         card.addEventListener('touchstart', function(e) {
//             // Prevent default to avoid triggering mouse events
//             e.preventDefault();

//             // Clear any existing timeout
//             clearTimeout(touchTimeout);

//             // Toggle expanded class
//             if (this.classList.contains('expanded')) {
//                 this.classList.remove('expanded');
//             } else {
//                 // Remove expanded class from all other cards
//                 moduleCards.forEach(otherCard => {
//                     if (otherCard !== this) {
//                         otherCard.classList.remove('expanded');
//                     }
//                 });

//                 // Add expanded class to this card
//                 this.classList.add('expanded');

//                 // Auto-collapse after 5 seconds
//                 touchTimeout = setTimeout(() => {
//                     this.classList.remove('expanded');
//                 }, 5000);
//             }
//         });

//         // Click event for navigation
//         card.addEventListener('click', function(e) {
//             // Don't navigate if clicking on a button
//             if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A') {
//                 return;
//             }

//             // Find the first link in the card
//             const link = this.querySelector('a');
//             if (link && !this.classList.contains('expanded')) {
//                 window.location.href = link.href;
//             }
//         });
//     });

//     // Smooth scroll for anchor links
//     document.querySelectorAll('a[href^="#"]').forEach(anchor => {
//         anchor.addEventListener('click', function(e) {
//             e.preventDefault();
//             const target = document.querySelector(this.getAttribute('href'));
//             if (target) {
//                 target.scrollIntoView({
//                     behavior: 'smooth',
//                     block: 'start'
//                 });
//             }
//         });
//     });

//     // Add parallax effect to hero section
//     const hero = document.querySelector('.hero-landing');
//     if (hero) {
//         window.addEventListener('scroll', () => {
//             const scrolled = window.pageYOffset;
//             const rate = scrolled * -0.5;
//             hero.style.transform = `translateY(${rate}px)`;
//         });
//     }
// });
