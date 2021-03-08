#!/usr/bin/env bash

set -u
set -o pipefail
set -o noclobber

# ec2=$(aws --profile alt_839700910164 ec2 describe-instances --filters "Name=tag:Name,Values=rtunnel" | jq -s -r '.[] | .Reservations[] | .Instances[] | .NetworkInterfaces[] | .Association | .PublicDnsName')
# ssh -o StrictHostKeyChecking=no -i /home/alt/Keys/aws-rtunnel.pem -f -N -T -R2222:localhost:22 "ec2-user@$ec2"

ec_profile='xxx'
ec_search="Name=tag:Name,Values=xxx"
ec_hostfile="/tmp/ec2-publicdns.txt"
ec_pidfile="/tmp/ec2-rtunnel.pid"
ec_user="xxx"
ec_sshkey="xxx"
ec_sshport=22
ec_sshopts=(-p $ec_sshport -f -N -o StrictHostKeyChecking=no -i $ec_sshkey -T -R2222:localhost:22)

[ -f "$ec_hostfile" ] && rm "$ec_hostfile"
/usr/local/bin/aws --profile $ec_profile ec2 describe-instances --filters "$ec_search" | /usr/bin/jq -s -r '.[]|.Reservations[]|.Instances[]|.NetworkInterfaces[]|.Association|.PublicDnsName' > "$ec_hostfile"

function ec_check() {
    echo -n "$(date) [#PID] "
    if [ ! -f "$ec_pidfile" ]; then
        echo -n "$(date) [HOST] "
        if [ -z $ec_hostname ] || [ "$ec_hostname" == "null" ]; then
            ec_stat='host-fail'
        else
            echo -n "$(date) [PORT] "
            nc -z -v -w10 $ec_hostname $ec_sshport
            if [ $? -eq 0 ]; then
                ec_stat='ok'
            else
                ec_stat='port-fail'
            fi
        fi
    else
        ssh_pid=$(cat $ec_pidfile)
        echo "$ec_pidfile ($ssh_pid)"
        echo -n "$(date) [#CMD] "
        ps -p $(ssh_pid) -o command=
        if [ $? -eq 0 ]; then
            ec_stat='sshtun-active'
        else
            ec_stat='sshtun-zombie'
        fi
    fi
}

function ec_connect() {
    ec_creds="${ec_user}@$(cat $ec_hostfile)"
    # ssh ${ec_sshopts[@]} "ec2-user@$(cat $ec_hostfile)"
    ssh ${ec_sshopts[@]} "$ec_creds"
    ps aux | grep "$ec_creds" | grep ssh | awk '{print $2}' > "$ec_pidfile"
}

function ec_kill() {
    kill -9 $(cat $ec_pidfile)
    rm "$ec_pidfile"
    rm "$ec_hostfile"
}

ec_act=${1:-status}
ec_hostname=$(cat "$ec_hostfile")
echo "$(date) [INIT] Connection: ${ec_user}@${ec_hostfile}:${ec_sshport}"
ec_stat='preflight'
ec_check
case $ec_stat in
    fail|off)
        echo "$(date) [CHCK] Failed: ${ec_stat}"
    ;;
    *)
        echo "$(date) [CHCK] Status: ${ec_stat}"
        case $ec_act in
            start)
                case $ec_stat in
                    ok)
                        ec_connect
                        echo "$(date) [DONE] $ec_act"
                    ;;
                    broken)
                        ec_kill
                        ec_connect
                        echo "$(date) [DONE] Restart broken tunnel"
                    ;;
                    *)
                        echo "$(date) [SKIP] Action: $ec_act"
                    ;;
                esac
            ;;
            restart)
                ec_kill
                echo "$(date) [KILL] $ec_act"
                ec_connect
                echo "$(date) [STRT] $ec_act"
            ;;
            stop)
                ec_kill
                echo "$(date) [DONE] $ec_act"
            ;;
            *)
                echo "$(date) [HUH?] $0: $ec_act"
            ;;
        esac
    ;;
esac
