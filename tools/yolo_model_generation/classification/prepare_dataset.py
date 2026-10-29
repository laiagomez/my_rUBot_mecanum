from pathlib import Path
import shutil
import random
from PIL import Image, ImageOps

# ============================================================
# Configuration
# ============================================================
TOOL_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = TOOL_ROOT / "workspace"
RAW_DATASET_DIR = WORKSPACE_DIR / "photos"
OUTPUT_DATASET_DIR = WORKSPACE_DIR / "traffic_sign_dataset"

CLASSES = [
    "Stop",
    "Right",
    "Left",
    "Give",
    "Nothing",
    "Forbidden",
]

TRAIN_RATIO = 0.80
IMG_SIZE = 640
PADDING_COLOR = (114, 114, 114)

VALID_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]

random.seed(42)


def resize_and_save_image(src_path: Path, dst_path: Path, size: int = 640):
    """
    Resize an image proportionally, pad it to size x size, and save it as JPG.
    """
    with Image.open(src_path) as img:
        img = img.convert("RGB")
        img = ImageOps.pad(
            img,
            (size, size),
            method=Image.Resampling.LANCZOS,
            color=PADDING_COLOR,
            centering=(0.5, 0.5),
        )
        img.save(dst_path, quality=95)


def prepare_folders():
    """
    Create train/val folder structure.
    """
    for split in ["train", "val"]:
        for class_name in CLASSES:
            folder = OUTPUT_DATASET_DIR / split / class_name
            folder.mkdir(parents=True, exist_ok=True)


def process_class(class_name: str):
    """
    Split images of one class into train and val.
    """
    input_class_dir = RAW_DATASET_DIR / class_name

    if not input_class_dir.exists():
        print(f"WARNING: Folder not found: {input_class_dir}")
        return

    image_paths = [
        p for p in input_class_dir.iterdir()
        if p.suffix.lower() in VALID_EXTENSIONS
    ]

    random.shuffle(image_paths)

    n_total = len(image_paths)
    n_train = int(n_total * TRAIN_RATIO)

    train_images = image_paths[:n_train]
    val_images = image_paths[n_train:]

    print(f"{class_name}: {n_total} images -> {len(train_images)} train, {len(val_images)} val")

    for split, images in [("train", train_images), ("val", val_images)]:
        for i, src_path in enumerate(images):
            dst_filename = f"{class_name.lower()}_{i:04d}.jpg"
            dst_path = OUTPUT_DATASET_DIR / split / class_name / dst_filename
            resize_and_save_image(src_path, dst_path, IMG_SIZE)


def main():
    if OUTPUT_DATASET_DIR.exists():
        print(f"Removing existing folder: {OUTPUT_DATASET_DIR}")
        shutil.rmtree(OUTPUT_DATASET_DIR)

    prepare_folders()

    for class_name in CLASSES:
        process_class(class_name)

    print("\nDataset prepared successfully.")
    print(f"Output folder: {OUTPUT_DATASET_DIR}")


if __name__ == "__main__":
    main()
