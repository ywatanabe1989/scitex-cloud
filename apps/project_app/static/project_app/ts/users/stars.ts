/**
 * User stars page functionality
 * Corresponds to: templates/project_app/users/stars.html
 */


console.log("[DEBUG] apps/project_app/static/project_app/ts/users/stars.ts loaded");

class UserStarsPage {
    constructor() {
        this.init();
    }

    private init(): void {
        console.log('[UserStars] Initializing user stars');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new UserStarsPage();
});
