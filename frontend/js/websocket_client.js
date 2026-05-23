class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.socket = null;
        this.messageHandler = null;
        this.statusHandler = null;
    }

    connect() {
        if (this.isConnected()) {
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            console.log("Opening WebSocket:", this.url);

            this.socket = new WebSocket(this.url);

            this.socket.onopen = () => {
                console.log("WebSocket connected");
                this.notifyStatus("connected");
                resolve();
            };

            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);

                if (data.timestamp) {
                    data.roundTripMs = Date.now() - data.timestamp;
                } else {
                    data.roundTripMs = null;
                }

                //console.log("Received backend feedback:", data);

                if (this.messageHandler) {
                    this.messageHandler(data);
                }
            };

            this.socket.onerror = (event) => {
                console.error("WebSocket error:", event);
                this.notifyStatus("error");
                reject(new Error("WebSocket connection failed"));
            };

            this.socket.onclose = (event) => {
                console.log("WebSocket closed:", {
                    code: event.code,
                    reason: event.reason,
                    wasClean: event.wasClean,
                });

                this.notifyStatus("disconnected");
            };
        });
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }

        this.notifyStatus("disconnected");
    }

    sendAnalysis(exerciseId, landmarks) {
        if (!this.isConnected()) {
            console.warn("Skipping send because WebSocket is not connected");
            return;
        }

        this.socket.send(JSON.stringify({
            exercise_id: exerciseId,
            landmarks: landmarks,
            timestamp: Date.now(),
        }));
    }

    onMessage(handler) {
        this.messageHandler = handler;
    }

    onStatusChange(handler) {
        this.statusHandler = handler;
    }

    isConnected() {
        return this.socket && this.socket.readyState === WebSocket.OPEN;
    }

    notifyStatus(status) {
        if (this.statusHandler) {
            this.statusHandler(status);
        }
    }
}