#### [Diego] solution
There are several options you can choose between. </br>
At my work we are using VLC to stream video captured by Raspberry Pi Camera from our server-rooms to the office. </br>
One downside of this is that there are about 5 seconds delay and I haven't found a solution to this. </br>
The following is our setup:
- Have raspbian installed, expand root partition and [enabled your camera], run:
  ```bash
  sudo raspi-config
  ```
  and choose _**Interfacing Options > Camera > Yes**_
- Update packages
  ```bash
  sudo apt-get update
  sudo apt-get upgrade
  ```
- Install vlc
  ```bash
  sudo apt-get install vlc
  ```
- Run the command.
  ```bash
  raspivid -o - -t 0 -hf -w 640 -h 360 -fps 25 | cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:6969}' :demux=h264
  ```
- To watch the videostream, open VLC on a computer on the same network as the raspberry pi you are using for streaming. </br>
  Press Media -> Open Networkstream and paste the following in the field: </br>
  rtsp://[IP].[TO].[THE].[PI]:6969/
- If you don't care about FPS (frames per second) and don't want any delay you could use [MJPEG]. </br>
  Read [THIS wiki] about Raspberry Pi Camera Module. </br>
  Hope you find what you're looking for.


The solution suggested by Diego is good except that it's pretty slow and has a huge video delay </br>
since the vlc there re-streams a stream of the raspvid. </br>
Since 12/2013 there is an **official [v4l2 driver]** available: 
```bash
sudo modprobe bcm2835-v4l2
cvlc v4l2:///dev/video0 \
    --v4l2-width 1920 --v4l2-height 1080 --v4l2-chroma h264 \
    --sout '#standard{access=http,mux=ts,dst=0.0.0.0:6969}'
```
This creates an http stream at port 6969, you can use other formats too, like the rtcp one from the Diego's answer.


[Diego]: https://raspberrypi.stackexchange.com/questions/23182/how-to-stream-video-from-raspberry-pi-camera-and-watch-it-live
[enabled your camera]: https://www.raspberrypi.org/documentation/usage/camera/
[v4l2 driver]: http://www.ics.com/blog/raspberry-pi-camera-module#.VJFhbyvF-b8
[MJPEG]: http://www.raspberrypi.org/forums/viewtopic.php?t=45178
[THIS wiki]: http://elinux.org/Rpi_Camera_Module
