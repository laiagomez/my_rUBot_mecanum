# Computer Vision Tasks with YOLO

In robot perception, four common vision tasks are typically
used:

-   Image Classification
-   Object Detection
-   Image Segmentation
-   Pose Estimation

These tasks progressively increase spatial understanding of the scene.

## Image Classification

Image classification assigns **one label per image**.

Example:

Input image → `STOP sign`

Used when only the object type matters, not its position.

Typical robotics use: - traffic sign recognition - object category
filtering - simple scene understanding

In our traffic‑sign project we use **classification**, because each
frame contains a single relevant sign.


## Object Detection

Object detection identifies:

-   object class
-   object position
-   bounding box coordinates

Example:

`STOP sign → (x, y, w, h)`

Useful when multiple objects appear simultaneously.

Typical robotics use:

-   obstacle detection
-   people detection
-   multi‑sign navigation


Detection could be added later to our project using datasets annotated
with tools such as **Roboflow**.


## Image Segmentation

Segmentation assigns a **class label to each pixel** in the image.

Instead of bounding boxes, it produces masks.

Typical robotics use:

-   road detection
-   hand contour extraction
-   grasp planning
-   environment mapping


Segmentation provides higher spatial precision but requires more
computation.

## Pose Estimation

Pose estimation detects **keypoints of articulated bodies**, typically
humans.

Example:

-   shoulders
-   elbows
-   wrists
-   knees

Typical robotics use:

-   gesture recognition
-   human‑robot interaction
-   hand tracking
-   collaborative robotics


Pose estimation is useful for interaction tasks such as detecting a
handshake or a raised hand.

![](./Images/07_Yolo/01_Yolo.png)

Image from: https://www.dfrobot.com/blog-13844.html


## YOLO

YOLO (You Only Look Once) is a family of real-time object detection models based on deep learning.

We use YOLO because:

-   it runs in real time
-   it works well on CPU systems
-   it supports classification, detection, segmentation and pose
    estimation
-   it integrates easily with ROS 2 pipelines

Alternative frameworks exist:

-   Detectron2
-   Faster R‑CNN
-   EfficientDet
-   RT‑DETR

However, YOLO provides the best balance between speed, simplicity, and
accuracy for robotics education.

| Year | Version | Main improvement                                    |
| ---- | ------- | --------------------------------------------------- |
| 2015 | YOLOv1  | First real-time object detection model              |
| 2016 | YOLOv2  | Improved accuracy and localization                  |
| 2018 | YOLOv3  | Multi-scale object detection                        |
| 2020 | YOLOv4  | Better training techniques and performance          |
| 2020 | YOLOv5  | PyTorch implementation (easy to train and use)      |
| 2022 | YOLOv6  | Optimized for industrial applications               |
| 2023 | YOLOv8  | Anchor-free detection and multi-task support        |
| 2024 | YOLO11  | Higher efficiency and better small-object detection |
| 2025 | YOLO26  | Unified detection pipeline without NMS              |


## Ultralytics

Ultralytics is a Python library for training and running YOLO-based computer vision models.

We use **Ultralytics Python library** because it:

-   simplifies training workflows
-   supports custom datasets
-   exports `.pt` models easily
-   runs efficiently on embedded platforms
-   integrates well with real‑time camera pipelines

## Current Strategy in the Traffic Sign Project

Current approach:

Traffic signs → **classification model**

Advantages:

-   simple dataset structure
-   fast training
-   efficient inference on mobile robots

Future extension:

Traffic signs → **object detection model**

This can be implemented by labeling bounding boxes using **Roboflow**
and retraining YOLO in detection mode.

This upgrade allows the robot to detect multiple signs simultaneously
inside the same image.

## References

