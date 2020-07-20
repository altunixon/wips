### Download latest Raspbian/Ubuntu (Prefer 64bit OS for Rpi4)
Raspbian (32bit): https://downloads.raspberrypi.org/raspios_lite_armhf_latest </br>
Ubuntu 18.04 (32bit): https://ubuntu.com/download/raspberry-pi/thank-you?version=18.04&versionPatch=.4&architecture=armhf+raspi3 </br>
Ubuntu 20.04 (32bit): https://ubuntu.com/download/raspberry-pi/thank-you?version=20.04&architecture=armhf+raspi </br>
Ubuntu 18.04 (64bit): https://ubuntu.com/download/raspberry-pi/thank-you?version=18.04&versionPatch=.4&architecture=arm64+raspi3 </br>
Ubuntu 20.04 (64bit): https://ubuntu.com/download/raspberry-pi/thank-you?version=20.04&architecture=arm64+raspi </br>
Ubuntu MATE 18.04 (64bit): https://ubuntu-mate.org/download/arm64/bionic/ </br>
Ubuntu MATE 20.04 (64bit): https://ubuntu-mate.org/download/arm64/focal/ </br>
Flash image to sdcard with yout preferred program
### Migrate SD Card content to external HDD
- Using another *nix computer:
  - Connect both the SD card and external hdd to said computer
    ```bash
    sudo lsblk
    # create mount folders
    sudo mkdir -p /media/$USER/rpi-sdcard/{boot,root,hdd}
    # mount sdcard boot partition (for editing cmdline.txt, touch ssh, etc...)
    sudo mount /dev/sdm1 /media/$USER/rpi-sdcard/boot
    # mount sdcard root partition to migrate its content to external hdd
    sudo mount /dev/sdm2 /media/$USER/rpi-sdcard/root
    ```
  - Prepare external hdd for migration
    ```bash
    # edit external hdd partition table, follow other guide and pray lord, be careful
    sudo fdisk /dev/sdq
    # format external hdd as root partion (ext4)
    sudo mkfs.ext4 /dev/sdq1
    # optional, format another partition to use as /home
    sudo mkfs.ext3 /dev/sdq2
    # mount external hdd root partition
    sudo mount /dev/sdq1 /media/$USER/rpi-sdcard/hdd
    ```
  - Migrate sdcard /root to external hdd
    ```bash
    # migrate sdcard root partition to external hdd
    sudo cp --archive /media/$USER/rpi-sdcard/root/* /media/$USER/rpi-sdcard/hdd/
    ```
  - Edit **external hdd's** /etc/fstab
    ```bash
    sudo vim /media/$USER/rpi-sdcard/hdd/etc/fstab
    ```
    Modify Line:
    ```
    PARTUUID=ed8acfca-02  /               ext4    defaults,noatime  0       1
    ```
    Set **PARTUUID=ed8acfca-02** to **external hdd's** partition id.
  - Backup then modify **sdcard's** boot config cmdline.txt
    ```bash
    sudo cp /media/$USER/rpi-sdcard/boot/cmdline.{txt,sd}
    sudo vim /media/$USER/rpi-sdcard/boot/cmdline.txt
    ```
    Change boot line's option **root=PARTUUID=ed8acfca-02**:
    ```
    dwc_otg.lpm_enable=0 console=tty1 root=PARTUUID=ed8acfca-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait
    ```
    to **external hdd's** partition id.
  - Finish, you can now unmount sdcard and external hdd, insert both to your rpi and powerup.
- Using the Rpi itself:
  - Connect external hdd to the pi
  - Prepare external hdd for migration
    ```bash
    sudo lsblk
    sudo mkdir -p /media/$USER/rpi-hdd
    # edit external hdd partition table, follow other guide and pray lord, be careful
    sudo fdisk /dev/sdq
    # format external hdd as root partion (ext4)
    sudo mkfs.ext4 /dev/sdq1
    # optional, format another partition to use as /home
    sudo mkfs.ext3 /dev/sdq2
    # mount external hdd root partition
    sudo mount /dev/sdq1 /media/$USER/rpi-hdd
    ```
  - Migrate sdcard /root to external hdd
    ```bash
    # migrate sdcard root partition to external hdd
    rsync -ax / /media/$USER/rpi-hdd/
    ```
  - Edit **external hdd's** /etc/fstab (same as above)
  - Backup then modify **sdcard's** boot config cmdline.txt (same as above)
  - Finish, you can now reboot.

- The pi will boot using **sdcard's** boot config, which will then mount **external hdd** as root partition (if god wills it). </br>
  Preferred method is mounting both sdcard and external hdd since migrating from a non active os is much more stable

### Other Sources:
[Adafruit Guide](https://cdn-learn.adafruit.com/downloads/pdf/external-drive-as-raspberry-pi-root.pdf)
[Rpi forum Sticky](https://www.raspberrypi.org/forums/viewtopic.php?t=44177)
