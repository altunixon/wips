### Enable lirc gpio interface
Edit /boot/config.txt
```bash
sudo vim /boot/config.txt

# Uncomment this to enable infrared communication.
# default input pin 17
#dtoverlay=gpio-ir,gpio_pin=17
# default output pin 18
#dtoverlay=gpio-ir-tx,gpio_pin=18
# here i will use pin 17 for connected ir input module
dtoverlay=gpio-ir,gpio_pin=17

reboot
```
After reboot, lirc (INPUT) device should be available
```bash
ls -l /dev/lirc0
crw-rw---- 1 root video 251, 0 Aug 27 13:04 /dev/lirc0
```
### Install lirc softwares
```bash
sudo apt-get install -y lirc liblirc0 liblirc-dev liblirc-client0 lirc-compat-remotes
```
### Test lirc (INPUT) device
Using lirc mode2
```bash
mode2 -d /dev/lirc0
```
or continous read with ir-ctl
```bash
ir-ctl -d /dev/lirc0 -r
```
if you have setup your ir module correctly, you should receive signal coming in through /dev/lirc0
