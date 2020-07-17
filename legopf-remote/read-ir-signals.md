### [Guide by shallowsky](https://shallowsky.com/blog/hardware/raspberry-pi-ir-remote.html)

#### Install packages and test hardware
- Install LIRC and enable the drivers on the Pi
  ```bash
  sudo apt-get install lirc python-lirc python3-lirc
  ```
- Then you have to enable the lirc daemon. </br>
  Assuming the sensor's pin is on the Pi's GPIO 18, edit /boot/config.txt as root, look for this line and uncomment it: 
  ```bash
  # Uncomment this to enable the lirc-rpi module
  dtoverlay=lirc-rpi
  ```
  As for where the [GPIO] pin 18 is:
    ![40-pin GPIO header](https://github.com/altunixon/wips/new/master/legopf-remote/gpio-40-pin-header.png)
    ![40-pin GPIO number](https://github.com/altunixon/wips/new/master/legopf-remote/gpio-40-pin-number.png)
- Reboot. </br>
  Then use a program called mode2 to make sure you can read from the remote at all, </br>
  after first making sure the lirc daemon isn't running: 
  ```bash
  sudo systemctl stop lirc
  ps aux | grep lirc
  mode2 -d /dev/lirc0
  ```
  Press a few keys. If you see a lot of output, you're good. If not, check your wiring. 

#### Set up a lircd.conf
- You'll need to make an lircd.conf file mapping the codes the buttons send to symbols like KEY_PLAY. </br>
  You can do that -- ina somewhat slow and painstaking process -- with irrecord. </br>
  First you'll need a list of valid key names. </br>
  Get that with irrecord -l and you'll probably want to keep that window up so you can search or grep in it. </br>
  Open another window and run: </br>
  ```bash
  irrecord -d /dev/lirc0 ~/lircd.conf
  ```
  You will probably have to repeat the command a couple of times; the first few times it might not beable to read anything. </br>
  But once it's running, then for each key on the remote, </br>
  first, find the key name that most closely matches what you want the key to do </br>
  (for instance, if the key is the power button, irrecord -l | grep -i power will suggest KEY_POWER and KEY_POWER2). </br>
  Type or paste that key name into irrecord -d, then press the key. </br>
  At the end of this, you should have a ~/lircd.conf. </br>
  *Some guides say to copy that lircd.conf to /etc/lirc/, </br>
  but I'm not sure it matters since you're going to be running your programs as $USER rather than root. 
- Then enable the lirc daemon that you stopped back when you were testing with mode2. </br>
  In /etc/lirc/hardware.conf, START_LIRCMD is commented out, so uncomment it. </br>
  Then edit /etc/lirc/hardware.conf as specified in [alexba.in]'s "[Setting Up LIRC on the RaspberryPi]". </br>
  Now you can start the daemon: 
  ```bash
  sudo systemctl start lirc
  ps aux | grep lirc
  ```

#### Testing with irw
- Run irw:
  ```bash
  irw
  ```
  Press buttons, and hopefully you'll see lines like:
  ```bash
  0000000000fd8877 01 KEY_2 /home/pi/lircd.conf
  0000000000fd08f7 00 KEY_1 /home/pi/lircd.conf
  0000000000fd906f 00 KEY_VOLUMEDOWN /home/pi/lircd.conf
  0000000000fd906f 01 KEY_VOLUMEDOWN /home/pi/lircd.conf
  0000000000fda05f 00 KEY_PLAYPAUSE /home/pi/lircd.conf
  ```
  If they correspond to the buttons you pressed, your lircd.conf is working. 

#### Python [example](https://github.com/akkana/scripts/blob/master/rpi/pyirw.py)
```python
#!/usr/bin/env python

# Read lirc output, in order to sense key presses on an IR remote.
# There are various Python packages that claim to do this but
# they tend to require elaborate setup and I couldn't get any to work.
# This approach requires a lircd.conf but does not require a lircrc.
# If irw works, then in theory, this should too.
# Based on irw.c, https://github.com/aldebaran/lirc/blob/master/tools/irw.c

import socket

SOCKPATH = "/var/run/lirc/lircd"
sock = None

def init_irw():
    global sock
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    print ('starting up on %s' % SOCKPATH)
    sock.connect(SOCKPATH)

def next_key():
    '''Get the next key pressed. Return keyname, updown.
    '''
    while True:
        data = sock.recv(128)
        # print("Data: " + data)
        data = data.strip()
        if data:
            break
    words = data.split()
    return words[2], words[1]

if __name__ == '__main__':
    init_irw()
    while True:
        keyname, updown = next_key()
        print('%s (%s)' % (keyname, updown))
```

[GPIO]: https://www.raspberrypi.org/documentation/usage/gpio/
[alexba.in]: http://alexba.in/blog/2013/01/06/setting-up-lirc-on-the-raspberrypi/
[Setting Up LIRC on the RaspberryPi]: https://github.com/altunixon/wips/tree/master/tips/rpi-lirc-alexba.htm
