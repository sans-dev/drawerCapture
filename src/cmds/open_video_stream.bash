#!bin/bash
# get camera name and usb port as user args 
# example: ./open_video_stream.bash --name fuji --port 001:004

# store user args in variables
args=("$@")
for ((i=0; i<${#args[@]}; i++)); do
    case ${args[i]} in
        --model) model=${args[i+1]};;
        --port) port=${args[i+1]};;
        --dir) dir=${args[i+1]};;
        --fs) r=${args[i+1]};;
    esac
done

gphoto2 --set-config movie=1 --stdout --capture-movie --camera $model --port $port --set-config liveviewsize=0 | ffmpeg -i - -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 -s:v 1024x780 -r $r $dir