#!/usr/bin/env bash

set -ue
set -o noclobber

IFS=$"\r\n"
help_msg="$0 <pack|unpack>"

list_configs=(
"samba|/etc/samba/smbd|smb.conf"
"firewalld|/etc/firewalld|"
"sshd|/etc/sshd|sshd.conf"
"keys|$HOME/.ssh|id_rsa;id_rsa.pub;authorized_keys"
"transmission|$HOME/.config/transmission_daemon|"
"mounts|$HOME/.config|mount_list.conf"
"bashrc|$HOME|.bashrc;.bash_profile;.bash_aliases"
"vim|$HOME/.vimrc|"
)

for line_config in ${list_configs[@]}; do
    file_for=$(echo "$line_config" | cut -d '|' -f 1)
    file_src=$(echo "$line_config" | cut -d '|' -f 2)
    file_names=$(echo "$line_config" | cut -d '|' -f 3)
    IFS=';' read -ra file_list <<< "$file_names"
    echo -e "Service: [$file_for]\nSRC: $file_src\nFiles:\n"
    for file_n in ${file_list[@]}; do
        echo -e "\t${file_n}\n"
    done
done
