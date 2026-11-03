# Complete Automatic Installation: ROS 2 Humble, USB Hardware, and Local Services

Use this guide after writing Ubuntu 22.04 Server to the SD card and completing [Ubuntu Server and Wi-Fi setup](1_Install_Ubuntu22server_wifi.md).

This procedure installs ROS 2 Humble, required robot packages including the V4L2 camera driver, workspace dependencies, stable USB device names, and these local services:

- `my_robot.service`
- `my_rosbridge.service`
- `my_robot_web.service`

This guide assumes the standard rUBot hardware:

- Arduino Nano mecanum driver
- RPLidar with CP210x USB serial adapter
- USB camera with vendor ID `046d` and product ID `0825`

If your hardware differs, use [Robust hardware bringup](3_Install_rubot_robust_bringup_hw.md) to identify its IDs and adapt `99-rubot-hardware.rules` before running the USB installation script.

## 1. Clone the repository

Connect to the Raspberry Pi as `ubuntu` and clone the repository in the expected location:

```bash
cd /home/ubuntu
git clone https://github.com/manelpuig/my_rUBot_mecanum.git
cd /home/ubuntu/my_rUBot_mecanum/tools/robot_installation/Local_service
```

## 2. Install ROS 2 Humble and dependencies

This script installs ROS 2 Humble, `ros-humble-v4l2-camera`, rosbridge, development dependencies, resolves ROS dependencies, and builds the workspace. It can take some time on a Raspberry Pi.

```bash
chmod +x install_ros2_humble_rubot.sh
./install_ros2_humble_rubot.sh
```

## 3. Configure the robot ROS domain

Edit `robot.env`. For each new robot, change only `ROS_DOMAIN_ID` to the assigned group or robot number.

```bash
nano robot.env
```

For example:

```ini
ROS_DOMAIN_ID=6
```

All services and startup scripts read this same file. Do not edit the ROS domain in individual service files.

## 4. Connect the robot USB hardware

Connect the Arduino, lidar, and USB camera before installing the udev rules.

If you are using non-standard hardware, stop here and follow [Robust hardware bringup](3_Install_rubot_robust_bringup_hw.md) to update `99-rubot-hardware.rules` with the correct IDs.

## 5. Install and verify the USB udev rules

```bash
chmod +x install_robot_udev_rules.sh
sudo ./install_robot_udev_rules.sh
```

The script installs `99-rubot-hardware.rules`, reloads udev, and verifies these stable names:

```text
/dev/robot_arduino
/dev/robot_lidar
/dev/robot_camera
```

The script stops with an error if a required stable device name is missing. Check cable connections and the hardware IDs before continuing.

## 6. Install and start the local services

```bash
chmod +x install_local_services.sh
sudo ./install_local_services.sh
```

The installer checks that the workspace has been built, installs the three unit files in `/etc/systemd/system`, reloads systemd, and enables and starts all services.

It is safe to run it again after pulling service-related changes from the repository.

## 7. Verify the installation

```bash
systemctl status my_robot my_rosbridge my_robot_web
```

To follow logs:

```bash
sudo journalctl -u my_robot -f
sudo journalctl -u my_rosbridge -f
sudo journalctl -u my_robot_web -f
```

The dashboard is available at:

```text
http://ROBOT_IP:8000/
```

## 8. Test after reboot

```bash
sudo reboot
```

After reconnecting, verify that all three services are active and that the stable device names still exist:

```bash
ls -l /dev/robot_arduino /dev/robot_lidar /dev/robot_camera
```
