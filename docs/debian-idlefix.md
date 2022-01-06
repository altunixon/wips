### system-logind
- Symptoms:
  ```bash

  ```
- Fix: `vim /etc/systemd/logind.conf`</br>
  Change or uncomment `IdleAction=ignore`

### dbus
- Symptoms
  - Screen turning off after every 30 seconds of idle time with KDE Neon 5.8 LTS \(Ubuntu 16.04 LTS\)
  - Noticed that org.freesmartphone.Device.IdleNotifier was sending a idle_prelock signal.</br>
    Sure there were some other signals too, but my screen turning off always seem to start with idle_prelock.
- Fix:
  - Create new dbus config: `vim /etc/dbus-1/system-local.conf`
  - Add this to content:
```xml
<!DOCTYPE busconfig PUBLIC "-//freedesktop//DTD D-Bus Bus Configuration 1.0//EN" "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig>
    <policy context="default">
        <deny send_interface="org.freesmartphone.Device.IdleNotifier" />
    </policy>
</busconfig>
```
  - Reload dbus: `sudo systemctl reload dbus`
- Janky fix: `xset -dpms s off s noblank s 0 0 s noexpose; xset s off; xset dpms 0 7200 0; xset dpms force off`