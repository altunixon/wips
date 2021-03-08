#!/usr/bin/env bash

set -u
set -o pipefail
set -o noclobber

# ec2=$(aws --profile alt_839700910164 ec2 describe-instances --filters "Name=tag:Name,Values=rtunnel" | jq -s -r '.[] | .Reservations[] | .Instances[] | .NetworkInterfaces[] | .Association | .PublicDnsName')
# ssh -o StrictHostKeyChecking=no -i /home/alt/Keys/aws-rtunnel.pem -f -N -T -R2222:localhost:22 "ec2-user@$ec2"

ec_profile='xxx'
ec_search="Name=tag:Name,Values=xxx"
ec_pidfile="/tmp/ec2-rtunnel.pid"
ec_user="xxx"
ec_sshkey="xxx"
ec_sshport=22
ec_sshopts=(-p $ec_sshport -f -N -o StrictHostKeyChecking=no -i $ec_sshkey -T -R2222:localhost:22)

# ec_hostfile="/tmp/ec2-publicdns.txt"
# [ -f "$ec_hostfile" ] && rm "$ec_hostfile"
ec_hostname=$(/usr/local/bin/aws --profile $ec_profile ec2 describe-instances --filters "$ec_search" | /usr/bin/jq -s -r '.[]|.Reservations[]|.Instances[]|.NetworkInterfaces[]|.Association|.PublicDnsName')
#ec_hostname=$(cat "$ec_hostname")

function ec_check() {
    echo -n "$(date) [#PID] "
    if [ ! -f "$ec_pidfile" ]; then
        echo -n "$(date) [CHCK] Hostname: ($ec_hostname)"
        if [ -z $ec_hostname ] || [ "$ec_hostname" == "null" ]; then
            ec_stat='host-fail'
        else
            echo -n "$(date) [CHCK] Port: "
            nc -z -v -w10 $ec_hostname $ec_sshport
            if [ $? -eq 0 ]; then
                ec_stat='available'
            else
                ec_stat='port-fail'
            fi
        fi
    else
        ssh_pid=$(cat $ec_pidfile)
        echo "$(date) [CHCK] Session Exists: $ec_pidfile ($ssh_pid)"
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
    ec_creds="${ec_user}@${ec_hostname}"
    # ssh ${ec_sshopts[@]} "ec2-user@$(cat $ec_hostfile)"
    ssh ${ec_sshopts[@]} "$ec_creds"
    ps aux | grep "$ec_creds" | grep ssh | awk '{print $2}' > "$ec_pidfile"
    ec_current=$(ps -p $(cat $ec_pidfile) -o command=)
    echo "$(date) [DONE] Session Started: $ec_current"
}

function ec_kill() {
    kill -9 $(cat $ec_pidfile)
    rm "$ec_pidfile"
    echo "$(date) [KILL] Session Killed"
}

ec_act=${1:-status}
echo "$(date) [INIT] Connection: ${ec_user}@${ec_hostname}:${ec_sshport}"
ec_stat='pre-flight'
ec_check
case $ec_stat in
    *fail)
        echo "$(date) [CHCK] Failed: ${ec_stat}"
        echo "$(date) [SKIP] Action: ${ec_act} (${ec_stat})"
    ;;
    *)
        case $ec_act in
            start)
                case $ec_stat in
                    available)
                        ec_connect
                    ;;
                    sshtun-zombie)
                        ec_kill
                        ec_connect
                    ;;
                    *)
                        echo "$(date) [CHCK] Status: ${ec_stat}"
                    ;;
                esac
            ;;
            restart)
                ec_kill
                ec_connect
            ;;
            stop)
                ec_kill
            ;;
            *)
                echo "$(date) [CHCK] Status: ${ec_stat}"
            ;;
        esac
    ;;
esac
echo "$(date) [FIN#] ${ec_act} (${ec_stat})"
