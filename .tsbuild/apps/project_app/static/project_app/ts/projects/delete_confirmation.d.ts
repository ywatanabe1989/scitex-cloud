/**
 * Delete Confirmation Handler
 * Enables delete button only when user types exact project path
 * @module projects/delete_confirmation
 */
interface DeleteConfirmationElements {
    confirmInput: HTMLInputElement;
    deleteButton: HTMLButtonElement;
    expectedText: string;
}
declare class DeleteConfirmation {
    private elements;
    constructor();
    private init;
    private setupElements;
    private attachListeners;
    private updateButtonState;
}
//# sourceMappingURL=delete_confirmation.d.ts.map