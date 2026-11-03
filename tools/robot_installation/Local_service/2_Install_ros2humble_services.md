# ROS 2 Humble and Local Services: Manual Installation

Use this guide after completing [Ubuntu Server and Wi-Fi setup](1_Install_Ubuntu22server_wifi.md). It installs ROS 2 Humble, builds the rUBot workspace, and configures the robot bringup, rosbridge, and dashboard services manually.

For the automated alternative, including USB device rules, see [Automatic installation](4_Install_ros2humble_usb_services_automatic.md).

## 1. Clone the repository

```bash
cd /home/ubuntu
git clone https://github.com/manelpuig/my_rUBot_mecanum.git
cd /home/ubuntu/my_rUBot_mecanum/tools/robot_installation/Local_service
```

## 2. Install ROS 2 Humble and build the workspace

The installation script installs ROS 2 Humble, all required packages (including `ros-humble-v4l2-camera`), resolves workspace dependencies, and builds the workspace.

```bash
chmod +x install_ros2_humble_rubot.sh
./install_ros2_humble_rubot.sh
```

When it finishes, open a new terminal or run:

```bash
source /home/ubuntu/.bashrc
ros2 doctor
```

## 3. Configure the robot

All shared ROS and service settings are stored in `robot.env`. For a new robot, normally only `ROS_DOMAIN_ID` must be changed.

```bash
nano robot.env
```

Example:

```ini
ROS_DOMAIN_ID=6
```

Do not set different ROS domain values in the service files or startup scripts. `robot.env` is the single source of configuration for all three services.

## 4. Prepare the startup scripts

```bash
chmod +x start_robot.sh start_rosbridge.sh start_web_dashboard.sh
```

The scripts remain in this repository; do not copy them to `/home/ubuntu`.

## 5. Install the systemd unit files manually

Copy the three unit files to the system systemd directory:

```bash
sudo install -m 0644 my_robot.service /etc/systemd/system/my_robot.service
sudo install -m 0644 my_rosbridge.service /etc/systemd/system/my_rosbridge.service
sudo install -m 0644 my_robot_web.service /etc/systemd/system/my_robot_web.service
```

Reload systemd and enable all services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now my_robot.service my_rosbridge.service my_robot_web.service
```

## 6. Verify the services

```bash
systemctl status my_robot my_rosbridge my_robot_web
```

Follow logs when diagnosing a startup issue:

```bash
sudo journalctl -u my_robot -f
sudo journalctl -u my_rosbridge -f
sudo journalctl -u my_robot_web -f
```

The dashboard is available at:

```text
http://ROBOT_IP:8000/
```

## 7. Test after reboot

```bash
sudo reboot
```

After reconnecting to the robot, check the service status again.

## 8. Update service configuration

To change the ROS domain or a configured port, edit `robot.env`:

```bash
cd /home/ubuntu/my_rUBot_mecanum/tools/robot_installation/Local_service
nano robot.env
sudo systemctl restart my_robot.service my_rosbridge.service my_robot_web.service
```

To apply changed `.service` files, copy them again, reload systemd, and restart the services:

```bash
sudo install -m 0644 my_robot.service /etc/systemd/system/my_robot.service
sudo install -m 0644 my_rosbridge.service /etc/systemd/system/my_rosbridge.service
sudo install -m 0644 my_robot_web.service /etc/systemd/system/my_robot_web.service
sudo systemctl daemon-reload
sudo systemctl restart my_robot.service my_rosbridge.service my_robot_web.service
```

## Hardware note

Before relying on automatic startup, configure stable device names for the Arduino, lidar, and camera as described in [Robust hardware bringup](3_Install_rubot_robust_bringup_hw.md).
