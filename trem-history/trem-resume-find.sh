#!/usr/bin/env bash

set -u -e

trem_user=$USER
trem_rdir="/home/$trem_user/.config/transmission-daemon/resume"
trem_file=${1:-}
file_delim=","
# for all available fields, see: https://github.com/transmission/transmission/wiki/Transmission-Resume-Files
file_nodisp='bitfield\|ratio-mode\|up-mode\|down-mode\|use-speed-limit\|use-global-speed-limit\|ratio-limit\|peers2-6\|peers2\|max-peers'
help_msg="Usage:\n\t$0 <SEARCH_TEXT>\n"
msg_sep="[INFO] ==========================================="

if [ ! -z $trem_file ]; then
    resume_files=( $(ls -1 "${trem_rdir%/}/"*"$trem_file"*) )
    if [ ${#resume_files[@]} -gt 0 ]; then
        echo "$msg_sep"
        for n in ${!resume_files[@]}; do
            echo -e "[INFO] From file [$((n + 1))]: ${resume_files[$n]}"
            tr "$file_delim" '\n' "${resume_files[$n]}" | grep -v "$file_nodisp"
            echo "$msg_sep"
        done
    else
        echo "[WARN] Could not find '$trem_file' in '$trem_rdir'"
    fi
else
    echo -e "Couldn't search with an empty string\n$help_msg"
fi
