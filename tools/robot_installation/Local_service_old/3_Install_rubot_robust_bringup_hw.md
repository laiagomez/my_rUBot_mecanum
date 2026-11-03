# Install stable USB device names for the robot and use a robust hardware bring-up launch

This guide explains how to create stable device names for the robot hardware on the Raspberry Pi, so the Arduino Nano driver, the lidar, and the camera do not depend on changing USB names like `/dev/ttyUSB0` or `/dev/video0`.

The idea is simple:

- create stable symlinks via `udev`
- use those symlinks in the launch file
- wait until the devices are present and can be opened before starting the ROS nodes
- start the nodes in order with a small delay

This is more robust than launching everything at once and relying on `respawn` to recover later.

## 1) Why this is useful

USB device names can change between reboots or when devices are connected in a different order.

For example, this may happen:

- `/dev/ttyUSB0` becomes `/dev/ttyUSB1`
- `/dev/video0` becomes `/dev/video2`

That breaks a launch file that expects a fixed port path.

With `udev` rules, you can define permanent names such as:

- `/dev/robot_arduino`
- `/dev/robot_lidar`
- `/dev/robot_camera`

Then your launch file can use those stable paths always.

## 2) Find the device IDs

First, connect the hardware to the Raspberry Pi and check which USB devices are present.

### List USB devices

```bash
lsusb
```

You should see entries similar to:

```bash
Bus 001 Device 005: ID 2341:0070 Arduino SA Uno R3 (CDC ACM)
Bus 001 Device 006: ID 10c4:ea60 Silicon Labs CP210x UART Bridge
Bus 001 Device 007: ID 046d:0825 Microdia USB Camera
```

The important values are:

- `idVendor`
- `idProduct`

These values are used in the `udev` rule.

### Check the exact device node

For serial devices:

```bash
ls -l /dev/ttyUSB* /dev/ttyACM*
```

For camera devices:

```bash
ls -l /dev/video* 
```

If you want the exact device properties, you can read them with:

```bash
udevadm info -q property -n /dev/ttyUSB0
```

or:

```bash
udevadm info -q property -n /dev/video0
```

This helps you confirm the correct device before creating the rule.

## 3) Create the udev rule

Create a file in `/etc/udev/rules.d/`.

Example:

```bash
sudo nano /etc/udev/rules.d/99-rubot-hardware.rules
```

Then add rules like this:

```bash
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0070", SYMLINK+="robot_arduino"
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="robot_lidar"
SUBSYSTEM=="video4linux", ATTR{index}=="0", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="0825", SYMLINK+="robot_camera"
```

These rules map each device to a stable name.

After saving the file, reload the rules:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Then check the symlinks:

```bash
ls -l /dev/robot_arduino /dev/robot_lidar /dev/robot_camera
```

If everything is correct, the device paths should exist and remain stable across reboots.

## 4) Check if the ports are ready

For the Arduino and lidar, the most useful check is:

- device file exists
- the serial port can be opened successfully

A simple Python test is enough:

```bash
python3 - <<'PY'
import serial
ports = ['/dev/robot_arduino', '/dev/robot_lidar']
for port in ports:
    try:
        s = serial.Serial(port, timeout=0.5)
        print(port, 'OK')
        s.close()
    except Exception as e:
        print(port, 'NOT READY:', e)
PY
```

For the camera, it is usually enough to verify that the device exists:

```bash
ls -l /dev/robot_camera
```

If it exists, the v4l2 driver usually sees it correctly.

## 5) Use the stable names in the launch file

The launch file should not use `/dev/ttyUSB0` or `/dev/video0` directly.

Use:

- `/dev/robot_arduino`
- `/dev/robot_lidar`
- `/dev/robot_camera`

This is much more robust and is the recommended approach for real hardware.

## 6) Robust launch sequence

Instead of starting all nodes at the same time, wait for the devices to appear and then launch them in order with a small delay.

This helps avoid races like:

- driver starts before the serial port is ready
- lidar starts before the port exists
- camera starts before the device enumeration is finished

The launch file `my_robot_bringup_robust_hw.launch.py` implements this pattern.

It does three things:

1. waits for all hardware device files to be ready
2. starts the driver first
3. waits a bit, then starts the camera, then the lidar

This is a much cleaner startup sequence than using repeated `respawn` as the main solution.

## 7) Notes

- `udev` rules are normally created once on the Raspberry Pi.
- You do not need to recreate them often.
- If you change hardware or move to a different USB adapter, you may need to update the `idVendor` and `idProduct` values.
- `respawn=True` can still be kept as a safety net, but it should not be the main startup strategy.

## 8) Example supported launch defaults

The robust launch file uses defaults like:

- `mecanum_serial_port=/dev/robot_arduino`
- `rplidar_serial_port=/dev/robot_lidar`
- `usb_video_device=/dev/robot_camera`

Those are the values you want to use when the `udev` rules are working correctly.

## 9) Summary

The recommended setup is:

- create stable `udev` names once
- validate device presence and serial openability
- delay node startup in order
- keep `respawn` only as a fallback

This is the easiest and most robust way to bring up the real robot hardware.

## 10) Final optimized launch behavior

The final launch file is [my_rUBot_mecanum/src/my_robot_bringup/launch/my_robot_bringup_robust_hw.launch.py](../../../../src/my_robot_bringup/launch/my_robot_bringup_robust_hw.launch.py).

Its structure is intentionally simple and robust:

1. It defines stable launch arguments for the robot hardware.
2. It starts `robot_state_publisher` first so the robot URDF is available immediately.
3. It runs a small Python helper script before launching the hardware nodes:
   - `/dev/robot_arduino`
   - `/dev/robot_lidar`
   - `/dev/robot_camera`
4. The helper script validates that each device exists and that the serial ports can be opened successfully.
5. Once all devices are ready, the launch starts the hardware in sequence:
   - Arduino driver
   - camera
   - lidar
6. It uses `TimerAction` so the devices are not started simultaneously and do not fight for USB initialization.

The result is a much more stable boot sequence than launching all nodes at once and relying on `respawn` to recover from startup races.

The lidar frame is set to `laser` by default. On launch file the `rplidar_frame_id` is set to `base_scan`, which is the link associated to Lidar on URDF file.
