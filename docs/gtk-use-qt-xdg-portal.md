## Install xdg-desktop-portal
```bash
sudo apt-get install -y xdg-desktop-portal xdg-desktop-portal-kde
```
**NOTE:** You should not have both `xdg-desktop-portal-kde`, and `xdg-desktop-portal-gtk` installed at the same time, this typically will not work or behave in strange/unpredictable ways, as these packages will conflict with each other.
```bash
sudo apt-get remove --purge xdg-desktop-portal-gtk 
sudo apt-get install -y xdg-desktop-portal-kde
```

## Config file
- In `~/.xsession`:</br>
  - `export XDG_CURRENT_DESKTOP=Openbox`: Set Desktop Environment name
  - `export GTK_USE_PORTAL=1`: Set global default for all GTK3 apps to use xdg portal
  - `exec /usr/libexec/xdg-desktop-portal &`: Run xdg-desktop-portal daemon, this will spawn `xdg-desktop-portal-kde`
- For xdg-desktop-portal-kde: `/usr/share/xdg-desktop-portal/portals/kde.portal`</br>
  add `UseIn=KDE;Openbox`
- For xdg-desktop-portal-gtk: `/usr/share/xdg-desktop-portal/portals/gtk.portal`</br>
  remove if this exists, usually will be removed if you run `apt-get remove` with the `--purge` flag

## Individual use
- Run program with `GTK_USE_PORTAL=1 <program>`</br>
  i.e. `GTK_USE_PORTAL=1 /usr/bin/firefox`
- Add to `/usr/share/applications/<program>.desktop` file:</br>
  At `Exec=` directive: `Exec=GTK_USE_PORTAL=1 /usr/lib/firefox-esr/firefox-esr %u` 
- For firefox: Navigate to `about:config`, Search for `widget.use-xdg-desktop-portal` toggle this option to `True`
