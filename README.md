# Ultimate Thermal Printer


## Linux Installation and Configuration

### Download Raspbian
Works either with Desktop and Lite
> https://www.raspberrypi.org/downloads/raspbian/

### Prepare SD Card

```bash
# List disk
diskutil list

# Assuming SD Card is /dev/disk2
diskutil unmountDisk /dev/disk2

# Burn image to SD Card
sudo dd bs=1m if=path/to/raspbian.img of=/dev/rdisk2

# See the boot volume
ls -ls /Volumes/boot

# Enabling SSH
touch /Volumes/boot/ssh

# Add Network Info
nano /Volumes/boot/wpa_supplicant.conf
```

Add the following:
```bash
country=FR
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="<NETWORK-NAME>"
    psk="<NETWORK-PASSWORD>"
    key_mgmt=<WPA-PSK/NONE>
    priority=1
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
  - Change Locale > Add `en_US.UTF-8 UTF-8`, `fr_FR.UTF-8 UTF-8`
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

### update Serial configuration
Run `sudo raspi-config`:
- Interfacing Options
  - Serial > Turn **OFF** the **login shell** over serial, and **ENABLE** the hardware **serial port**. **NO** and **YES**, respectively.

Reboot the Raspberry Pi: `sudo reboot`.

### Printer configuration

Connect the printer to the correct Pins in the Raspberry Pi, and try to print some text:

```bash
stty -F /dev/serial0 19200
echo -e "This is a test.\\n\\n\\n" > /dev/serial0
```

"*This is a test.*" should print.

### printer libraries and drivers

Install all these packages:
```bash
sudo apt-get install -y git libcups2-dev libcupsimage2-dev cups lpr build-essential system-config-printer wiringpi python-serial python-pil python-unidecode
```

Install printer drivers:
```bash
cd ~
git clone https://github.com/adafruit/zj-58
cd zj-58
make
sudo ./install
```

The `make` command will output an error, but still works:

```bash
# output of the make command

rastertozj.c:87:16: warning: ‘rasterModeStartCommand’ is static but used in inline function ‘rasterheader’ which is not static
  outputCommand(rasterModeStartCommand);
                ^~~~~~~~~~~~~~~~~~~~~~
gcc  -o rastertozj rastertozj.o -lcupsimage -lcups
```

Configure printer
```bash
sudo lpadmin -p ZJ-58 -E -v serial:/dev/serial0?baud=19200 -m zjiang/ZJ-58.ppd
sudo lpoptions -d ZJ-58

# Share printer on the local network
sudo cupsctl --share-printers
```

Reboot the Raspberry Pi: `sudo reboot`.

Test to print something:

```bash
echo "This is a test." | lp
lp -o fit-to-page ./image.png
```

The printer is now ready to be used via command line, or over the network.

---
## Resources
- https://desertbot.io/blog/setup-pi-zero-w-headless-wifi
- https://learn.adafruit.com/pi-thermal-printer/raspberry-pi-os-setup
- https://learn.adafruit.com/networked-thermal-printer-using-cups-and-raspberry-pi
- https://www.cups.org/doc/sharing.html
- https://wiki.archlinux.org/index.php/systemd-timesyncd
- https://bbs.archlinux.org/viewtopic.php?id=182600
- https://www.linuxquestions.org/questions/linux-newbie-8/where-does-raspbian-stretch-assign-default-ntp-servers-4175618162/
- https://unix.stackexchange.com/questions/284354/problems-with-timesyncd-or-networkd