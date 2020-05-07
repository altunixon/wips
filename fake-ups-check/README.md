### USAGE
```bash
ups-ping.sh <IP_ADDR> <DELAY_MINUTES> [recovery]
```

### DESCRIPTION
**Should REALLY be run with crontab** <br/>
ERROR_FILE: "/tmp/ups-ping.err" <br/>
Ping <IP_ADDR> with 4 package, if failed schedule shutdown after DELAY_MINUTES <br/>
Set DELAY_MINUTES = 0 to shutdown immediately. <br/>
If recovery flag is set, if next check falls within DELAY_MINUTES is successful, <br/>
scheduled shutdown will be cancelled. <br/>

### Ping
Ping <IP_ADDR> 4 times
```bash
ping -c 4 $IP_ADDR &> /dev/null
```

### Shutdown|Reboot
Wait 5 mins before starting the shutdown sequence.
```bash
sudo shutdown -P +5
```
Wait 5 mins before reboot.
```bash
sudo shutdown -r +5
```
Cancel scheduled shutdown|reboot sequence.
```bash
sudo shutdown -c
```

### TODO
Add logging capabilities.
