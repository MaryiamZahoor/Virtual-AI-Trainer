const CONFIG = {
    API_URL: "http://localhost:8000",
    WS_URL: "ws://localhost:8000/ws/analyze",
    MODEL_NAME: "yolov8s-pose",
    MODEL_PATH: "models/",
    CANVAS_WIDTH: 640,
    CANVAS_HEIGHT: 480,
    FPS: 30,
    CONFIDENCE_THRESHOLD: 0.5,
    COLORS: {
        correct: [0, 255, 0],
        warning: [255, 255, 0],
        wrong: [255, 0, 0]
    }
};