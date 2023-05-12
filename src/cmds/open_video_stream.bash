#!bin/bash
gphoto2 --stdout --capture-movie --set-config liveviewsize=XGA | ffmpeg -i - -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video2