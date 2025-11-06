/**
 * Collaboration session page functionality
 * Corresponds to: templates/writer_app/collaboration/session.html
 */
interface CollaboratorPresence {
    user_id: number;
    username: string;
    is_active: boolean;
}
declare class CollaborationSessionPage {
    private _websocket;
    private _collaborators;
    constructor();
    private init;
    private setupWebSocket;
}
//# sourceMappingURL=session.d.ts.map