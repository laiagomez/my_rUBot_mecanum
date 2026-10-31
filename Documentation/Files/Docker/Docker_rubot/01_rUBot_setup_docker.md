# **ROS2 rUBot setup**

The objectives of this section are:
- Setup the rUBot mecanum in virtual environment for simulation
- Setup the rUBot mecanum in raspberrypi4 for real control
- Install needed interfaces

Webgraphy:
- https://github.com/AntoBrandi/Self-Driving-and-ROS-2-Learn-by-Doing-Odometry-Control/tree/main
- https://github.com/AntoBrandi/Self-Driving-and-ROS-Learn-by-Doing-Odometry-Control
- https://github.com/AntoBrandi/Arduino-Bot/tree/humble

## **1. Setup the Robot in virtual environment for simulation**


## **2. Setup the Robot in real control**

To create a fast and robust image of ROS2 Humble for our robot, an improved method is to use a Docker.

References:
- TheConstruct DockerHub: https://hub.docker.com/u/theconstructai
- TheConstruct Final Image Humble-v3: https://hub.docker.com/r/theconstructai/limo/tags

We have 2 different robots:
- UB custom made rUBot mecanum
- Commercial LIMO robot

Each one has speciffic Docker configuration characteristics.

### **2.1. Setup UB custom made rUBot mecanum**

For this robot we will use a computero onboard based on Raspberrypi4 where we will install a RaspberryPi OS (64Bits)-

#### **2.1.1. Install SO**
We can install in the raspberrypi4:
- RaspberryPi OS 64Bits
- Ubuntu22.04 server SO 64bits (Recommended)


**a) RaspberryPi OS 64Bits**

- Run Raspberry Pi Imager (https://www.raspberrypi.org/software/)
  - select Device: Raspberrypi4 (or 5)
  - select OS: RaspberryPi OS (64Bits) to the SD card
  - Select the configurations:
    - Name: rUBot01D
    - User: ubuntu
    - Pass: ubuntu1234
    - LAN config: wifi you want to connect (i.e. Robotics_UB)
    - Regional settings: ES
    - Services: activate ssh
- Insert the SD in a RBPi board and connect an ethernet cable to the router
- Connect the RBPI Board to a display, with mouse and Keyboard
- power the raspberrypi4 and login:
  - login: ubuntu
  - password: ubuntu1234
- update the OS:
  ````shell
  sudo apt update
  sudo apt upgrade
  sudo reboot
  ````
- If you want to change the hostname:
  ````shell
  sudo hostnamectl set-hostname new_hostname
  sudo reboot
  ````
- If you want to configure a fixed IP:
    - "Edit connections"
    - Select the "Robotics_UB" wifi connection
    - In section "IPv4 settings" Select "Manual"
    - Add IP address and choose the desired IP (192.168.1.110), Netmask (255.255.255.0), Gateway (192.168.1.1)
    - Add DNS server (8.8.8.8) for google DNS
    - Apply and reboot

**VNC connections**

- Connect to the raspberrypi with ssh and activate **VNC connections**:
  - type: sudo raspi-config
  - Navigate to: Interface Options > VNC > Select Yes to enable it.
  - sudo reboot
- In your PC install Remote desktop on RealVNC Viewer: https://www.realvnc.com/es/connect/download/viewer

- If you want to connect to another network, you have to be connected first manually to the different networks to enable raspberrypi to connect to on reboot
- reboot and it will be connected to the first network available


#### **2.1.2. Install Docker**

You can use VScode and install the Extensions:
- "Remote Development"
- Docker (from Docker and Microsoft)
- Open VScode and connect remotelly to the Raspberrypi with ssh -X ubuntu@192.168.xxx.xxx
- If you can not connect to the raspberrypi, perhaps you have to regenerate permissions (replace IP-raspberrypi by 192.168.xx.xx):
  ````shell
  ssh-keygen -R 192.168.1.xx
  ````

In raspberrypi, when **RaspberryPi OS** (64Bits), add Docker’s official repository for Ubuntu
  ````shell
  sudo apt update
  sudo apt upgrade
  # install Docker automatically in function of the Raspbian version installed
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  # Start Docker service
  sudo systemctl start docker
  # Enable Docker to start on boot
  sudo systemctl enable docker
  sudo systemctl enable containerd.service
  # Add your user to the Docker group (to avoid using sudo for Docker commands)
  sudo usermod -aG docker $USER
  # Reboot to apply changes (especially for the user group change)
  sudo reboot
  ````
In raspberrypi, when **Ubuntu22.04 server OS** (64Bits)
  ````shell
  sudo apt update
  sudo apt install ca-certificates curl gnupg lsb-release -y
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt update
  sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
  # Start Docker service
  sudo systemctl start docker
  # Enable Docker to start on boot
  sudo systemctl enable docker
  sudo systemctl enable containerd.service
  # Add your user to the Docker group (to avoid using sudo for Docker commands)
  sudo usermod -aG docker $USER
  sudo reboot
  ````

#### **2.1.3. Create a rUBot ROS2 environment**

We first create a Docker folder where we place:
- Dockerfile.robot
- entrypoint.robot.yaml
- docker-compose.robot.yaml
- bringup.sh

>**Important**: make all files executable!
  ````shell
  cd Docker
  sudo chmod +x *
  ````

Follow the instructions:
- To see the Images and Containers:
    ```bash
    docker ps -a               # containers
    docker images              # images
    ```
- To modify the `Dockerfile`, build and push to Docker Hub, you can follow the instructions:
    ```bash
    docker build -f Dockerfile_orbbec.robot -t manelpuig/ros2-humble-ub-rubot:orbbec .
    docker login
    docker push manelpuig/ros2-humble-ub-rubot:orbbec
    ```
- Start the Container
````shell
docker system prune -f
docker compose -f docker-compose_orbbec_services.yaml up
````
>First time this will take 25min aprox.
- If you want to Stop the Container
````shell
docker compose -f docker-compose.robot.yaml down 
````
- To check the running container and to check logs for troubleshooting:
````shell
docker ps
docker logs robot-humble-container
````
- To verify if the container is working type on terminal:
````shell
docker exec -it robot-humble-container /bin/bash
````
- After some time, if the Container do not work properly, delete the image and create it again with docker-compose:
````shell
docker rmi robot_humble_image
docker system prune -f
docker compose -f docker-compose.robot.yaml up -d --build
````

#### **2.1.4. Connect to control rUBot**

We have different possibilities to connect to the rUBot:
- SSH remote Desktop connection to Docker container
- Connect a PC to the same rUBot network
- Using service RRL fro TheConstruct

**a) Connect locally to the robot**

