#!/usr/bin/env bash

# Strict mode, exit if there are unbound(undefined) Variables
set -u
set -o pipefail
# Debug exit on first error, safe to comment on production
# set -e
# set -vx
IFS=$'\r\n'

script_name=${0:-trem-add}
#transm_opts=('http://192.168.11.40:9091/transmission' '--auth' 'alt:efsf')
transm_opts=('--auth' 'alt:efsf')
transm_addok=0
transm_addfa=0

function trem-halp() {
    halp_case=${1:-halp}
    halp_usage="Usage: $script_name <torrent_type[add|all|ex*|eh*]> <output_folder> [input folders/files]"
    case $halp_case in
        h|help|halp)
            echo "[ INFO ] Not knowing what todo?"
        ;;
        missing|none|null)
            echo "[ERRO] Missing Argument(s)"
        ;;
        dir|path)
            echo "[WARN] Path not found"
        ;;
        error|err)
            echo "[ERRO] Broken Piece of Shiet"
        ;;
        *)
            echo "[ERRO] Help me i'm retarded [$halp_case]!"
        ;;
    esac
    echo -e "\t$halp_usage"
}

function trem-mkdp() {
    dir_path=${1:-}
    if [ -z "$dir_path" ]; then
        trem-halp 'dir'
        exit 1
    elif [ -d "$dir_path" ]; then
        echo "[INFO_] '$dir_path' Exists, Continuing..."
    else
        read -t 10 -p "Create '$dir_path' and retry? [y/n]:> " -n 1 wanna_retry
        wanna_retry=${wanna_retry:-n}
        echo " ($wanna_retry)"
        case $wanna_retry in
            y|Y|yes)
                mkdir -p "$dir_path"
                if [ $? -eq 0 ]; then
                    echo "[_OK_] Directory path '$dir_path' Created, continuing..."
                else
                    echo "[FAIL] '$dir_path' Could not be Created, Abort!"
                    exit 1
                fi
            ;;
            *)
                echo "[WARN] Please Create '$dir_path' manually and run this script again."
                exit 0
            ;;
        esac
    fi
}

function trem-add-all() {
torrent_out1=${1:-}
torrent_path1=${2:-}
if [ -z $torrent_path1 ] || [ -z $torrent_out1 ]; then
    echo "[DBUG] Src: '$torrent_path1' / Dst: '$torrent_out1'"
    trem-halp 'missing'
    exit 1
else
    if [ -f "$torrent_path1" ]; then
        echo -e "\t[INFO_] Adding '$torrent_path1'"
        /usr/bin/transmission-remote ${transm_opts[@]} --add --start-paused --download-dir "$torrent_out1" "$torrent_path1"
		[ $? -eq 0 ] && transm_addok=$((transm_addok + 1)) || transm_addfa=$((transm_addfa + 1))
        sleep 1
    elif [ -d "$torrent_path1" ]; then
        for t in $(find "$torrent_path1" -maxdepth 1 -type f -iname '*.torrent'); do
            echo -e "\t[INFO_] Adding '$t'"
            /usr/bin/transmission-remote ${transm_opts[@]} --add --start-paused --download-dir "$torrent_out1" "$t"
            [ $? -eq 0 ] && transm_addok=$((transm_addok + 1)) || transm_addfa=$((transm_addfa + 1))
            sleep 1
        done
    elif [[ "$torrent_path1" == *'://'* || "$torrent_path1" == 'magnet:'* ]]; then
        echo -e "\t[INFO_] Adding Link '$torrent_path1'"
        /usr/bin/transmission-remote ${transm_opts[@]} --add --start-paused --download-dir "$torrent_out1" "$torrent_path1"
        [ $? -eq 0 ] && transm_addok=$((transm_addok + 1)) || transm_addfa=$((transm_addfa + 1))
        sleep 1
    else
        ls -lah "$torrent_path1"
        trem-halp 'doh'
        exit 1
    fi
fi
}

