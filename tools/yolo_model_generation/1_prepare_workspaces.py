from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parent
CLASSES = ("Stop", "Right", "Left", "Give", "Nothing", "Forbidden")
DETECTION_CLASSES = ("Stop", "Right", "Left", "Give", "Forbidden")


def create_class_folders(parent: Path, classes: tuple[str, ...]) -> None:
    for class_name in classes:
        (parent / class_name).mkdir(parents=True, exist_ok=True)


def main() -> None:
    classification_workspace = TOOL_DIR / "classification" / "workspace"
    detection_workspace = TOOL_DIR / "detection" / "workspace"

    create_class_folders(classification_workspace / "photos", CLASSES)
    for split in ("train", "val"):
        create_class_folders(
            classification_workspace / "traffic_sign_dataset" / split,
            CLASSES,
        )
    (classification_workspace / "runs" / "classify").mkdir(
        parents=True,
        exist_ok=True,
    )

    create_class_folders(detection_workspace / "photos", DETECTION_CLASSES)
    (detection_workspace / "roboflow").mkdir(parents=True, exist_ok=True)
    (detection_workspace / "runs" / "detect").mkdir(
        parents=True,
        exist_ok=True,
    )

    print(f"Classification workspace: {classification_workspace}")
    print(f"Detection workspace: {detection_workspace}")


if __name__ == "__main__":
    main()
