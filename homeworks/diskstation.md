### Disable thumbnail generation
**(2012 community thread)** </br>
~~DSM --> Control Panel --> Media Indexing --> Indexed Folder</br>
Create: /photo/subdir: --> unselect all file types~~</br>
```bash
/usr/syno/etc/rc.d/S77synomkthumbd.sh stop
/usr/syno/etc/rc.d/S77synomkthumbd.sh start
```
~~Double checked Control Panel > Media Server > Thumbnail Settings > Thumbnail Progress~~</br>
</br>
**(2017 jeffcosta blogpost)**
```bash
ps aux | grep 'thumb\|@'
6790 ? Ssl 0:00 /var/packages/FileStation/target/sbin/thumbd
6792 ? Ss 0:00 /var/packages/FileStation/target/sbin/thumbd
6793 ? Ss 0:00 /var/packages/FileStation/target/sbin/thumbd
6818 ? Ssl 0:13 /var/packages/CloudSync/target/sbin/syno-cloud-syncd /volume1/@cloudsync/config/daemon.conf
6987 ? Ss 0:00 /var/packages/FileStation/target/sbin/thumbd
6988 ? Ss 0:00 /var/packages/FileStation/target/sbin/thumbd
6989 ? Ss 0:00 /var/packages/FileStation/target/sbin/thumbd
6990 ? Ss 0:00 /var/packages/FileStation/target/sbin/thumbd
6991 ? Ss 0:00 /var/packages/FileStation/target/sbin/thumbd
6992 ? Ss 0:00 /var/packages/FileStation/target/sbin/thumbd
6993 ? Ss 0:00 /var/packages/FileStation/target/sbin/thumbd
6994 ? Ss 0:00 /var/packages/FileStation/target/sbin/thumbd
```
*You cannot disable or turn off the FileStation functionality without breaking some core GUI items that are required for normal functioning in the web interface.*</br>
But, you can stop the thumbd service from running and chewing up unnecessary system resources.</br>
Here’s how:
```bash
cd /var/packages/FileStation/target/etc/conf
mv thumbd.conf{,.orig}
reboot
```
SSH into the device and you should no longer see any instance of the thumbd. or, slightly more official perhaps:
```bash
$ synoservice --help
Copyright (c) 2003-2020 Synology Inc. All rights reserved.

SynoService Tool Help (Version 25426)
Usage: synoservice
        --help                                                  Show this help
        --help-dev                                              More specialty functions for deveplopment
        --is-enabled            [ServiceName]                   Check if the service is enabled
        --status                [ServiceName]                   Get the status of specified services
        --enable                [ServiceName]                   Set runkey to yes and start the service (alias to --start)
        --disable               [ServiceName]                   Set runkey to no and stop the service (alias to --stop)
        --hard-enable           [ServiceName]                   Set runkey to yes and start the service and its dependency (alias to --hard-start)
        --hard-disable          [ServiceName]                   Set runkey to no and stop the service and its dependency (alias to --hard-stop)
        --restart               [ServiceName]                   Restart the given service
        --reload                [ServiceName]                   Reload the given service
        --pause                 [ServiceName]                   Pause the given service
        --resume                [ServiceName]                   Resume the given service
        --pause-by-reason       [ServiceName]   [Reason]        Pause the service by given reason
        --resume-by-reason      [ServiceName]   [Reason]        Resume the service by given reason
        --pause-all             (-p)    [Reason]        (Event) Pause all service by given reason with optional event(use -p to include packages)
        --pause-all-no-action   (-p)    [Reason]        (Event) Set all service runkey to no but leave the current service status(use -p to include packages)
        --resume-all            (-p)    [Reason]                Resume all service by given reason(use -p to include packages)
        --reload-by-type        [type]          (buffer)        Reload services with specified type
        --restart-by-type       [type]          (buffer)        Restart services with specified type
                                                                Type may be {file_protocol|application}
                                                                Sleep $buffer seconds before exec the command (default is 0)

$ synoservice --disable synomkthumbd
$ synoservice --hard-disable synomkthumbd
# you still needs to restart the dsm box for this to take effect, since even --hard-disable doesnt do what it said it does
```
~~under DSM 7.0, which uses systemd, the command is basically~~: DSM(6.4) < 7 does not support systemctl (not using systemd)
```bash
systemctl stop pkg-FileStation-thumbd.service
systemctl disable pkg-FileStation-thumbd.service
```
### Kill @eaDir (invalid paths)
To stop the folders from being created:
```bash
# most of these dont exists
cd /usr/syno/etc.defaults/rc.d
S66synoindexd.sh stop
S77synomkthumbd.sh stop
S88synomkflvd.sh stop
S99iTunes.sh stop
chmod 000 S66synoindexd.sh S77synomkthumbd.sh S88synomkflvd.sh S99iTunes.sh
```
To re-enable the folders being created:
```bash
# most of these dont exists
cd /usr/syno/etc.defaults/rc.d
chmod 655 S66synoindexd.sh synomkthumbd.sh S88synomkflvd.sh S99iTunes.sh
S66synoindexd.sh start
S77synomkthumbd.sh start
S88synomkflvd.sh start
S99iTunes.sh start
```
To delete *all* @eaDir folders on your system: </br>
CAUTION:  This will delete files without confirmation, so be sure you have it right!!
```bash
cd /volume1/music
find . -name @eaDir -print | while read n ; echo $n ; rm -rf "$n" ; done
```
### Fan replacement guide (by asrk)
Tl;dr: You need one with a "rotor lock" detection, not one of those with a PWM tachometer output.



(2012 community thread): https://community.synology.com/enu/forum/17/post/37552
(2017 jeffcosta blogpost): http://blog.jeffcosta.com/2017/09/04/disable-thumbd-daemon-on-synology-diskstation/
(by asrk): http://www.askrprojects.net/other/synofan/index.html
