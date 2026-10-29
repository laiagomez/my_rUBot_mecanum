# YOLO model-generation tools

Standalone development tools for collecting images, preparing datasets,
training YOLO models and testing them before deployment in ROS 2.

These files are not a ROS package. Runtime perception belongs to
`src/AI_Projects/my_robot_ai_perception`.

## Layout

```text
yolo_model_generation/
|-- classification/
|   |-- capture_webcam.py
|   |-- capture_ros.py
|   |-- prepare_dataset.py
|   |-- train.py
|   |-- infer_webcam.py
|   `-- infer_ros.py
|-- detection/
|   |-- train.py
|   |-- infer_webcam.py
|   `-- infer_ros.py
|-- pose/
|   `-- pose_gesture_webcam.py
`-- workspace/                 # generated locally; ignored by Git
```

The local workspace contains large or reproducible artifacts:

```text
workspace/
|-- photos/<ClassName>/
|-- traffic_sign_dataset/
|-- roboflow/data.yaml
`-- runs/
```

## Classification workflow

Capture webcam images from inside the required class folder:

```bash
mkdir -p workspace/photos/Stop
cd workspace/photos/Stop
python ../../../classification/capture_webcam.py
```

For a ROS 2 camera, set `IMAGE_TOPIC` and `OUTPUT_RELATIVE_PATH` in
`classification/capture_ros.py`, then run:

```bash
python classification/capture_ros.py
```

Prepare and train the dataset:

```bash
python classification/prepare_dataset.py
python classification/train.py
```

Test the trained classifier:

```bash
python classification/infer_webcam.py
python classification/infer_ros.py
```

The best model is written to
`workspace/runs/classify/train/weights/best.pt`. Copy only the validated
deployment model to `my_robot_ai_perception/models/`.

## Object-detection workflow

Export a YOLO detection dataset from Roboflow and place its images, labels and
`data.yaml` under `workspace/roboflow/`. Verify that the paths inside
`data.yaml` are valid, then run:

```bash
python detection/train.py
python detection/infer_webcam.py
python detection/infer_ros.py
```

## Pose example

```bash
python pose/pose_gesture_webcam.py
```

Ultralytics downloads the standard pretrained models when they are not
already cached locally.

## Legacy material

The original scripts, datasets and experiment outputs remain unchanged under
`Documentation/Files/YOLO_model_generation/` during migration.
