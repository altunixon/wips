#### Non-KDE Dolphin \(Openbox\) no thumbnails fix [[arch]]

#### [Unity](https://askubuntu.com/questions/411891/dolphin-does-not-show-thumbnails)
```bash
sudo apt-get install -y ffmpegthumbs mplayerthumbs kffmpegthumbnailer kio-extras

sudo apt-get install -y qt5ct
export QT_QPA_PLATFORMTHEME=qt5ct
```
seems like all it needs is "kio-extra", qt5ct dont actually do anything.</br>

[arch]: https://wiki.archlinux.org/index.php/Qt#Configuration_of_Qt5_apps_under_environments_other_than_KDE
