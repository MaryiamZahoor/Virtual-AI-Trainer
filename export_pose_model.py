from pathlib import Path

import onnx
from onnxconverter_common import float16
from ultralytics import YOLO


ROOT_DIR = Path(__file__).resolve().parent

FRONTEND_MODEL_DIR = ROOT_DIR / "frontend" / "models"
FRONTEND_MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "yolov8s-pose.pt"
OUTPUT_NAME = "yolov8s-pose_fp16.onnx"


def export_pose_model():
    model = YOLO(MODEL_NAME)

    exported_path = model.export(
        format="onnx",
        imgsz=640,
        opset=12,
        simplify=True,
        dynamic=False,
    )

    exported_path = Path(exported_path)
    onnx_model = onnx.load(exported_path)

    #fp16_model = float16.convert_float_to_float16(
    #onnx_model,
    #op_block_list=["Resize"]
    #)


    # Final frontend path
    final_path = FRONTEND_MODEL_DIR / OUTPUT_NAME

    # Save FP16 model directly to frontend
    #onnx.save(fp16_model, final_path)
    onnx.save(onnx_model, final_path)

    print(f"Exported FP16 pose model to: {final_path}")


if __name__ == "__main__":
    export_pose_model()