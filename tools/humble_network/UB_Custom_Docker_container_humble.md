## UB custom Docker-based ROS2 Humble environment

We have designed a University of Barcelona custom Docker-based ROS 2 Humble environment to simplify student access to ROS 2 and ensure platform-independent workflows in robotics courses.

A proper Docker Image has been created with the custom configuration on Dockerfile and uploaded to my DockerHub account (https://hub.docker.com/r/manelpuig/ros2-humble-ub-biorob).

This image can be used for:
- **SIM use**: on PC-win (docker-compose_xlaunch.yaml or docker-compose_wsl2.yaml) or on PC-ubuntu/linux (docker-compose.yaml).
- **LAB use**: on PC-ubuntu/linux (docker-compose.yaml) to connect with the rUBot hardware.

**Students** in the lab they only need to:
- Verify you have installed `Docker Engine` and `Docker Compose plugin` from the official Docker repositories. 
- Open VScode in a working directory (e.g., `~/Desktop/rob/`) on your Host PC.
    - Install the `Docker` and `Remote Development` extensions from the VScode marketplace.
    - Clone your forked repository `my_rUBot_mecanum`
- Verify if you have added your user to the Docker group (to avoid using sudo for Docker commands)
```bash
sudo usermod -aG docker $USER
sudo reboot
```

**PC-ubuntu/linux** will work on SIM and LAB use. docker-compose.yaml is configured by default for LAB use.

- In `~/my_rUBot_mecanum/tools/humble_network` review in function of SIM or LAB case, on:
    - `docker-compose.yaml` file: 
        - `ROS_DOMAIN_ID=1` variable to match your Group number.
        - `ROS_AUTOMATIC_DISCOVERY_RANGE` SUBNET (SIM use) or OFF (LAB use).
        - `ROS_STATIC_PEERS` not set (SIM use) or set with your robot IP (LAB Use).
        - Be sure to include: CYCLONEDDS_URI=file:///config/cyclonedds_pc.xml

- Open a terminal in `~/my_rUBot_mecanum/tools/humble_network` and run:
    ````bash
    chmod +x entrypoint_pc.sh
    xhost +local:root            # only in case of Host Ubuntu to allow X11 for Docker 
    docker compose up
    ````
- Verify the environment variables are correctly set by checking the container startup output.
- In Host VScode you can `attach VScode`. You can also connect with container typing:
    ```bash
    docker exec -it pc_humble bash
    code .  # to open VSCode inside the container
    ```
- Clone and compile your ws in `/root/`
- Verify in container **.bashrc** to have:
    ```bash
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
    export CYCLONEDDS_URI=file:///config/cyclonedds_pc.xml
    ```
You are ready to work inside the container and to connect to the robot hardware within ROS2 Humble on Docker!

- To stop the container, open a new terminal on Host in `~/my_rUBot_mecanum/tools/humble_network` and run:
    ```bash
    docker compose down
    ```
- To see the Images and Containers:
    ```bash
    docker ps -a               # containers
    docker images              # images
    ```
- To modify the `Dockerfile`, build and push to Docker Hub, you can follow the instructions:
    ```bash
    docker build -t manelpuig/ros2-humble-ub-biorob:latest .
    docker login
    docker push manelpuig/ros2-humble-ub-biorob:latest
    ```