function trem-add-exht() {
torrent_out2=${1:-}
torrent_path2=${2:-}
if [ -z $torrent_path2 ] || [ -z $torrent_out2 ]; then
    echo "[DEBUG] SRC: '$torrent_path2' / DST: '$torrent_out2'"
    trem-halp 'missing'
    exit 1
else
    if [ -f "$torrent_path2" ]; then
        echo -e "\t[INFO ] Adding '$torrent_path2'"
        /usr/bin/transmission-remote ${transm_opts[@]} --add --start-paused --download-dir "$torrent_out2" "$torrent_path2"
        sleep 1
    elif [ -d "$torrent_path2" ]; then
        for ex_dir in $(find "$torrent_path2" -maxdepth 1 -mindepth 1 -type d); do
            #ex_tag=$(echo "${ex_dir%/}" | awk -F '/' '{print $NF}')
			ex_tag=$(basename "${ex_dir%/}")
            torrent_dir="${torrent_out2%/}/$ex_tag"
            trem-mkdp "$torrent_dir"
            echo "[INFO ] Processing '$ex_dir' > '$torrent_dir'"
            for t in $(find "$torrent_path2" -maxdepth 1 -type f -iname '*1of*.torrent'); do
                echo -e "\t[INFO ] Adding '$t'"
                /usr/bin/transmission-remote ${transm_opts[@]} --add --start-paused --download-dir "$torrent_dir" "$t"
                sleep 1
            done
        done
    else
        ls -lah "$torrent_path2"
        trem-halp 'doh'
        exit 1
    fi
fi
}

function trem-add() {
case "${transm_opts[@]}" in
    *http:/*|*https:/*|*:9091*|*/trans*)
        trem_safe=0
        echo "[DBUG] Using Remote Server ${transm_opts[@]}"
    ;;
    *)
        systemctl status transmission-daemon.service &> /dev/null
        trem_safe=$?
        echo "[DBUG] Local Server: systemctl status transmission-daemon.service ($trem_safe)"
    ;;
esac

if [ $trem_safe -eq 0 ]; then
    torrent_type=${1:-}
    torrent_out0=${2:-}
    torrent_rest=${#}
    if [ $torrent_rest -lt 3 ]; then
        trem-halp 'missing'
        exit 1
    else
        echo "[START] Adding Torrents form [$((torrent_rest - 2))] Source(s)"
        trem-mkdp "$torrent_out0"
        case $torrent_type in
            all|add|normal)
                echo "[DEBUG] Adding All Torrent to '$torrent_out0'."
                for i in $(seq 3 $torrent_rest); do
                    trem-add-all "$torrent_out0" "${!i}"
                done
                echo "[DONE] Added [$transm_addok] Torrent(s) From [$((torrent_rest - 2))] Source(s)."
            ;;
            ex*|eh*)
                echo "[DBUG] Adding E[X/H] type to '$torrent_out0'."
                for i in $(seq 3 $torrent_rest); do
                    trem-add-exht "$torrent_out0" "${!i}"
                done
            ;;
            file|txt)
                if [ -f "$3" ]; then
                    echo "[DEBUG] Adding Torrents Link from File '$3' to '$torrent_out0'."
                    for i in $(cat $3); do
                        trem-add-all "$torrent_out0" "$i"
                    done
                else
                    echo "[ERROR] Torrent list file '$3' does not Exists."
                    exit 1
                fi
            ;;
            *)
                echo "[ERROR] Operation [$torrent_type] > '$torrent_out0' < [$torrent_rest] not supported."
                trem-halp 'halp'
                exit 1
            ;;
        esac
		exit $transm_addfa
    fi
else
    echo -e "[WARN_] Service 'transmission-daemon' is currently stopped, please follow the steps down below\n\t*1: Check '$STORAGE_DIR' Availability\n\t*2: Then start transmission-daemon.service accordingly"
	exit 1
fi
}

# [[ $SHELL == *'/bash' ]] && trem-add "$@" || echo "$0 is Written for Bash, yours is: [$SHELL]"
trem-add "$@"
unset IFS
