# Chapter 2. Robot Description and Bringup
Hola

## Learning Objectives

After completing this chapter, students should be able to:

* Understand the architecture of a ROS 2 robot model.
* Interpret a URDF/Xacro description.
* Identify links, joints and coordinate frames.
* Understand the kinematics of a mecanum mobile robot.
* Understand the kinematic chain of a robotic arm.
* Understand how sensors are integrated into a robot model.
* Understand the purpose of the main bringup launch files.
* Launch and validate robot simulations in RViz2 and Gazebo Sim.
* Extend an existing robot model using AI-assisted development tools.
* Create and validate a Gazebo Sim world.

---

# 1. Introduction

The project uses two main packages:

```text
my_robot_description
my_robot_bringup
```

The first package contains all robot models.

The second package contains the launch files required to start the different robot configurations in simulation and on real hardware.

Students are not expected to create complete robot descriptions from scratch.

However, they must be able to:

* Understand an existing model.
* Modify an existing model.
* Add new components.
* Verify the resulting system.

---

# 2. Package: my_robot_description

## Purpose

This package contains:

* URDF models
* Xacro macros
* Sensor definitions
* RViz configurations
* Robot meshes
* Gazebo plugins and interfaces

---

# 3. Robot Models

The repository contains several robot configurations.

---

## 3.1 rUBot Mecanum

Main features:

* Four mecanum wheels
* LiDAR sensor
* RGB camera
* Differential odometry
* Navigation-ready platform

### Robot Structure

```text
base_footprint
    |
base_link
    |
    +-- wheel links
    +-- lidar link
    +-- camera link
```

### RViz Model

![rUBot Mecanum RViz](images/rubot_mecanum_rviz.png)

**TODO:** reuse image from previous document.

---

## 3.2 rUBot Arm

Main features:

* 6 revolute joints
* Serial manipulator
* Tool Center Point (TCP)
* MoveIt2 ready

### Kinematic Chain

```text
base_link
    |
joint1
    |
joint2
    |
joint3
    |
joint4
    |
joint5
    |
joint6
    |
tool
```

### RViz Model

![rUBot Arm RViz](images/rubot_arm_rviz.png)

**TODO:** reuse image from previous document.

---

## 3.3 rUBot Mecanum + Arm

Main features:

* Omnidirectional mobile base
* 6-DOF robotic arm
* RGB camera
* LiDAR
* Manipulation and navigation platform

### RViz Model

![rUBot Mecanum Arm RViz](images/rubot_mecanum_arm_rviz.png)

**TODO:** generate new image.

---

# 4. Understanding the Robot Description

Students should be able to identify:

## Links

A link represents a rigid body.

Examples:

```text
base_link
camera_link
lidar_link
arm_link3
```

---

## Joints

A joint defines the relationship between two links.

Examples:

```text
fixed
continuous
revolute
```

Students must understand:

* parent link
* child link
* axis
* origin
* limits

---

## Sensors

Students must identify:

### LiDAR

Publishes:

```bash
/scan
```

---

### RGB Camera

Publishes:

```bash
/camera/image
```

---

### Depth Camera

Publishes:

```bash
/camera/depth_image
```

```bash
/camera/points
```

---

# 5. Coordinate Frames (TF)

The TF tree describes the geometric relationship between all robot elements.

Typical structure:

```text
map
 |
odom
 |
base_footprint
 |
base_link
 |
 +-- lidar_link
 +-- camera_link
 +-- arm_base_link
```

Students must understand:

* global frames
* local frames
* sensor frames
* tool frames

---

# 6. Mecanum Kinematics

The mecanum base can generate:

* forward motion
* backward motion
* lateral motion
* diagonal motion
* pure rotation

Velocity command:

```bash
/cmd_vel
```

Parameters:

```text
vx
vy
wz
```

Students should understand how wheel velocities combine to generate omnidirectional motion.

---

# 7. Arm Kinematics

Students should understand:

* serial manipulator structure
* forward kinematics
* inverse kinematics
* TCP concept

Joint interpretation:

| Joint   | Function      |
| ------- | ------------- |
| Joint 1 | Base rotation |
| Joint 2 | Shoulder      |
| Joint 3 | Elbow         |
| Joint 4 | Wrist pitch   |
| Joint 5 | Wrist roll    |
| Joint 6 | Tool rotation |

---

# 8. Package: my_robot_bringup

## Purpose

This package launches complete robotic systems.

Students are not expected to write launch files from scratch.

However, they must understand:

* which launch to use
* what each launch starts
* how to modify launch parameters

