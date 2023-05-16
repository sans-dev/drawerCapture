#!bin/bash

args=( "$@" )
for ((i=0; i<${#args[@]}; i++)); do
    case ${args[i]} in
        --image_dir) IMAGE_DIR=${args[i+1]};;
        --image_name) IMAGE_NAME=${args[i+1]};;
        --model) MODEL=${args[i+1]};;
        --port) PORT=${args[i+1]};;
        --debug) DEBUG=${args[i+1]};;
    esac
done

echo "MODEL: $MODEL"
echo "PORT: $PORT"
echo "Capturing image to $IMAGE_DIR/$IMAGE_NAME"
echo "DEBUG: $DEBUG"

# capture image and download to image dir with full resolution
# check if debug is enabled
if [ $DEBUG == "true" ]; then
    gphoto2 --camera $MODEL --port $PORT --set-config imageformat=0 --capture-image-and-download --filename $IMAGE_DIR/$IMAGE_NAME --force-overwrite --debug --debug-logfile=logs/capture.log
    else
    gphoto2 --camera $MODEL --port $PORT --set-config imageformat=0 --capture-image-and-download --filename $IMAGE_DIR/$IMAGE_NAME --force-overwrite
fi