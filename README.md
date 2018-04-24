# Ultimate Thermal Printer


## Linux Installation and Configuration

### Step 1: Download Raspbian Lite
> https://www.raspberrypi.org/downloads/raspbian/

### Step 2: Prepare SD Card

```
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
```
country=FR
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="NETWORK-NAME"
    psk="NETWORK-PASSWORD"
}
```

Eject the SD Card:
```
diskutil eject /dev/disk2
```

Insert the SD Card into the Raspberry Pi. Boot and wait a minute.
