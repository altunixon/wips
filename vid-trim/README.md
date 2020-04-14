# ffmpeg Take screenshot ar 30 second mark
ffmpeg -ss 00:00:30 -i input -vframes 1 -q:v 5 /tmp/screenshot.jpg
# Get video resolution
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 input.mp4

# ImageMagick trim screen shot and detect crop geometry
mogrify -trim -fuzz 25% /tmp/screenshot.jpg
$ss_geo=$(magick identify /tmp/screenshot.jpg | awk '{print $3}')
$ss_w=$(echo "$ss_geo" | awk -F 'x' '{print $1}')
$ss_h=$(echo "$ss_geo" | awk -F 'x' '{print $2}')

# Crop image (default from center) to final dimensions
# https://video.stackexchange.com/questions/4563/how-can-i-crop-a-video-with-ffmpeg
ffmpeg -i input.mp4 -filter:v "crop=$ss_w:$ss_h" -c:a copy output.mp4
