#!/usr/bin/env bash

set -u -e
set -o noclobber
set -o pipefail

IFS=$'\r\n'
path_out=${1:-}
path_temp="/media/alt/ramdisk1"
temp_img="${path_temp}/screenshot-trim.jpg"
temp_res="/tmp/screenshot-resolutions.txt"
trim_fuzz="5%"
msg_usage="Usage:\n\t$0 <path_out> [video_files]\nWorkDir: '$path_temp'"

function dimensions() {
    ss_file=${1:-}
    ss_retv=${2:-both}
    ss_tmpf=${3:-$temp_res}
    if [ -s "$ss_tmpf" ]; then
        ss_dimensions=$(cat "$ss_tmpf")
    else
        ss_dimensions=$(identify "$temp_img" | awk '{print $3}' | tee "$ss_tmpf")
    fi
    case $ss_retv in
        w) echo -n "$ss_dimensions" | awk -F 'x' '{print $1}';;
        h) echo -n "$ss_dimensions" | awk -F 'x' '{print $2}';;
        *) echo -n "$ss_dimensions"
    esac
}

if [ -z $path_out ] || [ $# -lt 2 ]; then
    echo -e "$msg_usage"
    exit 10
else
    for v_in in ${@:2}; do
        # Get file name and extension
        v_base=$(basename -- "$v_in")
        v_name="${v_base%.*}"
        v_ext="${v_base##*.}"
        v_out="${path_out%%/}/${v_name}-cropped.${v_ext}"
        # Copy original video to temp file, reduce disk usage, should probly disable for larger files
        temp_vid="${path_temp}/vid-in.${v_ext}"
        cp -rf "$v_in" "$temp_vid"

        # v_resolution=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$temp_vid")
        # Take screenshot
        ffmpeg -hide_banner -ss 00:00:30 -i "$temp_vid" -vframes 1 -q:v 5 "$temp_img"
        # Original dimensions
        vid_w=$(dimensions "$temp_img" w)
        vid_h=$(dimensions "$temp_img" h)
        # begin the screenshot trimming process, starting with adding right stripes to screenshot
        mogrify -gravity East -background green -splice 5x0 -background red -splice 5x0 "$temp_img"
        # Trim Left(West)
        mogrify -trim -fuzz $trim_fuzz "$temp_img"
        mogrify -gravity East -chop 5x0 "$temp_img"
        ss_geo_ww=$(dimensions "$temp_img" w "/tmp/screenshot-trim-w.txt")
        ss_geo_x1=$((vid_w - ss_geo_ww))
        # Trim Right(East)
        mogrify -gravity West -background green -splice 5x0 "$temp_img"
        mogrify -trim -fuzz $trim_fuzz "$temp_img"
        
        # Trim screenshot img
        mogrify -trim -fuzz $trim_fuzz "$temp_img"
        # Detect final dimensions
        ss_geo=$(identify "$temp_img" | awk '{print $3}')
        ss_w=$(echo "$ss_geo" | awk -F 'x' '{print $1}')
        ss_h=$(echo "$ss_geo" | awk -F 'x' '{print $2}')
        # Crop video to final dimensions
        echo -e "Trim: '$v_base' [$v_resolution] => [$ss_geo]"
        # ffmpeg -i "$temp_vid" -filter:v "crop=$ss_w:$ss_h" -c:a copy "$v_out"
        ffmpeg -hide_banner -i "$temp_vid" -vf "crop=$ss_w:$ss_h" "$v_out"
        # Cleanup temp files
        rm "$temp_img" "$temp_vid"
        [ -f "$temp_res" ] && rm "$temp_res" 
    done
fi

# For Filename
# echo "a.b.c.txt" | rev | cut -d"." -f2-  | rev
# For extension
# echo "a.b.c.txt" | rev | cut -d"." -f1  | rev
