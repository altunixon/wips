#!/usr/bin/env bash

IFS=$'\r\n'
path_mapfile="mapfile.txt"

function warning_empty() {
    if [ -z $3 ]; then
        echo -e "Should not try running [$1] with Empty $2"
        exit 10
    fi
}

trem_mode=${1:-ls}

echo -e "START [$trem_mode]"
case $trem_mode in
    ls)
        trem_key=${2:-}
        if [ -z $trem_key ]; then
            for x in $(cat "$path_mapfile"); do
                echo "$x" | awk -F '|' '{print "trem \'"$2"\' *"$1"*"}'
            done
        else
            grep "$trem_key" "$path_mapfile" | awk -F '|' '{print "trem \'"$2"\' *"$1"*"}'
        fi
    ;;
    add)
        trem_dst=${2:-}
        warning_empty $trem_mode "DEST" $trem_dst
        trem_key=${3:-}
        warning_empty $trem_mode "KEY" $trem_key
        if [ $(grep "${trem_key}" $path_mapfile | wc -l) -gt 0 ]; then
            # probly should check for multiple match, single match will have to do for now
            trem_map=$(grep -m 1 "$trem_key" "$path_mapfile")
            mapd_key=$(echo "$trem_map" | awk -F '|' '{print $1}')
            mapd_dst=$(echo "$trem_map" | awk -F '|' '{print $2}')
            echo "Found Mapping: '$mapd_dst' <= '$mapd_key'"
            if [ "${trem_dst%%/}" != "${mapd_dst%%/}" ]; then
                replace_dst=$(read -p "Mapped DST != INPUT, Use That instead? [y/n]> " -n 1 -r)
                case $replace_dst in
                    y|Y)
                        echo -e "Swapping DST '$trem_dst' > '$mapd_dst'"
                        trem_dst="$mapd_dst"
                        trem_key="$mapd_key"
                    ;;
                    *)
                        echo -e "Ignore Mapped Match, Staying with '$trem_dst'"
                        # Update mapfile with new keyword&path
                        sed -i "/^$mapd_key/d" "$path_mapfile"
                        echo "${trem_key}|${trem_dst}" >> $path_mapfile
                    ;;
                esac
            fi
        else
            echo "${trem_key}|${trem_dst}" >> $path_mapfile
        fi
        # Add torrent
        trem "${trem_dst}" ./*${trem_key}*
    ;;
    replay)
        trem_key=${2:-}
        warning_empty $trem_mode "KEY" $trem_key
        trem_maps=($(grep "${trem_key}" "$path_mapfile"))
        if [ ${#trem_maps[@]} -gt 0 ]; then
            echo -e "Multiple [$trem_key] Match:"
            for map_line in $(seq 0 ${#trem_maps[@]}); do
                # ??? might be wrong
                echo -e "[$map_line]: '${trem_maps[mapline]}'"
            done
            read -p "Choose [0-${#trem_maps[@]}] to continue: " map_choice
            case $map_choice in
                [0-9]*) trem_map_chosen="${trem_maps[map_choice]}";;
                *) trem_map_chosen="${trem_maps[0]}";;
            esac
        else
            trem_map_chosen="${trem_maps[@]}"
        fi
        trem_key=$(echo "$trem_map_chosen" | awk -F '|' '{print $1}')
        trem_dst=$(echo "$trem_map_chosen" | awk -F '|' '{print $2}')
        trem "${trem_dst}" ./*${trem_key}*
    ;;
    autoplay)
        trem_src=${2:-'./'}
        for map_line in $(cat "$path_mapfile"); do
            trem_key=$(echo "$map_line" | awk -F '|' '{print $1}')
            trem_dst=$(echo "$map_line" | awk -F '|' '{print $2}')
            trem "${trem_dst}" ./*${trem_key}*
        done
    ;;
esac
echo -e "FINISH [$trem_mode]"
