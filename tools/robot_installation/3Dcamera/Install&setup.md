# Install Intel RealSense D435/i

This camera could be installed on:
- PC Ubuntu 22 with ROS2 Humble
- Raspberrypi4 Ubuntu 22 with ROS2 Humble

The installation process in **PC Ubuntu 22**:

```bash
sudo apt install -y git cmake build-essential \
  libssl-dev libusb-1.0-0-dev libudev-dev pkg-config \
  libgtk-3-dev libglfw3-dev libgl1-mesa-dev libglu1-mesa-dev 

mkdir -p ~/software && cd ~/software
git clone https://github.com/IntelRealSense/librealsense.git
cd librealsense
sudo ./scripts/setup_udev_rules.sh
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DFORCE_RSUSB_BACKEND=true -DBUILD_EXAMPLES=true
make -j$(nproc)
sudo make install
````
Increase the `usbfs_memory` to 512:
```bash
echo 'options usbcore usbfs_memory_mb=512' | sudo tee /etc/modprobe.d/usbfs_memory.conf
sudo reboot
```
To test if the installation was successful, connect the camera and run:
```bash
realsense-viewer
```

To install the wrapper ROS2:
```bash
sudo apt install ros-humble-realsense2-camera ros-humble-realsense2-description
````
The launch file with default parameters:
```bash
ros2 launch realsense2_camera rs_launch.py \
  rgb_camera.color_profile:=640x480x15 \
  depth_module.depth_profile:=640x360x15 \
  pointcloud.enable:=false
```
When camera is on **raspberrypi** (not recommended!), the installation instructions are equivalent, but you have to:
- add a patch to it kernel (after step `cd librealsense`):
  ````bash
  cd ~/software/librealsense
  sudo ./scripts/setup_udev_rules.sh
  sudo ./scripts/patch-realsense-ubuntu-lts-hwe.sh
  ````
- Increase the `usbfs_memory` to 512:
  - open the file:
    ```bash
    sudo nano /boot/firmware/cmdline.txt
    ````
  - add at the end of line:
    ````bash
    usbcore.usbfs_memory_mb=512
    ````
  - reboot the raspberrypi
- change to a more stable firmware version for D435/i: version
`5.12.15.50`. This can be done in the "Device" tab -> "Update Firmware".

- Use the launch file with custom parameters:
  ```bash
  ros2 launch realsense2_camera rs_launch.py \
    initial_reset:=true \
    enable_color:=true \
    enable_depth:=true \
    align_depth:=true \
    enable_sync:=false \
    pointcloud.enable:=false \
    depth_module.depth_profile:=640x360x15 \
    rgb_camera.color_profile:=640x480x30 \
    enable_infra1:=false enable_infra2:=false
  ```

## PC Ubuntu 24 with Docker

We have created a Docker image: 
- manelpuig/ros2-humble-ub-ur5e:realsense
- Documented on `https://github.com/manelpuig/UR5e_social_robotics`

Important to add on `.bashrc` an environment variable:
- export LD_PRELOAD=/usr/local/lib/librealsense2.so

# Install Orbbec DaBai

This camera could be installed on:
- PC Ubuntu 22 with ROS2 Humble
- Raspberrypi4 Ubuntu 22 with ROS2 Humble

The installation process is very simple in both cases.

## PC Ubuntu 22 with ROS2 Humble

Install dependencies:
```bash
sudo apt install libgflags-dev nlohmann-json3-dev libgoogle-glog-dev \
     ros-humble-image-transport ros-humble-camera-info-manager \
     ros-humble-image-publisher libusb-1.0-0-dev libeigen3-dev
```
Clone the ROS2 package in your workspace (the correct branch is main):
```bash
cd ~/ROS2_rUBot_mecanum_ws/src
git clone --branch main https://github.com/orbbec/OrbbecSDK_ROS2.git
cd ..
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```
Define the UDEV rules:
```bash
cd src/OrbbecSDK_ROS2/orbbec_camera/scripts
sudo bash install_udev_rules.sh
sudo udevadm control --reload-rules && sudo udevadm trigger
```
Launch:
```bash
ros2 launch orbbec_camera dabai.launch.py
```
Or with custom parameters:
```bash
ros2 launch orbbec_camera dabai.launch.py \
  color_width:=640  color_height:=480  color_fps:=15 \
  depth_width:=640  depth_height:=480  depth_fps:=15 \
  enable_point_cloud:=false
```

