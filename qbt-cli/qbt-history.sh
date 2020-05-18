#!/usr/bin/env bash

IFS=$'\r\n'
path_mapfile="/home/alt/git-repo/txt-lists/trem-maps.txt"
qbt_api="http://127.0.0.1:9090"
qbt_recycle="/tmp/recyclebin/trem"
qbt_exec=('qbt-cli.py' '--api' "$qbt_api" '--recyclebin' "$qbt_recycle")
msg_help="Usage:\n\t$0 <ls> [keyword]\n\t$0 <add> <dest> <keyword>\n\t$0 <replay|autoplay> <keyword>"

function warning_empty() {
    if [ -z $3 ]; then
        echo -e "Should not try running [$1] with Empty $2"
        echo -e "$msg_help"
        exit 10
    fi
}

qbt_mode=${1:-ls}

echo -e "START [$qbt_mode]"
case $qbt_mode in
    ls)
        qbt_key=${2:-}
        if [ -z $qbt_key ]; then
            for x in $(cat "$path_mapfile"); do
                echo "$x" | awk -F '|' '{print "qbt-cli.py --output \""$2"\" --start *"$1"*"}'
            done
        else
            grep "$qbt_key" "$path_mapfile" | awk -F '|' -v qbt="${qbt_alias[@]}" '{print qbt" \""$2"\" *"$1"*"}'
        fi
    ;;
    add)
        qbt_dest=${2:-}
        warning_empty "$qbt_mode" "DEST" "$qbt_dest"
        qbt_key=${3:-}
        warning_empty "$qbt_mode" "KEY" "$qbt_key"
        if [ $(grep "${qbt_key}" $path_mapfile | wc -l) -gt 0 ]; then
            # probly should check for multiple match, grep -m 1 will have to do for now
            qbt_map=$(grep -m 1 "$qbt_key" "$path_mapfile")
            mapd_key=$(echo "$qbt_map" | awk -F '|' '{print $1}')
            mapd_dst=$(echo "$qbt_map" | awk -F '|' '{print $2}')
            echo "Found Mapping: '$mapd_key' => '$mapd_dst'"
            if [ "${qbt_dest%%/}" != "${mapd_dst%%/}" ]; then
                replace_dst=$(read -p "Mapped DST != INPUT, Use That instead? [y/n]> " -n 1 -r)
                case $replace_dst in
                    y|Y)
                        echo -e "Swapping DST '$qbt_dest' > '$mapd_dst'"
                        qbt_dest="$mapd_dst"
                        qbt_key="$mapd_key"
                    ;;
                    *)
                        echo -e "Ignore Mapped Match, Staying with '$qbt_dest'"
                        # Update mapfile with new keyword&path
                        sed -i "/^$mapd_key/d" "$path_mapfile"
                        echo -e "${qbt_key}|${qbt_dest}\n" >> $path_mapfile
                    ;;
                esac
            fi
        else
            echo -e "${qbt_key}|${qbt_dest}\n" >> $path_mapfile
        fi
        # Add torrent
        ${qbt_exec[@]} --output "${qbt_dest}" --start ./*"${qbt_key}"*
    ;;
    replay)
        qbt_key=${2:-}
        warning_empty "$qbt_mode" "KEY" "$qbt_key"
        qbt_maps=($(grep "${qbt_key}" "$path_mapfile"))
        if [ ${#qbt_maps[@]} -gt 1 ]; then
            qbt_li=$((${#qbt_maps[@]} - 1))
            echo -e "Multiple [$qbt_key] Match:"
            for map_ln in $(seq 0 $qbt_li); do
                # ??? might be wrong
                echo -e "[$map_ln]: '${qbt_maps[map_ln]}'"
            done
            read -p "Choose [0-${qbt_li}] to continue: " map_choice
            case $map_choice in
                [0-9]*) qbt_map_chosen="${qbt_maps[map_choice]}";;
                *) qbt_map_chosen="${qbt_maps[0]}";;
            esac
        else
            qbt_map_chosen="${qbt_maps[@]}"
        fi
        qbt_key=$(echo "$qbt_map_chosen" | awk -F '|' '{print $1}')
        qbt_dest=$(echo "$qbt_map_chosen" | awk -F '|' '{print $2}')
        ${qbt_exec[@]} --output "${qbt_dest}" --start ./*"${qbt_key}"*
    ;;
    autoplay)
        qbt_src=${2:-'./'}
        for map_line in $(cat "$path_mapfile"); do
            qbt_key=$(echo "$map_line" | awk -F '|' '{print $1}')
            qbt_dest=$(echo "$map_line" | awk -F '|' '{print $2}')
            ${qbt_exec[@]} --output "${qbt_dest}" --start ./*"${qbt_key}"*
        done
    ;;
    *)
        echo -e "$msg_help"
    ;;
esac
echo -e "FINISH [$qbt_mode]"
