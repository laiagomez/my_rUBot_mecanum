# **Setup UB custom made rUBot mecanum**

For this robot we will use a computero onboard based on Raspberrypi4 where we will install a Ubuntu22.04 server OS (64Bits)

## **Install Ubuntu22.04 server OS 64Bits**

- Run Raspberry Pi Imager (https://www.raspberrypi.org/software/)
  - select Device: Raspberrypi4 (or 5)
  - select OS: Ubuntu22.04 server OS (64Bits) to the SD card
  - Select the configurations:
    - Name: rUBot01D
    - User: ubuntu
    - Pass: ubuntu1234
    - LAN config: wifi you want to connect (i.e. Robotics_UB)
    - Regional settings: ES
    - Services: activate ssh
- Insert the SD in a RBPi board and connect an ethernet cable to the router
- Identify the IP with IP-scan an open VScode window
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
- Change the /etc/hosts with the new name in first line:
  ````bash
  127.0.1.1 rubot06
  ````
- Now if you connect the raspberrypi to a router with ethernet cable you will be able to connect with another computer with ssh protocol:
  ````bash
  ssh ubuntu@rubot06.local
  ````
- Using VScode with `Remote-SSH` extension:
  ````xml
  Host rUBot06_on_Ethernet
    HostName rubot06.local
    ForwardX11 yes
    User ubuntu
  ````

## Change Netplan configuration for Ethernet + Multiple WiFi

This guide explains how to configure a Raspberry Pi with Ubuntu Server
so that:

-   Ethernet (`eth0`) is the **primary connection**
-   WiFi (`wlan0`) is used as **fallback**
-   Multiple WiFi SSIDs can be configured

This setup is particularly useful for robotics or ROS2 environments
where a wired connection is preferred but WiFi is still available when
needed.

Fist of all you have to connect to the raspberrypi with VScode:
- If you can not connect to the raspberrypi, perhaps you have to regenerate permissions (identify IP-raspberrypi: xx.xx.xx.xx):
  ````shell
  ssh-keygen -R xx.xx.xx.xx
  ````

### 1. Create Ethernet configuration

Create a dedicated Netplan file for Ethernet.

``` bash
sudo nano /etc/netplan/60-ethernet.yaml
```

Content:

``` yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true
      optional: true
```

Apply:

``` bash
sudo chmod 600 /etc/netplan/60-ethernet.yaml
sudo netplan apply
```

------------------------------------------------------------------------

### 2. Disable cloud-init network configuration

Ubuntu images generated with Raspberry Pi Imager usually create a file
called `50-cloud-init.yaml`. This file is automatically managed by
cloud-init.

Disable cloud-init network configuration so you can manage Netplan
yourself:

``` bash
echo 'network: {config: disabled}' | sudo tee /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
```

------------------------------------------------------------------------

### 3. Disable the original Netplan file

Keep a backup but prevent Netplan from loading it.

``` bash
sudo cp /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml.bak
sudo mv /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.disabled
```

Now Netplan will only read the new configuration files.

------------------------------------------------------------------------

### 4. Create WiFi configuration

Create a new Netplan file:

``` bash
sudo nano /etc/netplan/70-wifi.yaml
```

Example configuration with two SSIDs:

``` yaml
network:
  version: 2
  wifis:
    wlan0:
      dhcp4: true
      optional: true
      regulatory-domain: ES
      access-points:
        "Robotics_UB":
          password: "rUBot_xx"
        "ssid2":
          password: "pass2"
```

Apply:

``` bash
sudo chmod 600 /etc/netplan/70-wifi.yaml
sudo netplan apply
```

------------------------------------------------------------------------

### 5. Install useful WiFi diagnostic tools

These tools help debugging WiFi connectivity.

``` bash
sudo apt update
sudo apt install iw wireless-tools wpasupplicant
```

------------------------------------------------------------------------

### 6. Verify WiFi networks

Scan visible networks:

``` bash
sudo iwlist wlan0 scanning | grep ESSID
```

Check current connection:

``` bash
iw dev wlan0 link
```

Show assigned IP addresses:

``` bash
ip a
```

------------------------------------------------------------------------

### 7. Expected final configuration

Example result:

    eth0  → 192.168.67.xx   metric 100
    wlan0 → 192.168.67.yy   metric 600

Meaning:

-   Ethernet is the **primary route**
-   WiFi is **fallback**

------------------------------------------------------------------------

### 8. Test automatic WiFi switching

If the first SSID becomes unavailable:

1.  `wpa_supplicant` scans for available networks
2.  It connects to the next configured SSID

------------------------------------------------------------------------

### 9. Connect from another computer

Example SSH connections:

Ethernet:

``` bash
ssh ubuntu@192.168.67.71
```

WiFi:

``` bash
ssh ubuntu@192.168.67.74
```

