# YOLO model-generation tools

Standalone development tools for collecting images, preparing datasets,
training YOLO models and testing them before deployment in ROS 2.

These files are not a ROS package. Runtime perception belongs to
`src/AI_Projects/my_robot_ai_perception`.

## Layout

```text
yolo_model_generation/
|-- 1_prepare_workspaces.py  # create local data folders for both tasks
|-- classification/
|   |-- yolo_classification_model_generation.md
|   |-- images/
|   |-- workspace/             # local data, ignored by Git
|   |-- 2_capture_webcam.py
|   |-- 2_capture_ros.py
|   |-- 3_prepare_dataset.py
|   |-- 4_train.py
|   |-- yolo_models/             # selected models for standalone checks
|   |-- 5_infer_webcam.py
|   `-- 5_infer_ros.py
|-- detection/
|   |-- yolo_detection_model_generation.md
|   |-- images/
|   |-- workspace/             # local data, ignored by Git
|   |-- 4_train.py
|   |-- 5_infer_webcam.py
|   `-- 5_infer_ros.py
`-- pose/
    `-- pose_gesture_webcam.py
```

Create the work folders from the repository root:

```bash
python tools/yolo_model_generation/1_prepare_workspaces.py
```

For step-by-step dataset and training instructions, see
`classification/yolo_classification_model_generation.md` and
`detection/yolo_detection_model_generation.md`.

## Classification workflow

1. Run `1_prepare_workspaces.py` once to create the class photo folders.
2. Capture webcam images from inside the required folder. For example:

```bash
cd tools/yolo_model_generation/classification/workspace/photos/Stop
python ../../../2_capture_webcam.py
```

The capture window previews the live camera image. Press `s` when the sign is
in frame to save the current image and start saving photos. The terminal
prints each photo number and filename. Press Ctrl+C or `q` in the preview
window to stop.
For about 100 photos, stop when the terminal reaches photo 100.

For a ROS 2 camera, set `IMAGE_TOPIC` and `OUTPUT_RELATIVE_PATH` in
`classification/2_capture_ros.py`, then run from the repository root:

```bash
python tools/yolo_model_generation/classification/2_capture_ros.py
```

3. Prepare the dataset and train the model, in this order:

```bash
python tools/yolo_model_generation/classification/3_prepare_dataset.py
python tools/yolo_model_generation/classification/4_train.py
```

The training output is written to
`classification/workspace/runs/classify/train/weights/best.pt`. Copy the
selected model to `classification/yolo_models/yolo11n_cls_g1.pt` before
verification. Then run one of these checks:

```bash
python tools/yolo_model_generation/classification/5_infer_webcam.py
python tools/yolo_model_generation/classification/5_infer_ros.py
```

For a different ROS camera topic or model:

```bash
python tools/yolo_model_generation/classification/5_infer_ros.py \
  --model yolo_models/yolo11n_cls_g2.pt \
  --image-topic /camera/image_raw
```

Copy the same validated deployment model to
`my_robot_ai_perception/models/` before launching the ROS 2 perception node.

## Object-detection workflow

1. Run `1_prepare_workspaces.py` if it has not been run yet.
2. Keep source photos in `detection/workspace/photos/<ClassName>/`. Annotate
   them in Roboflow and export the dataset to
   `detection/workspace/roboflow/`.
3. Verify that paths in `data.yaml` are valid, then train and verify:

```bash
python tools/yolo_model_generation/detection/4_train.py
python tools/yolo_model_generation/detection/5_infer_webcam.py
python tools/yolo_model_generation/detection/5_infer_ros.py
```

All task workspaces are local and ignored by Git.

## Pose example

```bash
python pose/pose_gesture_webcam.py
```

Ultralytics downloads the standard pretrained models when they are not
already cached locally.

## Legacy material

The original scripts, datasets and experiment outputs remain unchanged under
`Documentation/Files/YOLO_model_generation/` during migration.
