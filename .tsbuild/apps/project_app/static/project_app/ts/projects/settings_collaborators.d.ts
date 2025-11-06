/**
 * Collaborator Autocomplete Handler
 * Provides user search and autocomplete for adding collaborators
 * @module projects/settings_collaborators
 */
interface UserSearchResult {
    username: string;
    email?: string;
}
interface AutocompleteElements {
    input: HTMLInputElement;
    dropdown: HTMLDivElement;
}
declare class CollaboratorAutocomplete {
    private elements;
    private searchTimeout;
    private readonly SEARCH_DELAY_MS;
    private readonly MIN_QUERY_LENGTH;
    constructor();
    private init;
    private setupElements;
    private attachListeners;
    private handleInput;
    private performSearch;
    private renderResults;
    private createUserItem;
    private selectUser;
    private highlightItem;
    private showDropdown;
    private hideDropdown;
    private escapeHtml;
}
//# sourceMappingURL=settings_collaborators.d.ts.map