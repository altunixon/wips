#!/usr/bin/env bash

set -u -e
set -o pipefail
IFS=$'\r\n'

chat_id=$1
chat_cmd=""
file_ip="/tmp/myip_now.tmp"
temp_ip="$(mktemp /tmp/myip_now.XXXXXX)"

ip_now=$(myip | tee "$temp_ip")
if [ -f "$file_ip" ]; then
    ip_prv=$(cat "$file_ip")
else
    ip_prv="INIT"
    cp "$temp_ip" "$file_ip"
fi

if [ "$ip_now" == "$ip_prv" ]; then
    echo "PASS"
else
    if [ ${#ip_prv} -eq 0 ] || [ "$ip_prv" == "INIT" ]; then
        $chat_cmd --to "$chat_id" --msg "IP Changed:\nOLD: INIT\nNEW: $ip_now"
    else
        $chat_cmd --to "$chat_id" --msg "IP Changed:\nOLD: $ip_prv\nNEW: $ip_now"
    fi
    cat "$temp_ip" > "$file_ip"
fi

rm "$temp_ip"
unset IFS
