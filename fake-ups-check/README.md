### USAGE
```bash
ups-ping.sh <IP_ADDR> <REPEAT_FOR> [<shutdown|reboot>]
```
ERROR_FILE: "/tmp/ups-ping.err" <br/>
Ping <IP_ADDR> with 4 package, if failed write a timestamped COUNT to ERROR_FILE <br/>
If REPEAT_FOR > 1, next run will check if ERROR_FILE's COUNT > REPEAT_FOR <br/>
Then run shutdown|reboot if true, write new COUNT value to ERROR_FILE <br/>
If REPEAT_FOR =< 1, run shutdown|reboot immediately. <br/>

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
