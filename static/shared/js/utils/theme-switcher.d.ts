/**
 * SciTeX Theme Switcher
 * Handles Light/Dark mode switching with localStorage persistence and database sync
 */
type Theme = 'light' | 'dark';
interface SciTeXThemeAPI {
    toggle: () => void;
    set: (theme: Theme) => void;
    get: () => Theme;
    LIGHT: Theme;
    DARK: Theme;
}
declare global {
    interface Window {
        SciTeX: {
            theme: SciTeXThemeAPI;
        };
    }
}
export {};
//# sourceMappingURL=theme-switcher.d.ts.map