# System and Printer configuration

## System configuration
Install all these packages:
```bash
sudo apt-get install -y git libcups2-dev libcupsimage2-dev cups lpr build-essential system-config-printer wiringpi python-serial python-pil python-unidecode
```

## [Adafruit Mini Thermal Receipt Printer](https://www.adafruit.com/product/597) configuration

Configuration via serial port.

### update Serial configuration
Run `sudo raspi-config`:
- Interfacing Options
  - Serial > Turn **OFF** the **login shell** over serial, and **ENABLE** the hardware **serial port**. **NO** and **YES**, respectively.

Reboot the Raspberry Pi: `sudo reboot`.

### Printer configuration

Connect the printer to the correct Pins in the Raspberry Pi (pin 6, 8 and 10), and try to print some text:

```bash
stty -F /dev/serial0 19200
echo -e "This is a test.\\n\\n\\n" > /dev/serial0
```

"*This is a test.*" should print.

### printer drivers

Install printer drivers:
```bash
cd ~
git clone https://github.com/adafruit/zj-58
cd zj-58
make
sudo ./install
```

The `make` command will output a warning, but still works:

```bash
# output of the make command

rastertozj.c:87:16: warning: ‘rasterModeStartCommand’ is static but used in inline function ‘rasterheader’ which is not static
  outputCommand(rasterModeStartCommand);
                ^~~~~~~~~~~~~~~~~~~~~~
gcc  -o rastertozj rastertozj.o -lcupsimage -lcups
```

Configure printer:
```bash
sudo lpadmin -p ZJ-58 -E -v serial:/dev/serial0?baud=19200 -m zjiang/ZJ-58.ppd
sudo lpoptions -d ZJ-58

# Share printer on the local network
sudo cupsctl --share-printers
```

The printer named `ZJ-58` is now ready to be used via command line, or over the network.

## [Epson TM-T88V](https://epson.com/For-Work/Point-of-Sale/POS-Printers/TM-T88V-POS-Receipt-Printer/p/C31CA85084) configuration

Configuration via the USB port.

### printer drivers

Install printer drivers:
```bash
cd ~
git clone https://github.com/plinth666/epsonsimplecups
cd epsonsimplecups
sudo make
sudo make install
```

### printer configuration

Find the cups direct usb device for printer:
```bash
sudo lpinfo -v | grep 'EPSON'
```

the command should print something like:
```bash
direct usb://EPSON/TM-T88V?serial=4D5135467263910000
```

Configure printer:
```bash
sudo lpadmin -p TM-T88V -E -v usb://EPSON/TM-T88V?serial=4D5135467263910000 -P ppd/EpsonTMT20Simple.ppd
sudo lpoptions -d TM-T88V

# Share printer on the local network
sudo cupsctl --share-printers
```

The printer named `TM-T88V` is now ready to be used via command line, or over the network.

## Print via command line

Reboot the Raspberry Pi: `sudo reboot`.

Test to print something:

```bash
echo "This is a test." | lp
lp /usr/share/cups/data/testprint -d <PRINTER-NAME>
lp -o fit-to-page ./image.png
```

---
