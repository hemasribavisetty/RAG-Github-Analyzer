(() => {
  var __defProp = Object.defineProperty;
  var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
  var __publicField = (obj, key, value) => __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);

  // app/static/ts/client.ts
  var AnalysisStream = class {
    constructor(repoId, statusElementId) {
      __publicField(this, "ws", null);
      __publicField(this, "statusDiv");
      __publicField(this, "repoId");
      this.repoId = repoId;
      this.statusDiv = document.getElementById(statusElementId);
    }
    connect() {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${protocol}//${window.location.host}/ws/${this.repoId}`;
      console.log(`[TypeScript] Connecting to GitAnalyze Stream: ${wsUrl}`);
      this.ws = new WebSocket(wsUrl);
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.updateUI(data);
      };
      this.ws.onclose = () => {
        console.log("[TypeScript] Stream closed.");
      };
      this.ws.onerror = (error) => {
        console.error("[TypeScript] WebSocket Error:", error);
        this.statusDiv.innerText = "Connection error. Please refresh.";
      };
    }
    updateUI(data) {
      if (data.status === "update") {
        this.statusDiv.innerText = data.message;
        if (data.message.toLowerCase().includes("complete")) {
          this.statusDiv.className = "finished";
          this.statusDiv.classList.remove("pulse");
        }
      }
    }
  };
  window.startGitAnalyzeStream = (repoId, elementId) => {
    const stream = new AnalysisStream(repoId, elementId);
    stream.connect();
  };
})();
