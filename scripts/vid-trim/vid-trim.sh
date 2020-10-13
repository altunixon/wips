#!/usr/bin/env bash

set -u -e
set -o noclobber
set -o pipefail

IFS=$'\r\n'
path_out=${1:-}
path_temp="/media/alt/ramdisk1"
temp_img="${path_temp}/screenshot-trim.jpg"
trim_fuzz="5%"
msg_usage="Usage:\n\t$0 <path_out> [video_files]\nWorkDir: '$path_temp'"

function dimensions() {
    ss_file=${1:-}
    ss_retv=${2:-both}
    ss_tmpf=${3:-$temp_res}
    ss_dimensions=$(identify "$temp_img" | awk '{print $3}')
    fi
    case $ss_retv in
        w) echo -n "$ss_dimensions" | cut -d 'x' -f 1 ;;
        h) echo -n "$ss_dimensions" | awk -d 'x' -f 2 ;;
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
        vid_res=$(dimensions "$temp_img")
        vid_w=$(echo "$vid_res" | cut -d 'x' -f 1)
        vid_h=$(echo "$vid_res" | cut -d 'x' -f 2)
        # begin the screenshot trimming process, starting with adding right stripes to screenshot
        # mogrify -gravity East -background green -splice 5x0 -background red -splice 5x0 "$temp_img"
        # Trim Left(West)
        mogrify -gravity East -background green -splice 5x0 -background red -splice 5x0 -trim -fuzz $trim_fuzz -chop 5x0 "$temp_img"
        ss_geo_w1=$(dimensions "$temp_img" w)
        ss_geo_x1=$((vid_w - ss_geo_w1))
        # Trim Right(East), prevent trim north, south
        mogrify -gravity West -background green -splice 5x0 -trim -fuzz $trim_fuzz "$temp_img"
        # mogrify -trim -fuzz $trim_fuzz "$temp_img"
        # ss_geo_w2=$(dimensions "$temp_img" w)
        # ss_geo_x2=$((ss_geo_x1 + ss_geo_w2))
        # Trim North
        mogrify -gravity South -background green -splice 5x0 -trim -fuzz $trim_fuzz "$temp_img"
        ss_geo_h1=$(dimensions "$temp_img" h)
        ss_geo_y1=$((vid_h - ss_geo_h1))
        # Trim South
        mogrify -trim -fuzz $trim_fuzz "$temp_img"
        # ss_geo_h2=$(dimensions "$temp_img" h)
        # ss_geo_y2=$((ss_geo_y1 + ss_geo_h2))
        crop_size=$(dimensions "$temp_img")
        crop_w=$(echo "$crop_size" | cut -d 'x' -f 1)
        crop_h=$(echo "$crop_size" | cut -d 'x' -f 2)
        # ffmpeg crop format: upper left coordinates x:y => crop area dimensions w:h
        crop_area="crop=${ss_geo_x1}:${ss_geo_y1}:${crop_w}:${crop_h}"
        # Trim screenshot img
        # mogrify -trim -fuzz $trim_fuzz "$temp_img"
        # Detect final dimensions
        # ss_geo=$(identify "$temp_img" | awk '{print $3}')
        # ss_w=$(echo "$ss_geo" | awk -F 'x' '{print $1}')
        # ss_h=$(echo "$ss_geo" | awk -F 'x' '{print $2}')
        # Crop video to final dimensions
        echo -e "Trim: '$v_base' [$vid_res] => [$crop_area]"
        # ffmpeg -i "$temp_vid" -filter:v "crop=$ss_w:$ss_h" -c:a copy "$v_out"
        ffmpeg -hide_banner -i "$temp_vid" -vf "$crop_area" "$v_out"
        # Cleanup temp files
        rm "$temp_img" "$temp_vid"
    done
fi

# For Filename
# echo "a.b.c.txt" | rev | cut -d"." -f2-  | rev
# For extension
# echo "a.b.c.txt" | rev | cut -d"." -f1  | rev