Best cameras:
- https://www.orbbec.com/products/tof-camera/femto-bolt/
- https://www.orbbec.com/products/tof-camera/femto-mega/

## Raspberrypi4 Ubuntu 22 with ROS2 Humble

Optionally download the SDK driver for ARM64 from Orbbec site: 
- https://github.com/orbbec/OrbbecSDK/releases

- Copy the contents of SDK driver on home custom folder:
```bash
mkdir -p ~/orbbec_sdk
cp -r OrbbecViewer_v1.10.27_202509260950_arm64_release/* ~/orbbec_sdk/
````
- Execute the viewer to test the camera:
```bash
cd ~/orbbec_sdk
./OrbbecViewer
````
- Create udev rules (to run without sudo):
```bash
cd ~/orbbec_sdk/script
chmod +x install_udev_rules.sh
sudo ./install_udev_rules.sh
```

Install some needed packages:
```shell
apt update
apt install -y \
  ros-humble-image-transport \
  ros-humble-image-transport-plugins \
  ros-humble-compressed-image-transport

```
Install from source the ROS2 wrapper: https://github.com/orbbec/OrbbecSDK_ROS2.git
- Install ROS2 wrapper as in PC Ubuntu 22 section and launch with:
```bash
cd src
git clone --branch main https://github.com/orbbec/OrbbecSDK_ROS2.git
cd ..
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```
- Launch with:
```bash
ros2 launch orbbec_camera dabai.launch.py
ros2 launch orbbec_camera gemini2.launch.py
ros2 launch orbbec_camera astra2.launch.py
```
## Jetson Nano from LIMO robot
The installation process is the same as in Raspberrypi.
We have created a Dockerfile with the previous installation on Raspberrypi. 

Partim del `limo_ros2` official repository (https://github.com/agilexrobotics/limo_ros2.git
)
Cal copiar, al Host de Jetson Nano, Dockerfile i el fitxer de drivers comprimit (zip) a un directori `limo_ws` i obrir VSCode:
- Crear imatge i pujar-la directament a Docker hub:
````shell
cd ~/limo_ws   # o el directori on tens el Dockerfile
sudo docker build -t manelpuig/ros2-humble-limo-ub:jetson .
docker login
sudo docker push manelpuig/ros2-humble-limo-ub:jetson
````


Open VScode window on `Docker_limo_orbbec`:
````shell
docker compose up -d
````

For udev rules we have to do it on Host:
````shell
cd ~/orbbec_sdk/script
chmod +x install_udev_rules.sh
sudo ./install_udev_rules.sh
sudo udevadm control --reload-rules
sudo udevadm trigger
````
For GUI using X11:
````shell
xhost +local:root
````

## Program test
To test if the camera is working properly, you can:
- Start the camera:
  ```bash
  ros2 launch orbbec_camera dabai.launch.py \
  enable_ir:=false \
  depth_width:=640 depth_height:=400 depth_fps:=15 \
  color_width:=640 color_height:=480 color_fps:=15
  ```
- review the topics:
  ```bash
  ros2 topic list
  ```
- review the info of image topics:
  ```bash
  ros2 topic info /camera/color/image_raw/compressed
  ros2 topic info /camera/depth/image_raw/compressedDepth
  ```
- review the hz and bw of image topics:
  ```bash
  ros2 topic hz /camera/color/image_raw/compressed
  ros2 topic bw /camera/color/image_raw/compressed
  ros2 topic hz /camera/depth/image_raw/compressedDepth
  ros2 topic bw /camera/depth/image_raw/compressedDepth
  ```
