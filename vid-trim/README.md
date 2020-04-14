### ffmpeg take [screenshot] at 30 second mark
```bash
ffmpeg -ss 00:00:30 -i input -vframes 1 -q:v 5 /tmp/screenshot.jpg
```
#### Get [video resolution]
```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 input.mp4
```
### ImageMagick [trim] screen shot and detect crop [geometry]
```bash
mogrify -trim -fuzz 25% /tmp/screenshot.jpg
$ss_geo=$(magick identify /tmp/screenshot.jpg | awk '{print $3}')
$ss_w=$(echo "$ss_geo" | awk -F 'x' '{print $1}')
$ss_h=$(echo "$ss_geo" | awk -F 'x' '{print $2}')
```
### ffmpeg [crop video] (default from center) to final dimensions
```bash
ffmpeg -i input.mp4 -filter:v "crop=$ss_w:$ss_h" -c:a copy output.mp4
```
[screenshot]:https://trac.ffmpeg.org/wiki/Create%20a%20thumbnail%20image%20every%20X%20seconds%20of%20the%20video
[video resolution]:https://trac.ffmpeg.org/wiki/FFprobeTips
[trim]:http://www.imagemagick.org/Usage/crop/#trim_fuzz
[geometry]:https://imagemagick.org/script/identify.php
[crop video]:https://video.stackexchange.com/questions/4563/how-can-i-crop-a-video-with-ffmpeg
