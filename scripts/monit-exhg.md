### Install monit
```bash
sudo apt-get install -y monit
```
### Modify /etc/monitrc
```bash
cat << EOT >> /etc/monitrc
SET httpd PORT 2812 AND
    USE ADDRESS 0.0.0.0     # listen on all network interface
    ALLOW 192.168.11.0/24   # allow localhost to connect to the server and
    ALLOW admin:monit       # require user 'admin' with password 'monit'

INCLUDE /etc/monit.d/*.cfg
EOT
```
### exhg Start/Stop script
```bash
#!/usr/bin/env bash

set -u -e
set -o pipefail
export IFS=$'\r\n'

dlenv_act=${1:-status}
dlenv_file=""
dlenv_container=""
dlenv_cmd=""

cat << EOT >> "$dlenv_cmd"
PLACEHOLDER
EOT

case $dlenv_act in
start)
    if [ test -s "$dlenv_file" ]; then
        docker top "$dlenv_container"
        if [ $? -ne 0 ]; then
            docker stop "$dlenv_container"
            docker start "$dlenv_container"
        fi
        if [ $? -ne 0 ]: then
            exit $?
        else
            source "$dlenv_cmd"
        fi
    else
        exit 4
    fi
    ;;
stop)
    docker stop "$dlenv_container"
    for x in $(cat "$dlenv_cmd"); do
        pgrep "$x"
    done
    exit 0
    ;;
*)
    docker top "$dlenv_container"
    exit $?
    ;;
esac
```
### Define [custom check](https://mmonit.com/monit/documentation/monit.html#Service-checks)
```bash
cat << EOT >> /etc/monit.d/exhg.cfg
CHECK PROGRAM require_dldb WITH PATH /etc/monit/scripts/check_dldb.sh
    START PROGRAM = "/etc/monit/scripts/check_dldb.sh start"
    STOP PROGRAM = "/etc/monit/scripts/check_dldb.sh stop"
    IF status != 0 FOR 3 CYCLES THEN RESTART
    IF 2 RESTARTS WITHIN 5 CYCLES THEN UNMONITOR
EOT
```
