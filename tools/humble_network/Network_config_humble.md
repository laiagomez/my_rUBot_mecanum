# ROS 2 Humble – Lab Network Setup

## 1. Network topology and ROS 2 setup

This document describes the network setup of a teaching lab with a mobile robot and a control PC, both running ROS 2 Humble.

### 1.1 Physical network

- **WiFi router (mobile router / hotspot)**

  - Provides DHCP and fixed IP addresses in the `192.168.1.x` network.
- **Robot 1**

  - Hardware: Raspberry Pi 4
  - OS: Ubuntu Server 22.04
  - ROS: ROS 2 Humble
  - IP address (fixed): `192.168.1.14`
- **Control PC**

  - Hardware: PC with Ubuntu 22.04
  - ROS: ROS 2 Humble
  - IP address (fixed): `192.168.1.15`

Both machines are connected to the same WiFi router and are in the same Layer-2 network.

### 1.2 ROS 2 environment

The Ubuntu22.04 installations is performed, either with:
- PC Ubuntu22.04 with ROS2 Humble installed.
- External SSD USB Disc with Ubuntu 22.04 and ROS2 Humble installed.
- Docker container (on PC Unix) with ROS2 Humble installed.

In each case the communicacion is ensured by a proper DDS (Data Distribution Service) configuration.

## 2. ROS Networking Middleware

ROS2 network communication is based on DDS (Data Distribution Service) that provides:

- Discovery: nodes find each other automatically.

- Transport: messages go over UDP (usually) on your LAN.

- QoS (Quality of Service): rules for reliability, history, durability, deadlines, etc.

- Multicast/Broadcast (often) for discovery, then unicast for data.

So, DDS is basically the networking middleware that makes ROS 2 communication possible and is accessed through an abstraction layer called RMW (ROS Middleware Interface).

There are different RMW implementations:
- Fast DDS (Default in ROS2)

- Cyclone DDs


### 2.1. Fast DDS (rmw_fastrtps_cpp)

It was developped by eProsima (https://docs.ros.org/en/humble/Installation/RMW-Implementations/DDS-Implementations/Working-with-eProsima-Fast-DDS.html)

Typical strengths:

- Very widely used in ROS 2 ecosystem, lots of examples.

- Good performance and many features; integrates well with some ROS 2 stacks.

Typical weaknesses

- In “messy networks” (hotspots, Wi-Fi isolation, multiple interfaces), discovery can feel more fragile.

- Complex Configuration (profiles XML)

It can be selected with an environment variable:
````shell
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
````

### 2.2. Cyclone DDS (rmw_cyclonedds_cpp)

It was developped by Eclipse (https://docs.ros.org/en/humble/Installation/RMW-Implementations/DDS-Implementations/Working-with-Eclipse-CycloneDDS.html)

Typical strengths

- Often more predictable discovery and behavior in “simple LAN” robotics setups.

- Strong reputation for robustness and good interoperability.

- Simple Configuration via CycloneDDS XML (CYCLONEDDS_URI) is straightforward for static peers / restricted discovery.

Typical weaknesses

- Some complex multi-network setups require careful interface selection.

It can be selected with an environment variable:
````shell
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
````

## 3. Laboratory network configuration

To make the system robust and independent of multicast quirks and startup order, we explicitly choose and configure CycloneDDS to use unicast peer discovery between the PC and the robot.

With this configuration:

- Each machine (PC or rUBot) uses its own fixed IP address for DDS.

- Each machine is given the other machine as a peer (explicit unicast address).

- Discovery does not depend on multicast and works exclusively through explicit unicast peers.

We will:

- Define `ROS_AUTOMATIC_DISCOVERY_RANGE` environment variable values: OFF, LOCALHOST, SUBNET
    - This variable controls how far ROS 2 tries to auto-discover peers.
        - SUBNET (default)
            - Discovers any node reachable via multicast on the local subnet.
            - Use when:
                - Normal home/lab router
                - Multicast works
                - You want “plug and play discovery”
        - LOCALHOST
            - Discovers only nodes on the same machine.
            - Use when:
                - You run everything locally (Gazebo + Nav2 + RViz on one PC)
                - You want to prevent accidental network chatter on a shared LAN
        - OFF
            - Disables automatic discovery completely (even local-machine discovery).
            - nodes will not even discover other nodes on the same machine unless they are explicitly listed as peers.
            - Use when:
                - You want only explicit discovery via ROS_STATIC_PEERS (and/or Cyclone <Peers>)
                - Hotspot/mobile router situations where multicast is broken
                - Multi-robot labs where you want strict control over who sees who

- Define `ROS_STATIC_PEERS` to specify robot/PC IP to communicate with
- Define the `cyclonedds_pc.xml` and `cyclonedds_robot.xml` file for generic network configurations (NetworkInterface, etc)
    - To obtain the NetworkInterface, type:
        ````shell
        ip -br link
        ip -br addr
        ip a
        ````

- Update `.bashrc` to use these configs
    - On the PC: 

        ````bash
        # --- ROS 2 base ---
        source /opt/ros/humble/setup.bash
        source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
        # --- Your workspace ---
        source /home/student/Desktop/my_rUBot_mecanum/install/setup.bash
        cd ~/Desktop/my_rUBot_mecanum
        export QT_QPA_PLATFORM=xcb  # good default for RViz2 on many systems
        # --- ROS 2 networking ---
        export ROS_DOMAIN_ID=1 # Group number 1
        export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
        # Sim mode SUBNET / Lab mode OFF
        export ROS_AUTOMATIC_DISCOVERY_RANGE=OFF
        # Sim mode unset / Lab mode robot IP
        export ROS_STATIC_PEERS=192.168.1.14  # robot IP (14,24,34 or 44)
        # CycloneDDS XML. Not necessary
        #export CYCLONEDDS_URI=file:///home/Desktop/my_rUBot_mecanum/tools/humble_network/cyclonedds_pc.xml
        ````
        > write the proper workspace path, in PC case `/home/student/Desktop/my_rUBot_mecanum`
    - On the robot:

        ````bash
        source /opt/ros/humble/setup.bash
        source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
        source /home/ubuntu/my_rUBot_mecanum/install/setup.bash
        cd /home/ubuntu/my_rUBot_mecanum
        export ROS_DOMAIN_ID=1
        export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
        export ROS_AUTOMATIC_DISCOVERY_RANGE=OFF
        export ROS_STATIC_PEERS=192.168.1.15,192.168.1.16  # PC IP at FacFIS,FacINFORMATICS
        export CYCLONEDDS_URI=file:///home/ubuntu/my_rUBot_mecanum/tools/humble_network/cyclonedds_robot.xml
        ````
        > write the proper workspace path, in robot case `/home/ubuntu/my_rUBot_mecanum`

You are ready to work with ROS2 Humble and control your rUBot!

**Quick checklist if communication does not work**

- PC and robot use the same ROS_DOMAIN_ID
- ROS_AUTOMATIC_DISCOVERY_RANGE=OFF is set on both sides
- ROS_STATIC_PEERS contains the correct IP of the other machine
- Correct NetworkInterface is set in cyclonedds_*.xml