- Create a simple Python node that subscribes to the topics:
    - /camera/color/image_raw/compressed
    - /camera/depth/image_raw/compressedDepth
- Execute this node:
  ```bash
  chmod +x compressed_image_subscriber.py
  python3 compressed_image_subscriber.py
  ```
- Use `rqt_image_view` to visualize the topics:
  ```bash
  ros2 run rqt_image_view rqt_image_view
  ``` 
  - Select topic: `/camera/color/image_raw` → Transport: `compressed`

  - Select topic: `/camera/depth/image_raw` → Transport: `compressedDepth`
- Verify the clocks are sync:
  ```bash
  timedatectl
  ```
- Activate the NTP, chrony if necessary:
  ```bash
  sudo timedatectl set-ntp true
  sudo systemctl restart chrony
  chronyc tracking
  ```

# Install 3D camera Orbbec Gemini2

## If you have a PC-Ubuntu22

You have to install:
````bash
sudo apt update

sudo apt install -y \
  ros-humble-orbbec-camera \
  ros-humble-orbbec-description \
  libgflags-dev \
  nlohmann-json3-dev \
  libgoogle-glog-dev \
  libusb-1.0-0-dev \
  ros-humble-image-transport \
  ros-humble-image-transport-plugins \
  ros-humble-compressed-image-transport \
  ros-humble-image-publisher \
  ros-humble-camera-info-manager \
  ros-humble-diagnostic-updater \
  ros-humble-diagnostic-msgs \
  ros-humble-statistics-msgs \
  ros-humble-xacro \
  ros-humble-backward-ros \
  libdw-dev \
  libssl-dev \
  mesa-utils \
  libgl1
````
You have to install also Udev rules to the host:
````bash
sudo cp /opt/ros/humble/share/orbbec_camera/udev/99-obsensor-libusb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
````
Then you can use it with:
````bash
source /opt/ros/humble/setup.bash
ros2 run orbbec_camera list_devices_node
ros2 launch orbbec_camera gemini2.launch.py
````

**Possible trouble**:
- uvcvideo problem:
````bash
echo "blacklist uvcvideo" | sudo tee /etc/modprobe.d/blacklist-uvcvideo.conf
sudo update-initramfs -u
sudo reboot
````

## If you have a PC-Ubuntu24

You have tu use the Docker custom image `manelpuig/ros2-humble-ub-ur5e:latest`

Follow the steps:
- On host connect the Orbbec camera and verify
  ````bash
  lsusb
  ````
  > You have to see Orbbec Gemini
- Install Udev rules:
  ````bash
  sudo nano /etc/udev/rules.d/99-obsensor-libusb.rules
  ````
- Add this line
  ````bash
  SUBSYSTEM=="usb", ATTR{idVendor}=="2bc5", MODE:="0666"
  ````
- save and apply the rules:
  ````bash
  sudo udevadm control --reload-rules
  sudo udevadm trigger
  ````
- Unplug and plug again
- Close and open the container
- Verify:
  ````bash
  lsusb
  ros2 run orbbec_camera list_devices_node
  ````
- The correct answer has to be:
  ````bash
  Name: Orbbec Gemini2
  Connection: USB3.0
  ````
- Launch the correct configuration:
  ````bash
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
  ````
- Verify
  ````bash
  ros2 topic list
  ros2 topic hz /camera/color/image_raw
  ````
## On Raspberrypi4



  # 3D camera on Gazebo simulation

  The 3D camera plugin do not offers the compressed topics and messages. 

  We have to create the compressed images with "image-transport" package.

  This has to be included in the software launch file "yolo_prediction_sw.launch.py"

  This reproduce the same behaviour as the hardware node where the properly installed driver already creates the compressed topics and compressed messages.

  ```shell
  ros2 launch my_robot_ai_identification yolo_prediction_sw.launch.py
  ```