#!/usr/bin/env bash

set -u -e

IFS=$'\r\n'
check_act=${1:-halp}
check_addr=${2:-}
check_recovery=${3:-}
check_log="/tmp/connection-status.log"
act_inb4=""
act_wait=3
check_internet="https://www.google.com/"

help_msg="Usage:\n\t$0 <shutdown|reboot> <ip_address|internet|gateway>\n"


function logger() {
    log_msg=${1:-INTENTIONALLY_LEFT_BLANK}
    echo "$(date) $log_msg" | tee -a "$check_log"
}

function act_do() {
    check_res=${1:-}
    if [ ! -z $check_res ] && [ $check_res -ne 0 ]; then
        logger "[ERRO] Check connection to [$check_addr] Failed (Exit=${check_res}), next action: [$check_act]"
        if [ ! -z "$act_inb4" ]; then
            logger "[INFO] Inb4 [$check_act]: '$act_inb4'"
            $act_inb4
        fi
        case $check_act in
            shutdown|halt)
                logger "[INFO] Action [$check_act] will be performed in the next $act_wait minutes."
                sudo /sbin/shutdown -P "+${act_wait}"
            ;;
            reboot|restart)
                logger "[INFO] Action [$check_act] will be performed in the next $act_wait minutes."
                sudo /sbin/shutdown -r "+${act_wait}"
            ;;
            *)
                echo -e "Unknown Action [${check_act}]\n${help_msg}"
                exit 1
            ;;
        esac
    else
        logger "[INFO] Check connection to [$check_addr] Successful (Exit=${check_res}), skip action: [$check_act]"
    fi
}

fucntion act_delay() {
    check_cmd=${1:-}
    if [ ! -z $check_cmd ]; then
        $check_cmd
        check_exit=$?
    else
        echo -e "Invalid check CMD [${check_cmd}]\n${help_msg}"
        exit 3
    fi
    case $check_recovery in
        y|Y|yes|Yes)
            sleep $(($act_wait * 120))
            $check_cmd
            act_do $?
        ;;
        *)
            act_do $check_exit
        ;;
    esac
}

case $check_addr in
    [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})
        act_delay "ping -c 4 $check_addr &> /dev/null"
        # ping -c 4 $check_addr &> /dev/null
        # act_do $?
    ;;
    gateway|gw)
        check_gw=$(ip -4 route list 0/0 | cut -d ' ' -f 3)
        act_delay "ping -c 4 $check_gw &> /dev/null"
        # ping -c 4 $check_gw &> /dev/null
        # act_do $?
    ;;
    internet)
        act_delay "wget -q --spider "$check_internet" &> /dev/null"
        # wget -q --spider "$check_internet" &> /dev/null
        # act_do $?
    ;;
    *)
        echo -e "Unknown destination [${check_act}]\n${help_msg}"
        exit 2
    ;;
esac
