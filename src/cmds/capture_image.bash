#!bin/bash

args=( "$@" )
for ((i=0; i<${#args[@]}; i++)); do
    case ${args[i]} in
        --image_dir) IMAGE_DIR=${args[i+1]};;
        --image_name) IMAGE_NAME=${args[i+1]};;
        --image_format) IMAGE_FORMAT=${args[i+1]};;
        --camera_name) MODEL=${args[i+1]};;
        --port) PORT=${args[i+1]};;
        --image_quality) IMAGE_QUALITY=${args[i+1]};;
        --debug) DEBUG=${args[i+1]};;

    esac
done
#create file name from IMAGE_DIR and IMAGE_NAME and IMAGE_FORMAT
FILE_NAME="$IMAGE_DIR/$IMAGE_NAME$IMAGE_FORMAT"
echo "MODEL: $MODEL"
echo "PORT: $PORT"

echo "Capturing image to $FILE_NAME"
echo "DEBUG: $DEBUG"

# capture image and download to image dir with full resolution
# check if debug is enabled
if [ $DEBUG == "true" ]; then
    gphoto2 --camera $MODEL --port $PORT --set-config imageformat=$IMAGE_QUALITY --capture-image-and-download --filename $FILE_NAME --force-overwrite --debug --debug-logfile=logs/capture.log
    else
    gphoto2 --camera $MODEL --port $PORT --set-config imageformat=$IMAGE_QUALITY --capture-image-and-download --filename $FILE_NAME --force-overwrite
fi