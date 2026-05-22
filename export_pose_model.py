from pathlib import Path

from ultralytics import YOLO


ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_MODEL_DIR = ROOT_DIR / "frontend" / "models"
FRONTEND_MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "yolov8s-pose.pt"
OUTPUT_NAME = "yolov8s-pose.onnx"


def export_pose_model():
    model = YOLO(MODEL_NAME)

    exported_path = model.export(
        format="onnx",
        imgsz=640,
        opset=17,
        simplify=True,
        dynamic=False,
    )

    exported_path = Path(exported_path)
    final_path = FRONTEND_MODEL_DIR / OUTPUT_NAME

    if final_path.exists():
        final_path.unlink()

    exported_path.replace(final_path)

    print(f"Exported pose model to: {final_path}")


if __name__ == "__main__":
    export_pose_model()