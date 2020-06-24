#!/usr/bin/env bash

IFS=$'\r\n'
path_mapfile="/home/alt/git-repo/txt-lists/trem-maps.txt"
trem_alias=("/home/alt/bin-sh/trem-add" "normal")
trem_recycle="/tmp/recyclebin/trem"
msg_help="Usage:\n\t$0 <ls> [keyword]\n\t$0 <add> <dest> <keyword>\n\t$0 <replay|autoplay> <keyword>"
[ ! -d "$trem_recycle" ] && mkdir -p "$trem_recycle"

function warning_empty() {
    if [ -z $3 ]; then
        echo -e "Should not try running [$1] with Empty $2"
        echo -e "$msg_help"
        exit 10
    fi
}

function recycle_torrent() {
    if [ -d "$trem_recycle" ]; then
        mv -f ./*"${1}"* "${trem_recycle%%/}/"
    else
        echo -e "RecycleBin: '${trem_recycle}'\nMaybe cleanup by hand?: rm ./*\"${1}\"*"
        # rm ./*"${1}"*
    fi
}

trem_mode=${1:-ls}

echo -e "START [$trem_mode]"
case $trem_mode in
    ls)
        trem_key=${2:-}
        if [ -z $trem_key ]; then
            for x in $(cat "$path_mapfile"); do
                echo "$x" | awk -F '|' '{print "trem \""$2"\" *"$1"*"}'
            done
        else
            grep "$trem_key" "$path_mapfile" | awk -F '|' -v trem="${trem_alias[@]}" '{print trem" \""$2"\" *"$1"*"}'
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
                        echo -e "${trem_key}|${trem_dst}\n" >> $path_mapfile
                    ;;
                esac
            fi*:wq******
        else
            echo -e "${trem_key}|${trem_dst}\n" >> $path_mapfile
        fi
        # Add torrent
        ${trem_alias[@]} "${trem_dst}" ./*"${trem_key}"*
        [ $? -eq 0 ] && recycle_torrent "${trem_key}" || echo -e "[ERRO] ADD '$trem_key' to '$trem_dst' Failed"
    ;;
    replay)
        trem_key=${2:-}
        warning_empty $trem_mode "KEY" $trem_key
        trem_maps=($(grep "${trem_key}" "$path_mapfile"))
        if [ ${#trem_maps[@]} -gt 1 ]; then
            grep -n "${trem_key}" "$path_mapfile"
            trem_li=$((${#trem_maps[@]} - 1))
            echo -e "Multiple [$trem_key] Match:"
            for map_ln in $(seq 0 $trem_li); do
                # ??? might be wrong
                echo -e "[$map_ln]: '${trem_maps[map_ln]}'"
            done
            read -p "Choose [0-${trem_li}], Default [0]: " map_choice
            case $map_choice in
                [0-9]*) trem_map_chosen="${trem_maps[map_choice]}";;
                *) trem_map_chosen="${trem_maps[0]}";;
            esac
        else
            trem_map_chosen="${trem_maps[@]}"
        fi
        trem_key=$(echo "$trem_map_chosen" | awk -F '|' '{print $1}')
        trem_dst=$(echo "$trem_map_chosen" | awk -F '|' '{print $2}')
        ${trem_alias[@]} "${trem_dst}" ./*"${trem_key}"*
        [ $? -eq 0 ] && recycle_torrent "${trem_key}" || echo -e "[ERRO] REPLAY '$trem_key' Failed"
    ;;
    autoplay)
        trem_src=${2:-'./'}
        for map_line in $(cat "$path_mapfile"); do
            trem_key=$(echo "$map_line" | awk -F '|' '{print $1}')
            trem_dst=$(echo "$map_line" | awk -F '|' '{print $2}')
            ${trem_alias[@]} "${trem_dst}" ./*${trem_key}*
            [ $? -eq 0 ] && recycle_torrent "${trem_key}" || echo -e "[ERRO] AUTOPLAY Failed"
        done
    ;;
    *)
        echo -e "$msg_help"
    ;;
esac
echo -e "FINISH [$trem_mode]"
