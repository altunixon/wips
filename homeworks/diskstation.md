### Disable thumbnail generation
**(2012 community thread)**:
DSM --> Control Panel --> Media Indexing --> Indexed Folder</br>
Create: /photo/subdir: --> unselect all file types</br>
```bash
/usr/syno/etc/rc.d/S77synomkthumbd.sh stop
/usr/syno/etc/rc.d/S77synomkthumbd.sh start
```
Double checked Control Panel > Media Server > Thumbnail Settings > Thumbnail Progress</br>
</br>
**(2017 jeffcosta blogpost)**:
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
SSH into the device and you should no longer see any instance of the thumbd.</br>
or, slightly more official perhaps:
```bash
synoservice --disable synomkthumbd
```
under DSM 7.0, which uses systemd, the command is basically:
```bash
systemctl stop pkg-FileStation-thumbd.service
systemctl disable pkg-FileStation-thumbd.service
```
### Fan replacement guide (by asrk)
Tl;dr: You need one with a "rotor lock" detection, not one of those with a PWM tachometer output.



(2012 community thread): https://community.synology.com/enu/forum/17/post/37552
(2017 jeffcosta blogpost): http://blog.jeffcosta.com/2017/09/04/disable-thumbd-daemon-on-synology-diskstation/
(by asrk): http://www.askrprojects.net/other/synofan/index.html
