# Orbbec Gemini2 Installation Guide (Raspberry Pi 4, Ubuntu Server 22.04, ROS2 Humble)

This guide explains how to install and run the **Orbbec Gemini2 RGB‑D
camera** on a Raspberry Pi 4 using **Ubuntu Server 22.04 + ROS2
Humble**, and how to enable **compressed image transport** for efficient
network streaming.

------------------------------------------------------------------------

# 1. System Requirements

Recommended:

-   Raspberry Pi 4 (4GB or 8GB RAM)
-   Ubuntu Server 22.04 (64-bit)
-   ROS2 Humble installed
-   USB 3.0 connection (blue port)
-   Stable power supply (≥ 3A)

------------------------------------------------------------------------

# 2. Update the System

``` bash
sudo apt update
sudo apt upgrade -y
```

------------------------------------------------------------------------

# 3. Install Dependencies

``` bash
sudo apt update
sudo apt install -y \
  git build-essential cmake pkg-config \
  python3-colcon-common-extensions python3-rosdep \
  libgflags-dev libgoogle-glog-dev nlohmann-json3-dev \
  libdw-dev libssl-dev libgl1 mesa-utils \
  ros-humble-image-transport \
  ros-humble-image-transport-plugins \
  ros-humble-compressed-image-transport \
  ros-humble-camera-info-manager \
  ros-humble-image-publisher \
  ros-humble-diagnostic-updater \
  ros-humble-diagnostic-msgs \
  ros-humble-statistics-msgs \
  ros-humble-xacro \
  ros-humble-backward-ros
````
------------------------------------------------------------------------

# 4. Initialize rosdep

``` bash
sudo rosdep init
rosdep update
```

------------------------------------------------------------------------

# 5. Create Workspace

``` bash
mkdir -p ~/orbbec_ws/src
cd ~/orbbec_ws/src
```

------------------------------------------------------------------------

# 6. Clone Orbbec ROS2 Driver

``` bash
git clone https://github.com/orbbec/OrbbecSDK_ROS2.git
cd OrbbecSDK_ROS2
git checkout v2-main
cd ..
```

------------------------------------------------------------------------

# 7. Install Remaining Dependencies

``` bash
cd ~/orbbec_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
```

------------------------------------------------------------------------

# 8. Build the Workspace

``` bash
cd ~/orbbec_ws
colcon build --event-handlers console_direct+ --cmake-args -DCMAKE_BUILD_TYPE=Release
```

------------------------------------------------------------------------

# 9. Source the Workspace

``` bash
source ~/orbbec_ws/install/setup.bash
```

Add permanently:

``` bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "source ~/orbbec_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

------------------------------------------------------------------------

# 10. Install udev Rules

``` bash
cd ~/orbbec_ws/src/OrbbecSDK_ROS2/orbbec_camera/scripts
sudo bash install_udev_rules.sh
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Reconnect the camera afterward.

------------------------------------------------------------------------

# 11. Verify Camera Detection

``` bash
lsusb
```

Then:

``` bash
ros2 run orbbec_camera list_devices_node
```

Expected:

    Name: Orbbec Gemini2
    Connection: USB3.0

------------------------------------------------------------------------

# 12. Launch the Camera

Recommended lightweight configuration for Raspberry Pi 4:

``` bash
ros2 launch orbbec_camera gemini2.launch.py \
  color_width:=640 \
  color_height:=480 \
  color_fps:=15 \
  color_format:=MJPG \
  depth_width:=640 \
  depth_height:=400 \
  depth_fps:=15 \
  depth_registration:=false \
  enable_ir:=false \
  enable_point_cloud:=false \
  enable_accel:=false \
  enable_gyro:=false \
  connection_delay:=3000
```

Recommended configuration for a Orbbec_Gemini2L on Raspberrypi4 is:
````bash
ros2 launch orbbec_camera gemini2L.launch.py \
  color_width:=640 \
  color_height:=400 \
  color_fps:=15 \
  color_format:=MJPG \
  depth_width:=640 \
  depth_height:=400 \
  depth_fps:=15 \
  depth_format:=Y14 \
  depth_registration:=false \
  enable_ir:=false \
  enable_point_cloud:=false \
  enable_accel:=false \
  enable_gyro:=false \
  connection_delay:=3000
````

# 13. Verify Topics

``` bash
ros2 topic list
```

Expected:

    /camera/color/image_raw
    /camera/color/image_raw/compressed
    /camera/depth/image_raw

Check frame rate:

``` bash
ros2 topic hz /camera/color/image_raw
```
View compressed stream:

``` bash
ros2 run rqt_image_view rqt_image_view
```

Select:

    /camera/color/image_raw/compressed

