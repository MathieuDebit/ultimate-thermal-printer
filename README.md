# Ultimate Thermal Printer


## Linux Installation and Configuration

### Download Raspbian Lite
> https://www.raspberrypi.org/downloads/raspbian/

### Prepare SD Card

```bash
# List disk
diskutil list

# Assuming SD Card is /dev/disk2
diskutil unmountDisk /dev/disk2

# Burn image to SD Card
sudo dd bs=1m if=~/Downloads/2018-04-18-raspbian-stretch-lite.img of=/dev/disk2

# See the boot volume
ls -ls /Volumes/boot

# Enabling SSH
touch /Volumes/boot/ssh

# Add Network Info
vim /Volumes/boot/wpa_supplicant.conf
```

Add the following:
```bash
country=FR
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="NETWORK-NAME"
    psk="NETWORK-PASSWORD"
}
```

Eject the SD Card:
```bash
diskutil eject /dev/disk2
```

Insert the SD Card into the Raspberry Pi. Boot and wait a minute.

### First Boot

#### Login over Wifi
Default user is **pi** with a password of **raspberry**.
Be sure your computer and Raspberry Pi are connected to the same local network.

```bash
# Remove any previous pi@raspberry.local hosts in SSH config
ssh-keygen -R raspberrypi.local

# Connect to Raspberry Pi
ssh pi@raspberrypi.local
```

#### Basic System Configuration

Configure the Raspberry Pi:
```bash
sudo raspi-config
```

- Change User Password
- Network Options
  - Change Hostname
- Localisation Options
  - Change Locale > Add `en_US.UTF-8 UTF-8`, `fr_FR.UTF-8 UTF-8` and use `fr_FR.UTF-8 UTF-8` as default locale
  - Change Timezone > `Europe/Paris`
  - Change Keyboard Layout
  - Change Wi-fi country > `FR France`

Select `Finish` and reboot the Raspberry Pi with `sudo reboot`. Then connect with `pi@<HOSTNAME>` and the new password.

#### Updates
```bash
sudo apt update -y && sudo apt upgrade -y
```

The Raspberry Pi is now ready to be setup for the printer.

## System configuration for printer

Run `sudo raspi-config` and update Serial configuration
- Interfacing Options
  - Serial > Turn **OFF** the **login shell** over serial, and **ENABLE** the hardware **serial port**. **NO** and **YES**, respectively.

Reboot the Raspberry Pi: `sudo reboot`.