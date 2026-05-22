class VirtualTrainerApp {
    constructor() {
        this.apiClient = new ApiClient(CONFIG.API_URL);
        this.websocketClient = new WebSocketClient(CONFIG.WS_URL);
        this.feedbackRenderer = new FeedbackRenderer();
        this.poseDetector = new PoseDetector(`models/${CONFIG.MODEL_NAME}.onnx`);

        this.exerciseSelect = document.getElementById("exercise-select");
        this.startButton = document.getElementById("start-btn");
        this.stopButton = document.getElementById("stop-btn");
        this.startCameraButton = document.getElementById("start-camera-btn");
        this.stopCameraButton = document.getElementById("stop-camera-btn");
        this.runInferenceButton = document.getElementById("run-inference-btn");
        this.connectionDot = document.getElementById("connection-dot");
        this.connectionText = document.getElementById("connection-text");
        this.cameraStatus = document.getElementById("camera-status");

        this.cameraVideo = document.getElementById("camera-video");
        this.poseCanvas = document.getElementById("pose-canvas");

        this.cameraManager = new CameraManager(this.cameraVideo);
        this.canvasRenderer = new CanvasRenderer(this.poseCanvas, this.cameraVideo);

        this.demoTimer = null;
        this.demoFrameIndex = 0;
        this.demoFrames = [];
        this.poseModelLoaded = false;

        this.poseTimer = null;
        this.poseBusy = false;
        this.poseFps = 5;
        this.liveAnalysisRunning = false;
    }

    async init() {
        this.registerHandlers();
        await this.loadExercises();
        await this.loadPoseModel();
        this.updateButtonStates();
    }

    registerHandlers() {
        this.startButton.addEventListener("click", () => this.startDemo());
        this.stopButton.addEventListener("click", () => this.stopDemo());
        this.startCameraButton.addEventListener("click", () => this.startLiveAnalysis());
        this.stopCameraButton.addEventListener("click", () => this.stopLiveAnalysis());
        this.runInferenceButton.addEventListener("click", () => this.runTestInference());

        this.exerciseSelect.addEventListener("change", () => {
            this.updateButtonStates();
        });

        this.websocketClient.onMessage((data) => {
            this.feedbackRenderer.render(data);
            this.canvasRenderer.setFeedback(data);
        });

        this.websocketClient.onStatusChange((status) => {
            this.renderConnectionStatus(status);
        });
    }

    async loadExercises() {
        try {
            const exercises = await this.apiClient.getExercises();

            this.exerciseSelect.innerHTML = "";

            exercises.forEach((exercise) => {
                const option = document.createElement("option");
                option.value = exercise.id;
                option.textContent = exercise.name;
                this.exerciseSelect.appendChild(option);
            });

            this.updateButtonStates();
        } catch (error) {
            this.exerciseSelect.innerHTML = "<option value=\"\">Unable to load exercises</option>";
            this.addLogMessage(error.message);
            this.updateButtonStates();
        }
    }

    async loadPoseModel() {
        try {
            const modelInfo = await this.poseDetector.load();

            this.poseModelLoaded = true;

            this.addLogMessage(
                `Pose model loaded ${CONFIG.MODEL_NAME} with ${modelInfo.executionProvider}. Input: ${modelInfo.inputName}, outputs: ${modelInfo.outputNames.join(", ")}`
            );
        } catch (error) {
            this.poseModelLoaded = false;
            this.addLogMessage(`Pose model unavailable: ${error.message}`);
        }

        this.updateButtonStates();
    }

    async startDemo() {
        const exerciseId = this.exerciseSelect.value;

        if (!exerciseId) {
            return;
        }

        if (exerciseId !== "squats") {
            this.addLogMessage("Demo landmarks are currently available for squats only.");
            return;
        }

        try {
            await this.websocketClient.connect();

            this.demoFrames = DemoLandmarks.getSquatRepSequence();
            this.demoFrameIndex = 0;

            this.demoTimer = window.setInterval(() => {
                this.sendNextDemoFrame(exerciseId);
            }, 1000 / CONFIG.FPS);

            this.updateButtonStates();
        } catch (error) {
            this.addLogMessage(error.message);
        }
    }

    stopDemo() {
        if (this.demoTimer) {
            window.clearInterval(this.demoTimer);
            this.demoTimer = null;
        }

        this.websocketClient.disconnect();
        this.updateButtonStates();
    }

    sendNextDemoFrame(exerciseId) {
        if (this.demoFrameIndex >= this.demoFrames.length) {
            this.stopDemo();
            return;
        }

        const landmarks = this.demoFrames[this.demoFrameIndex];
        this.websocketClient.sendAnalysis(exerciseId, landmarks);
        this.demoFrameIndex += 1;
    }

    async startLiveAnalysis() {
        const exerciseId = this.exerciseSelect.value;

        if (!exerciseId) {
            this.addLogMessage("Select an exercise before starting live analysis.");
            return;
        }

        if (!this.poseModelLoaded) {
            this.addLogMessage("Pose model is not loaded yet.");
            return;
        }

        try {
            await this.websocketClient.connect();
            await this.cameraManager.start();

            this.liveAnalysisRunning = true;
            this.canvasRenderer.start();
            this.startPoseLoop();

            this.cameraStatus.textContent = "Live analysis on";
            this.updateButtonStates();
        } catch (error) {
            this.cameraStatus.textContent = "Camera unavailable";
            this.addLogMessage("Unable to start live analysis. Check camera permission and backend connection.");
            this.stopLiveAnalysis();
        }
    }

    stopLiveAnalysis() {
        this.liveAnalysisRunning = false;

        this.stopPoseLoop();
        this.canvasRenderer.stop();
        this.cameraManager.stop();
        this.websocketClient.disconnect();

        this.cameraStatus.textContent = "Camera off";
        this.updateButtonStates();
    }

    async runTestInference() {
        try {
            const result = await this.poseDetector.runTestInference(this.cameraVideo);

            this.addLogMessage(
                `Inference complete with ${result.executionProvider}. Input shape: ${result.inputShape.join("x")}, output shape: ${result.outputShape.join("x")}, values: ${result.outputLength}`
            );
        } catch (error) {
            this.addLogMessage(`Inference failed: ${error.message}`);
        }
    }

    startPoseLoop() {
        if (!this.poseModelLoaded || this.poseTimer) {
            return;
        }

        const intervalMs = 1000 / this.poseFps;

        this.poseTimer = window.setInterval(() => {
            if (!this.poseBusy && this.cameraManager.isRunning()) {
                this.detectCurrentPose();
            }
        }, intervalMs);
    }

    stopPoseLoop() {
        if (this.poseTimer) {
            window.clearInterval(this.poseTimer);
            this.poseTimer = null;
        }

        this.poseBusy = false;
        this.canvasRenderer.setKeypoints([]);
        this.canvasRenderer.setFeedback(null);
    }

    async detectCurrentPose() {
        this.poseBusy = true;

        try {
            const pose = await this.poseDetector.detectPose(this.cameraVideo);

            this.canvasRenderer.setKeypoints(pose.keypoints);

            if (this.liveAnalysisRunning && pose.backendLandmarks.length) {
                this.websocketClient.sendAnalysis(
                    this.exerciseSelect.value,
                    pose.backendLandmarks
                );
            }
        } catch (error) {
            this.addLogMessage(`Pose detection failed: ${error.message}`);
            this.stopLiveAnalysis();
        } finally {
            this.poseBusy = false;
        }
    }

    updateButtonStates() {
        const hasExercise = Boolean(this.exerciseSelect.value);
        const demoRunning = Boolean(this.demoTimer);
        const cameraRunning = this.cameraManager.isRunning();

        this.startButton.disabled = !hasExercise || demoRunning || this.liveAnalysisRunning;
        this.stopButton.disabled = !demoRunning;

        this.startCameraButton.disabled =
            !hasExercise || !this.poseModelLoaded || this.liveAnalysisRunning || demoRunning;

        this.stopCameraButton.disabled = !this.liveAnalysisRunning;

        this.runInferenceButton.disabled = !this.poseModelLoaded || !cameraRunning;

        this.exerciseSelect.disabled = demoRunning || this.liveAnalysisRunning;
    }

    renderConnectionStatus(status) {
        this.connectionDot.classList.remove("connected", "error");

        if (status === "connected") {
            this.connectionDot.classList.add("connected");
            this.connectionText.textContent = "Connected";
            return;
        }

        if (status === "error") {
            this.connectionDot.classList.add("error");
            this.connectionText.textContent = "Connection error";
            return;
        }

        this.connectionText.textContent = "Disconnected";
    }

    addLogMessage(message) {
        const eventLog = document.getElementById("event-log");
        const item = document.createElement("li");
        item.textContent = message;
        eventLog.prepend(item);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const app = new VirtualTrainerApp();
    app.init();
});