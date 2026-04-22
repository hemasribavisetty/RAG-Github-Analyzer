/**
 * GitAnalyze WebSocket Client
 * Managed real-time connection to the Distributed RAG Engine.
 */

interface WSMessage {
    status: 'update' | 'error';
    message: string;
}

class AnalysisStream {
    private ws: WebSocket | null = null;
    private statusDiv: HTMLElement;
    private repoId: string;

    constructor(repoId: string, statusElementId: string) {
        this.repoId = repoId;
        this.statusDiv = document.getElementById(statusElementId) as HTMLElement;
    }

    public connect(): void {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.repoId}`;
        
        console.log(`[TypeScript] Connecting to GitAnalyze Stream: ${wsUrl}`);
        this.ws = new WebSocket(wsUrl);

        this.ws.onmessage = (event: MessageEvent) => {
            const data: WSMessage = JSON.parse(event.data);
            this.updateUI(data);
        };

        this.ws.onclose = () => {
            console.log("[TypeScript] Stream closed.");
        };

        this.ws.onerror = (error: Event) => {
            console.error("[TypeScript] WebSocket Error:", error);
            this.statusDiv.innerText = "Connection error. Please refresh.";
        };
    }

    private updateUI(data: WSMessage): void {
        if (data.status === 'update') {
            this.statusDiv.innerText = data.message;
            
            if (data.message.toLowerCase().includes('complete')) {
                this.statusDiv.className = 'finished';
                this.statusDiv.classList.remove('pulse');
            }
        }
    }
}

// Global initialization
(window as any).startGitAnalyzeStream = (repoId: string, elementId: string) => {
    const stream = new AnalysisStream(repoId, elementId);
    stream.connect();
};
