class CanvasRenderer {
    constructor(canvasElement, videoElement) {
        this.canvasElement = canvasElement;
        this.videoElement = videoElement;
        this.context = this.canvasElement.getContext("2d");
        this.animationFrameId = null;
        this.keypoints = [];
        this.feedback = null;

        this.skeletonConnections = [
            [5, 6],
            [5, 7],
            [7, 9],
            [6, 8],
            [8, 10],
            [5, 11],
            [6, 12],
            [11, 12],
            [11, 13],
            [13, 15],
            [12, 14],
            [14, 16],
        ];

        this.jointSegments = {
            left_shoulder: [[11, 5], [5, 7]],
            right_shoulder: [[12, 6], [6, 8]],
            left_elbow: [[5, 7], [7, 9]],
            right_elbow: [[6, 8], [8, 10]],
            left_hip: [[5, 11], [11, 13]],
            right_hip: [[6, 12], [12, 14]],
            left_knee: [[11, 13], [13, 15]],
            right_knee: [[12, 14], [14, 16]],
        };

        this.colors = {
            correct: "rgba(18, 183, 106, 0.95)",
            warning: "rgba(247, 144, 9, 0.95)",
            wrong: "rgba(240, 68, 56, 0.95)",
            neutral: "rgba(152, 162, 179, 0.65)",
            point: "rgba(255, 255, 255, 0.95)",
        };
    }

    start() {
        if (this.animationFrameId) {
            return;
        }

        this.resizeCanvas();
        this.render();
    }

    stop() {
        if (this.animationFrameId) {
            window.cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }

        this.keypoints = [];
        this.feedback = null;
        this.clear();
    }

    setKeypoints(keypoints) {
        this.keypoints = keypoints || [];
    }

    setFeedback(feedback) {
        this.feedback = feedback;
    }

    render() {
        this.resizeCanvas();
        this.clear();
        this.drawGuideFrame();
        this.drawPose();

        this.animationFrameId = window.requestAnimationFrame(() => this.render());
    }

    resizeCanvas() {
        const width = this.canvasElement.clientWidth;
        const height = this.canvasElement.clientHeight;

        if (this.canvasElement.width !== width || this.canvasElement.height !== height) {
            this.canvasElement.width = width;
            this.canvasElement.height = height;
        }
    }

    clear() {
        this.context.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);
    }

    drawGuideFrame() {
        const width = this.canvasElement.width;
        const height = this.canvasElement.height;

        if (!width || !height) {
            return;
        }

        this.context.strokeStyle = "rgba(18, 183, 106, 0.25)";
        this.context.lineWidth = 2;
        this.context.setLineDash([12, 10]);
        this.context.strokeRect(18, 18, width - 36, height - 36);
        this.context.setLineDash([]);
    }

    drawPose() {
        if (!this.keypoints.length) {
            return;
        }

        this.drawSkeleton();
        this.drawKeypoints();
    }

    drawSkeleton() {
        this.context.lineWidth = 4;
        this.context.lineCap = "round";

        this.skeletonConnections.forEach(([startIndex, endIndex]) => {
            const start = this.keypoints[startIndex];
            const end = this.keypoints[endIndex];

            if (!this.shouldDrawPoint(start) || !this.shouldDrawPoint(end)) {
                return;
            }

            this.context.strokeStyle = this.getSegmentColor(startIndex, endIndex);
            this.context.beginPath();
            this.context.moveTo(start.x, start.y);
            this.context.lineTo(end.x, end.y);
            this.context.stroke();
        });
    }

    drawKeypoints() {
        this.keypoints.forEach((point) => {
            if (!this.shouldDrawPoint(point)) {
                return;
            }

            this.context.beginPath();
            this.context.arc(point.x, point.y, 5, 0, Math.PI * 2);
            this.context.fillStyle = this.colors.point;
            this.context.fill();

            this.context.lineWidth = 2;
            this.context.strokeStyle = this.colors.neutral;
            this.context.stroke();
        });
    }

    getSegmentColor(startIndex, endIndex) {
        const segmentKey = this.getSegmentKey(startIndex, endIndex);

        if (this.hasJointForSegment(segmentKey, this.feedback?.wrong_joints)) {
            return this.colors.wrong;
        }

        if (this.hasJointForSegment(segmentKey, this.feedback?.warning_joints)) {
            return this.colors.warning;
        }

        if (this.hasJointForSegment(segmentKey, this.feedback?.correct_joints)) {
            return this.colors.correct;
        }

        return this.colors.neutral;
    }

    hasJointForSegment(segmentKey, joints) {
        if (!joints || !joints.length) {
            return false;
        }

        return joints.some((jointName) => {
            const segments = this.jointSegments[jointName] || [];
            return segments.some(([startIndex, endIndex]) => {
                return this.getSegmentKey(startIndex, endIndex) === segmentKey;
            });
        });
    }

    getSegmentKey(startIndex, endIndex) {
        return [startIndex, endIndex].sort((a, b) => a - b).join("-");
    }

    shouldDrawPoint(point) {
        return point && point.confidence >= CONFIG.CONFIDENCE_THRESHOLD;
    }
}