---

# 9. Main Launch Files

---

## display.launch.py

Purpose:

Visualize robot model in RViz2.

Main nodes:

```text
robot_state_publisher
joint_state_publisher_gui
rviz2
```

Verification:

```bash
ros2 topic echo /robot_description --once
```

---

## my_robot_bringup_gz.launch.py

Purpose:

Launch rUBot Mecanum in Gazebo Sim.

Main nodes:

```text
gz_sim
robot_state_publisher
ros_gz_bridge
ekf_node
static_transform_publishers
```

Verification:

```bash
ros2 topic list
```

Expected topics:

```text
/cmd_vel
/odom
/scan
/camera/image
/tf
```

---

## my_robot_arm_bringup_gz.launch.py

Purpose:

Launch rUBot Mecanum + Arm.

Additional nodes:

```text
joint_state_broadcaster
arm_controller
ros2_control
```

Verification:

```bash
ros2 control list_controllers
```

---

## my_robot_bringup_hw.launch.py

Purpose:

Launch real robot hardware.

Students should understand the difference between:

```text
Simulation
vs
Real Robot
```

---

# 10. Validation Procedures

---

## Verify TF Tree

```bash
ros2 run tf2_tools view_frames
```

Expected result:

All robot frames connected.

---

## Verify Joint States

```bash
ros2 topic echo /joint_states --once
```

---

## Verify Odometry

```bash
ros2 topic echo /odom --once
```

---

## Verify LiDAR

```bash
ros2 topic hz /scan
```

---

## Verify RGB Camera

```bash
ros2 topic hz /camera/image
```

---

## Verify Depth Camera

```bash
ros2 topic hz /camera/depth_image
```

---

# 11. Creating a Gazebo Sim World

Worlds are stored inside:

```text
my_robot_gazebo/worlds
```

Starting point:

```text
empty_world.sdf
```

---

## World Design Rules

To avoid visualization problems:

* Keep the world centered around (0,0)
* Place obstacles symmetrically when possible
* Avoid very large coordinates
* Keep the robot initial position near the origin

---

## Example Wall

```xml
<model name="wall_1">

  <static>true</static>

  <pose>2 0 0.5 0 0 0</pose>

  <link name="link">

    <collision name="collision">
      <geometry>
        <box>
          <size>4 0.1 1</size>
        </box>
      </geometry>
    </collision>

    <visual name="visual">
      <geometry>
        <box>
          <size>4 0.1 1</size>
        </box>
      </geometry>
    </visual>

  </link>

</model>
```

---

## Example Rectangular Room

```text
        y

        ^
        |
  +-------------+
  |             |
  |             |
  |      R      |
  |             |
  |             |
  +-------------+

---------------> x
```

Robot:

```text
R = (0,0)
```

---

# 12. Practical Assignment 1

## Completing the rUBot Arm Model

### Objective

Add a depth camera to the existing arm model.

Students must:

* create camera link
* create fixed joint
* place camera correctly
* generate TF frame
* verify image topics

---

## Deliverables

1. Modified Xacro file
2. RViz screenshot
3. TF tree screenshot
4. Topic verification

---

## Fast Evaluation

Professor checks:

```bash
ros2 topic list | grep camera
```

```bash
ros2 run tf2_tools view_frames
```

Pass criteria:

* Camera frame exists
* Topics exist
* Model loads correctly

Evaluation time:

≈ 2 minutes per student

---

# 13. Practical Assignment 2

## Building the Laboratory World

### Objective

Create the Gazebo Sim world used during the laboratory sessions.

---

### Requirements

World must contain:

* Floor
* Four walls
* Two obstacles
* One docking area
* One target area

Robot initial pose:

```text
x = 0
y = 0
yaw = 0
```

World centered around origin.

---

### Deliverables

1. World file
2. Gazebo screenshot
3. Top-view map screenshot

---

## Fast Evaluation

Professor launches:

```bash
ros2 launch my_robot_bringup my_robot_bringup_gz.launch.py
```

Checks:

* World loads
* Robot appears
* Obstacles visible
* Robot starts at origin

Evaluation time:

≈ 3 minutes per student

---

# 14. Summary

At the end of this chapter students should be able to:

✓ Understand robot models

✓ Interpret TF trees

✓ Understand mecanum kinematics

✓ Understand arm kinematics

✓ Understand bringup architecture

✓ Add sensors

✓ Verify robot systems

✓ Build Gazebo Sim worlds

✓ Use AI tools responsibly to extend robotic systems
