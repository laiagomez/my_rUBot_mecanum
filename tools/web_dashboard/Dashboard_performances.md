# rUBot Web Dashboard

## Main features

The dashboard lets you control and monitor one rUBot from a web browser.

- Connects to ROS 2 through Rosbridge.
- Shows the robot camera.
- Controls forward and backward speed (`Vx`) up to `+/- 0.2 m/s`.
- Controls lateral speed (`Vy`) up to `+/- 0.2 m/s`.
- Controls angular speed from `-45 deg/s` to `+45 deg/s`.
- Returns the angular slider to zero when it is released.
- Shows the robot position, orientation, and velocity direction.
- Shows the current LiDAR scan in yellow.
- Can build a simple local occupancy map from repeated LiDAR scans.
- Starts with mapping disabled to reduce browser processing.
- Provides a **Mapping: OFF/ON** button that can be used at any time.
- Shows confirmed walls and obstacles in black.
- Removes old black obstacles when later LiDAR rays see free space there.
- Provides a **Reset map** button to clear and recenter the learned occupancy map.

## Map scale

The map uses fixed world limits. Resizing the browser does not change its physical scale.

- X range: `-1.5 m` to `+1.5 m`.
- Y range: `-1.5 m` to `+1.5 m`.
- Each axis has 10 equal intervals.
- Every interval represents `0.30 m` in the real world.
- Red vertical axis: X.
- Green horizontal axis: Y.
- Map resolution: `0.01 m` per occupancy cell.

The map is local to the dashboard and starts at the robot position when the page connects. It depends on wheel odometry. Long runs or wheel slip can make walls look thicker or displaced. For precise mapping, use a ROS 2 SLAM package such as `slam_toolbox`.

## Open the dashboard on a mobile phone

1. Connect the phone and the rUBot to the same Wi-Fi network.
2. Find the robot IP address.
3. Open Chrome, Safari, Firefox, or another modern browser on the phone.
4. Enter this address:

   ```text
   http://ROBOT_IP:8000/
   ```

   Example:

   ```text
   http://192.168.1.14:8000/
   ```

5. Select the robot number and press **Connect**.

Landscape mode gives more space for the camera, joystick, and map. If an old dashboard version appears, refresh the page or clear the browser cache.

## Required robot services

The robot must run:

- the robot bringup;
- Rosbridge WebSocket on port `9090`;
- the web server on port `8000`.

The web server serves this file by default:

```text
/home/ubuntu/my_rUBot_mecanum/tools/web_dashboard/index.html
```

## Previous dashboard (`index0.html`)

`index0.html` is a backup of the dashboard that was used before the changes described in this document. It can be used to return to the previous behaviour.

The previous dashboard:

- shows the camera, joystick, robot position, orientation, and current LiDAR scan;
- shows only the current LiDAR points and does not build a persistent occupancy map;
- has no **Reset map** button;
- shows angular speed in `rad/s`;
- does not return the angular slider to zero when it is released;
- uses one linear speed limit of `0.3 m/s` for both `Vx` and `Vy`.

### Test `index0.html` without changing the default dashboard

If `index0.html` is present in `tools/web_dashboard` on the robot, open:

```text
http://ROBOT_IP:8000/index0.html
```

This opens the previous dashboard only for that browser. The default address still opens `index.html`.

### Start the robot with `index0.html` as the default dashboard

The Python web server automatically opens the file named `index.html`. It does not select `index0.html` by itself. To make the previous dashboard the default, connect to the robot and run:

```bash
cd /home/ubuntu/my_rUBot_mecanum/tools/web_dashboard
cp index.html index_dashboard_current.html
cp index0.html index.html
```

The first command saves a copy of the current dashboard. The second command makes the old dashboard the default.

It is not necessary to restart `my_robot_web.service`. Refresh the browser, preferably with a full refresh, and open:

```text
http://ROBOT_IP:8000/
```

To restore the current dashboard later, run:

```bash
cd /home/ubuntu/my_rUBot_mecanum/tools/web_dashboard
cp index_dashboard_current.html index.html
```

Then refresh the browser again.

The dashboard uses these ROS topics:

- `/cmd_vel`
- `/odom`
- `/scan`
- `/image_raw/compressed`

## Map behaviour

Mapping is disabled by default. The current LiDAR scan remains visible in yellow while mapping is off, but the occupancy grid is not updated. Any black map points already created stay visible and frozen.

Press **Mapping: OFF** to enable mapping. The button changes to green and displays **Mapping: ON**. On the first activation, the current robot position becomes the centre of the `3 x 3 m` map. Mapping can be disabled and enabled again without losing the accumulated map.

One LiDAR hit is not immediately accepted as a wall. Repeated hits increase the confidence of a map cell. When the confidence passes a threshold, the cell becomes black.

LiDAR rays also mark visible space as free. If an old obstacle disappears, later free-space observations reduce its confidence until the black point disappears. This avoids keeping temporary obstacles forever.

The occupancy map is stored only in browser memory. It is cleared when the page is reloaded or when **Reset map** is pressed. **Reset map** also moves the map centre to the robot's current position, whether mapping is on or off.
