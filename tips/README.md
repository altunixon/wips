### Non-KDE Dolphin \(Openbox\) no thumbnails fix [[arch]] NOT WORKING

### [Unity](https://askubuntu.com/questions/411891/dolphin-does-not-show-thumbnails) NOT WORKING
```bash
sudo apt-get install -y ffmpegthumbs mplayerthumbs kffmpegthumbnailer kio-extras

sudo apt-get install -y qt5ct
export QT_QPA_PLATFORMTHEME=qt5ct
```
seems like all it needs is "kio-extra", qt5ct dont actually do anything.</br>

### Screen auto attach ONLY if login from ssh and is the first connection /dev/pts/0
```bash
echo "if [ $STY = '' ] && [ $SSH_TTY != '' ] && [ $SSH_TTY = "/dev/pts/0" ]; then screen -xR; fi" >> ~/.bashrc
```

### DYI Route 53 dynamic DNS
[Server-less dydns]


[arch]: https://wiki.archlinux.org/index.php/Qt#Configuration_of_Qt5_apps_under_environments_other_than_KDE
[Server-less dydns]: https://aws.amazon.com/jp/blogs/startups/building-a-serverless-dynamic-dns-system-with-aws/
