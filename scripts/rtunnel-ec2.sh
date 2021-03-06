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
ec_sshkey="xxx"
ec_sshport=22
ec_sshopts=(-p $ec_sshport -f -N -o StrictHostKeyChecking=no -i $ec_sshkey -T -R2222:localhost:22)

[ -f "$ec_hostfile" ] && rm "$ec_hostfile"
/usr/local/bin/aws --profile $ec_profile ec2 describe-instances --filters "$ec_search" | /usr/bin/jq -s -r '.[]|.Reservations[]|.Instances[]|.NetworkInterfaces[]|.Association|.PublicDnsName' > "$ec_hostfile"

function ec_check() {
    if [ ! -f "$ec_pidfile" ]; then
        ec_hostname=$(cat "$ec_hostfile")
        if [ -z $ec_hostname ] || [ "$ec_hostname" == "null" ]; then
            ec_stat='off'
        else
            echo -n "$(date) [PORT] "
            nc -z -v -w10 $ec_hostname $ec_sshport
            [ $? -eq 0 ] && ec_stat='ok' || ec_stat='fail'
        fi
    else
        echo -n "$(date) [#PID] "
        ps -p $(cat $ec_pidfile) -o command=
        if [ $? -eq 0 ]; then
            ec_stat='on'
        else
            ec_stat='broken'
        fi
    fi
}

function ec_connect() {
    ec_creds="ec2-user@$(cat $ec_hostfile)"
    # ssh ${ec_sshopts[@]} "ec2-user@$(cat $ec_hostfile)"
    ssh ${ec_sshopts[@]} "$ec_creds"
    ps aux | grep "$ec_creds" | grep ssh | awk '{print $2}' > "$ec_pidfile"
}

function ec_kill() {
    kill -9 $(cat $ec_pidfile)
    rm "$ec_pidfile"
    rm "$ec_hostfile"
}

ec_act=${1:-auto}
ec_stat='preflight'
ec_check
case $ec_stat in
    fail|off)
        echo -e "$(date) [ERRO] Check: ${ec_stat}, HostName: ($(cat $ec_hostfile))"
    ;;
    *)
        echo "$(date) [CHCK] Status: $ec_stat"
        case $ec_act in
            auto|start)
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
