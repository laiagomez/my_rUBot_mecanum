from pathlib import Path

from ultralytics import YOLO


TOOL_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = TOOL_ROOT / "workspace"
PRETRAINED_MODEL = "yolo11n.pt"
DATASET_YAML = WORKSPACE_DIR / "roboflow" / "data.yaml"
OUTPUT_DIR = WORKSPACE_DIR / "runs" / "detect"


def main():
    if not DATASET_YAML.is_file():
        raise SystemExit(f"Error: detection dataset configuration not found: {DATASET_YAML}")

    print(f"Loading model: {PRETRAINED_MODEL}")
    model = YOLO(PRETRAINED_MODEL)

    print(f"Starting detection training with: {DATASET_YAML}")
    model.train(
        data=str(DATASET_YAML),
        epochs=50,
        imgsz=640,
        batch=8,
        device="cpu",
        workers=0,
        project=str(OUTPUT_DIR),
        name="train",
        exist_ok=True,
        plots=True,
        save=True,
        verbose=True,
    )

    best_model = OUTPUT_DIR / "train" / "weights" / "best.pt"
    print("Training finished.")
    print(f"Best model: {best_model}")


if __name__ == "__main__":
    main()
