class PoseDetector {
    constructor(modelPath) {
        this.modelPath = modelPath;
        this.session = null;
        this.inputName = null;
        this.outputNames = [];
        this.inputSize = 640;
        this.confidenceThreshold = CONFIG.CONFIDENCE_THRESHOLD;
        this.executionProvider = "webgpu";
        this.preprocessCanvas = document.createElement("canvas");
        this.preprocessContext = this.preprocessCanvas.getContext("2d", {
            willReadFrequently: true,
        });
        this.lastTransform = null;
    }

    async load() {
        try {
            if (!window.ort) {
                throw new Error("ONNX Runtime Web is not loaded");
            }

            if (!navigator.gpu) {
                throw new Error("WebGPU is not available in this browser");
            }

            const modelResponse = await fetch(this.modelPath);

            if (!modelResponse.ok) {
                throw new Error(`Model file not found at ${this.modelPath}`);
            }

            const modelBuffer = await modelResponse.arrayBuffer();

            console.log("ONNX model bytes:", modelBuffer.byteLength);

            this.session = await ort.InferenceSession.create(modelBuffer, {
                executionProviders: ["webgpu"],
                graphOptimizationLevel: "all",
            });

            this.inputName = this.session.inputNames[0];
            this.outputNames = this.session.outputNames;

            console.log("Using ONNX Runtime execution provider: webgpu");

            return {
                inputName: this.inputName,
                outputNames: this.outputNames,
                executionProvider: this.executionProvider,
            };
        } catch (error) {
            console.error("Pose model load error:", error);
            throw new Error(this.formatLoadError(error));
        }
    }

    async runTestInference(videoElement) {
        const result = await this.runInference(videoElement);

        return {
            inputName: this.inputName,
            inputShape: result.inputShape,
            outputName: result.outputName,
            outputShape: result.outputShape,
            outputLength: result.outputLength,
            executionProvider: this.executionProvider,
        };
    }

    async detectPose(videoElement) {
        const result = await this.runInference(videoElement);
        return this.decodeOutput(result.outputTensor, videoElement);
    }

    async runInference(videoElement) {
        if (!this.isLoaded()) {
            throw new Error("Pose model is not loaded");
        }

        if (!videoElement.videoWidth || !videoElement.videoHeight) {
            throw new Error("Camera frame is not ready");
        }

        const inputTensor = this.preprocessVideoFrame(videoElement);

        const feeds = {
            [this.inputName]: inputTensor,
        };

        const results = await this.session.run(feeds);
        const outputName = this.outputNames[0];
        const outputTensor = results[outputName];

        return {
            inputTensor,
            outputTensor,
            inputShape: inputTensor.dims,
            outputName,
            outputShape: outputTensor.dims,
            outputLength: outputTensor.data.length,
        };
    }

    preprocessVideoFrame(videoElement) {
        const size = this.inputSize;
        const sourceWidth = videoElement.videoWidth;
        const sourceHeight = videoElement.videoHeight;

        this.preprocessCanvas.width = size;
        this.preprocessCanvas.height = size;

        this.preprocessContext.fillStyle = "black";
        this.preprocessContext.fillRect(0, 0, size, size);

        const scale = Math.min(size / sourceWidth, size / sourceHeight);
        const drawWidth = Math.round(sourceWidth * scale);
        const drawHeight = Math.round(sourceHeight * scale);
        const offsetX = Math.floor((size - drawWidth) / 2);
        const offsetY = Math.floor((size - drawHeight) / 2);

        this.preprocessContext.drawImage(
            videoElement,
            offsetX,
            offsetY,
            drawWidth,
            drawHeight
        );

        this.lastTransform = {
            scale,
            offsetX,
            offsetY,
            sourceWidth,
            sourceHeight,
        };

        const imageData = this.preprocessContext.getImageData(0, 0, size, size);
        const pixels = imageData.data;
        const channelSize = size * size;
        const inputData = new Float32Array(3 * channelSize);

        for (let index = 0; index < channelSize; index += 1) {
            const pixelIndex = index * 4;

            inputData[index] = pixels[pixelIndex] / 255;
            inputData[channelSize + index] = pixels[pixelIndex + 1] / 255;
            inputData[(2 * channelSize) + index] = pixels[pixelIndex + 2] / 255;
        }

        return new ort.Tensor("float32", inputData, [1, 3, size, size]);
    }

    decodeOutput(outputTensor, videoElement) {
        const dims = outputTensor.dims;
        const data = outputTensor.data;

        if (dims.length !== 3) {
            throw new Error(`Unexpected output dimensions: ${dims.join("x")}`);
        }

        const attributeCount = dims[1];
        const candidateCount = dims[2];

        let bestIndex = -1;
        let bestConfidence = 0;

        for (let candidateIndex = 0; candidateIndex < candidateCount; candidateIndex += 1) {
            const confidence = data[(4 * candidateCount) + candidateIndex];

            if (confidence > bestConfidence) {
                bestConfidence = confidence;
                bestIndex = candidateIndex;
            }
        }

        if (bestIndex === -1 || bestConfidence < this.confidenceThreshold) {
            return {
                confidence: bestConfidence,
                keypoints: [],
                backendLandmarks: [],
            };
        }

        const keypoints = [];

        for (let keypointIndex = 0; keypointIndex < 17; keypointIndex += 1) {
            const baseAttribute = 5 + (keypointIndex * 3);

            if (baseAttribute + 2 >= attributeCount) {
                break;
            }

            const modelX = data[(baseAttribute * candidateCount) + bestIndex];
            const modelY = data[((baseAttribute + 1) * candidateCount) + bestIndex];
            const confidence = data[((baseAttribute + 2) * candidateCount) + bestIndex];

            keypoints.push(
                this.mapKeypointToDisplay(modelX, modelY, confidence, videoElement)
            );
        }

        return {
            confidence: bestConfidence,
            keypoints,
            backendLandmarks: keypoints.map((point) => [
                point.sourceX,
                point.sourceY,
                point.confidence,
            ]),
        };
    }

    mapKeypointToDisplay(modelX, modelY, confidence, videoElement) {
        const transform = this.lastTransform;
        const displayWidth = videoElement.clientWidth;
        const displayHeight = videoElement.clientHeight;

        const sourceX = (modelX - transform.offsetX) / transform.scale;
        const sourceY = (modelY - transform.offsetY) / transform.scale;

        const clampedSourceX = Math.max(0, Math.min(sourceX, transform.sourceWidth));
        const clampedSourceY = Math.max(0, Math.min(sourceY, transform.sourceHeight));

        const displayX = displayWidth - ((clampedSourceX / transform.sourceWidth) * displayWidth);
        const displayY = (clampedSourceY / transform.sourceHeight) * displayHeight;

        return {
            x: displayX,
            y: displayY,
            sourceX: clampedSourceX,
            sourceY: clampedSourceY,
            confidence,
        };
    }

    formatLoadError(error) {
        if (error instanceof Error && error.message) {
            return error.message;
        }

        if (typeof error === "string") {
            return error;
        }

        if (typeof error === "number") {
            return `ONNX Runtime Web failed with runtime code: ${error}`;
        }

        try {
            return JSON.stringify(error);
        } catch {
            return "Unknown model loading error";
        }
    }

    isLoaded() {
        return Boolean(this.session);
    }
}