- [YOLO](https://www.dfrobot.com/blog-13844.html)
- [Ultralytics](https://github.com/ultralytics/ultralytics)
- [Training model](https://docs.ultralytics.com/es/usage/python/#how-do-i-train-a-custom-yolo-model-using-my-dataset)
- [Roboflow](https://roboflow.com/)

## Objectives

The traffic signs that we want to identify are:
- Stop
- Turn Right
- Turn Left
- Give Way
- No Entry 

![](./Images/07_Yolo/TrafficSigns.png)

## Installation
```bash
py -3.11 -m pip install ultralytics
py -3.11 -m pip uninstall numpy
py -3.11 -m pip install "numpy<2.0"
py -3.11 -m pip install pillow
py -3.11 -m pip install opencv-python
```
> Change the Python version to match the version installed on your computer.

## 1. YOLO Model Generation for a Classification Task

For traffic sign classification, we will use the pretrained YOLO11 model.
- Create the following initial folder structure:

```text
photos/
├── Stop/
├── Right/
├── Left/
├── Give/
├── Nothing/
└── Forbidden/
```
- Capture around 200 images of each traffic sign using different positions, lighting conditions, backgrounds, and viewing angles.
    - If you want to use your computer webcam: 
        - Open a terminal in the `/photos/Stop` folder, for example.
        - Run `1_capture_images.py`.
    - If you want to use the rUBot camera: 
        - Use the ROS 2 node `1_capture_images_from_topic.py` to read images from the `/image_raw` topic and save them in the specified folder.
        - In a new terminal, run:

        ```bash
        py -3.11 1_capture_images_from_topic.py
        ```
        - Verify the topic name and change `OUTPUT_RELATIVE_PATH` for each traffic sign.
- Use `2_prepare_dataset.py` to resize the images to 640 × 640 pixels and create the following dataset structure:
```text
traffic_sign_dataset/
├── train/
│   ├── Stop/
│   ├── Right/
│   ├── Left/
│   ├── Give/
│   ├── Nothing/
│   └── Forbidden/
└── val/
    ├── Stop/
    ├── Right/
    ├── Left/
    ├── Give/
    ├── Nothing/
    └── Forbidden/
```
> `TRAIN_RATIO = 0.80`: 80% of the images are used for training and 20% for validation.
- Train the classification model with `3_generate_model.py`.
- The model will be generated at `runs/classify/train/weights/best.pt`.
- **To test the model prediction** with the classification model `best.pt`:
    - Using your computer webcam:
        - Verify `MODEL_PATH` in `4_classify_camera.py`, and then run the script.
    - If you want to use the rUBot camera: 
        - Use the ROS 2 node `4_classify_camera_from_topic.py` to read images from the `/image_raw` topic and classify them in real time using the previously generated model.
        - In a new terminal, run:

        ```bash
        py -3.11 4_classify_camera_from_topic.py
        ```
        - Verify the topic name and `MODEL_PATH`.

## 2. YOLO Model Generation for an Identification Task

To label the traffic signs in the images and train a model, we will use Roboflow:

- Open [Roboflow](https://roboflow.com/) in a new browser tab.
    ![](./Images/07_Yolo/01_roboflow.png)
- Select **Get Started** or **Sign In**, and then **Continue with Google**.
- Enter a workspace name, for example `TrafficSignals`.
- Select the **Public Plan**.
- You can invite up to four project partners to collaborate on model generation. The suggested role for team members is **Admin**.
- Create the workspace.
- Answer the introductory questions.
- For **What type of model would you like to deploy?**, select **Object Detection**.
    ![](./Images/07_Yolo/02_Object_detection1.jpg)
- See the [Roboflow introductory tutorial](https://blog.roboflow.com/getting-started-with-roboflow/).

- Create a project in the workspace:
    - Select **Projects**, choose **New Project**, enter a name, and click **Continue with Public**.
        ![](./Images/07_Yolo/02_Object_detection1.jpg)
    - Select **Use Traditional Model Builder Instead** to retain full control of the YOLO model for robotics projects.
    - Create five classes: `Stop`, `Right`, `Left`, `Give`, and `Forbidden`.
    - Keep one local folder per class containing the images captured previously.
    - Choose **Select Folder** to upload images from a local folder. Upload all the project images.
        ![](./Images/07_Yolo/04_Project2.png)
    - Select **Save & Continue**, followed by **Start Labeling**.
    - You can assign images to different invited team members.
    - Select **Start Annotating** and repeat the process for each class.
        ![](./Images/07_Yolo/05_Label.png)
    - If you make an error, open the three-dot menu in **Layers** and change the class.
        ![](./Images/07_Yolo/06_Label_error.png)
    - When finished, go back using the arrow in the upper-left corner and select **Add Images to Dataset**.
    - Select **Use Existing Values**, and then **Add Images**.
    - Select **Train Model** and **Custom Training**.
    - Edit **Train/Valid/Test Split**, select **Balance**, and assign 80% to training, 15% to validation, and 5% to testing.
        ![](./Images/07_Yolo/07_train_balance.png)
    - Select **Continue** for the remaining options.
    - Under **Augmentation**, select **Shear** to account for variations along the x- and y-axes.
        ![](./Images/07_Yolo/08_shear.png)
    - Select **Create**.
    - Select **Download Dataset**, choose the **YOLOv8** format, and select **Download ZIP to Computer**. The ZIP file contains the training, validation, and test images together with the `data.yaml` file used to obtain the final model.

 <img src="./Images/07_Yolo/09_DataSet.png" width="400"/>  <img src="./Images/07_Yolo/09_DataSet2.png" width="200"/> 

- **To test the model prediction** with the identification model `yolov8n_identification_signals.pt`:
    - Using your computer webcam:
        - Verify `MODEL_PATH` in `5_identify_camera.py`, and then run the script.
    - If you want to use the rUBot camera: 
        - Verify the topic and `MODEL_PATH` in `5_identify_camera_from_topic.py`.
        - In a new terminal, run:

        ```bash
        py -3.11 5_identify_camera_from_topic.py
        ```


## 3. Pose Estimation

Pose estimation detects **keypoints of articulated bodies**, typically
humans.

1. Open a terminal in `YOLO_model_generation`.
2. Run the Python program:

```bash
py -3.11 6_pose_gesture_camera.py
```

![](./Images/07_Yolo/01_Yolo_Pose_Detection.png)
![](./Images/07_Yolo/01_Yolo_Pose_Detection2.png)
