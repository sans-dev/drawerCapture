#!bin/bash

# store arguments for image dir and name
IMAGE_DIR=$1
IMAGE_NAME=$2
echo "Capturing image to $IMAGE_DIR/$IMAGE_NAME"
# capture image and download to image dir with full resolution
gphoto2 --set-config imageformat=3 --capture-image-and-download --filename $IMAGE_DIR/$IMAGE_NAME --force-overwrite