The bringup of the robot is done automatically, but if you want to **work with the container using VScode**, proceed with:
- Select "Remote Explorer" and "Dev Containers"
- Right-click and attatch a new window to this container
- In a new terminal, type:
  ````shell
  ros2 node list
  ````
- You will be ready to work within the container
- In order to see a Plot:
  ````shell
  rqt -s rqt_plot /cmd_vel/linear/x
  ````

**b) Connect a PC to the same rUBot network**

If we have a PC in the same network, we only need to:
- Install Docker Desktop and run it
- Have an X Server like VcXsrv running (https://sourceforge.net/projects/vcxsrv/). Remember to start it with the "Disable access control" option checked.
- A better option is MobaXterm: Free version "Home Edition" (https://mobaxterm.mobatek.net/download-home-edition.html).
- Create folder with a custom Docker container (files in Documentation/Files/Docker_PC) with
  - Dockerfile.pc
  - entrypoint.pc.sh
  - docker-compose.pcXlaunch.yaml
  - docker-compose.pcWSL.yaml
- You have 2 options to create the container:
  - With graphical interface using Xlaunch
    - Open this folder on VScode and type in a new Git Bash terminal:
      ````shell
      docker compose -f docker-compose.pcXlaunch.yaml up -d --build
      ````
      >Remember to change the IP of the PC in this network on docker-compose.pcXlaunch.yaml
  - With graphical interface using WSL
    - This is only usefull if you work inside your computer isolated without the possibility to communicate with other robots on the same network!
    - Open this folder on VScode and type in a new WSL terminal (type first wsl):
      ````shell
      UID=$(id -u) GID=$(id -g) docker compose -f docker-compose.pcWSL.yaml up -d --force-recreate
      ````
- Attach the VScode window to the container
- You need to ensure the network communication with:
  - Windows Network status: WiFi properties to Network profile: "Private"
  - ??
- To test the communication:
  - In ROBOT: Open a terminal and run:
    ````shell
    ros2 run demo_nodes_cpp talker
    ````
  - In PC: Open a new terminal and run:
    ````shell
    ros2 run demo_nodes_cpp listener
    ````
**c) Connect with TheConstruct environment**

- Install the robot: copy the link
- Modify the docker-compose and entrypoint adding the lines corresponding to RRL service
- Stop and remove the container
  ````shell
  docker compose -f docker-compose.robot.yaml down 
  docker system prune -f
  docker compose -f docker-compose.robot.yaml up -d --build
  ````

#### **2.1.5. Start Docker container with services on rUBot**

We have translated the 3 services on rUBot in an equivalent `docker-compose_orbbec_services.yaml`

- Open an VScode terminal on `Files/Docker/Docker_rubot`
- Launch the:
  ````bash
  docker system prune -f
  docker compose -f docker-compose_orbbec_services.yaml up -d
  ````
- To proper network communication update `.bashrc` to use these configs
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



### **2.2. Setup the commercial LIMO robot**

The LIMO robot has a Jetson Nano computer onboard with Ubuntu20 and ROS Noetic & Foxy installed.

On Local you have a complete workspace:
- limo_ros: for ROS1 Noetic
- ros2_limo_ws: for ROS2

TheConstruct has made custom Limo Docker image to fast and proper operate:https://hub.docker.com/r/theconstructai/limo/tags
- theconstructai/limo:humble-v2: for astra camera model
- theconstructai/limo:humble-v3: for orbbec camera model

Our camera model is Orbbec: https://github.com/orbbec/OrbbecSDK_ROS2/tree/main

We follow the instructions on https://hub.docker.com/r/theconstructai/limo

In Files/Docker_limo you will find all the needed files to launch the docker-compose-v3.yaml. Copy them to the Limo home at ~/limo_docker
````shell
cd limo_docker
docker system prune
docker compose -f docker-compose-v3.yaml up -d
````

Add to the .bashrc file:
````bash
export ROS_DOMAIN_ID=0
````
>To be sure to point at the same robot. If you work simultaneously with 2 robots, the second one will have another ROS_DOMAIN_ID
