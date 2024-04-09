#!bin/bash

# imageformat for gphoto2 : 0=raw, 1=jpeg
# configure settings for capture: --set-config name=value - This will set the configuration of name to value
args=( "$@" )

DEBUG="false"
for ((i=0; i<${#args[@]}; i++)); do
    case ${args[i]} in
        --image_dir) IMAGE_DIR=${args[i+1]};;
        --image_name) IMAGE_NAME=${args[i+1]};;
        --image_format) IMAGE_FORMAT=${args[i+1]};;
        --model) MODEL=${args[i+1]};;
        --port) PORT=${args[i+1]};;
        --debug) DEBUG=${args[i+1]};;

    esac
done
#create file name from IMAGE_DIR and IMAGE_NAME and IMAGE_FORMAT
FILE_NAME="$IMAGE_DIR/$IMAGE_NAME$IMAGE_FORMAT"

# capture image and download to image dir with full resolution
# check if debug is enabled
if [ $DEBUG == "true" ]; then
    DEBUG_LOGFILE="logs/$IMAGE_NAME-capture.log"
    echo "DEBUG_LOGFILE: $DEBUG_LOGFILE"
    gphoto2 --set-config movie=0 --set-config imageformat=1 --camera $MODEL --port $PORT --capture-image-and-download --filename $FILE_NAME --force-overwrite --debug --debug-logfile=$DEBUG_LOGFILE
    else
    gphoto2 --set-config movie=0 --camera $MODEL --port $PORT --capture-image-and-download --filename $FILE_NAME --force-overwrite
fi