class CameraManager {
    constructor(videoElement) {
        this.videoElement = videoElement;
        this.stream = null;
    }

    async start() {
        if (this.stream) {
            return;
        }

        this.stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: CONFIG.CANVAS_WIDTH },
                height: { ideal: CONFIG.CANVAS_HEIGHT },
                facingMode: "user",
            },
            audio: false,
        });

        this.videoElement.srcObject = this.stream;
        await this.videoElement.play();
    }

    stop() {
        if (!this.stream) {
            return;
        }

        this.stream.getTracks().forEach((track) => {
            track.stop();
        });

        this.videoElement.srcObject = null;
        this.stream = null;
    }

    isRunning() {
        return Boolean(this.stream);
    }
}