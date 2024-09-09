#!/bin/bash

# Check for --local parameter
if [[ "$1" == "--local" ]]; then
  image_name="drawer-capture-app:dev"
else
  image_name="containerseb/drawer-capture-app:latest"
  docker image pull $image_name
fi

mkdir -p "$HOME"/named_pipes # Create directory if it doesn't exist
mkfifo -m a+rw "$HOME"/named_pipes/drawercapture_host
echo "Opened pipe for container host communication"
# Run eval_pipe.sh in the background and capture its process ID (PID)
while true; do eval "$(cat $HOME/named_pipes/drawercapture_host)"; done > /dev/null 2>&1 &
# ./eval_pipe.sh & 
eval_pipe_pid=$!
echo "Started pipe evaluation on host"
# Trap signal SIGTERM (sent when Docker container stops)
trap "kill -SIGTERM $eval_pipe_pid" TERM

echo "Starting app container"
# Remove any existing container with the same name
docker rm -f Drawer-Capture 2>/dev/null || true
# Run docker container
docker run \
  --name Drawer-Capture \
  --env DISPLAY=${DISPLAY} \
  --device /dev/bus/usb:/dev/bus/usb \
  --user 1000:1000 \
  --privileged \
  --volume /tmp/.X11-unix:/tmp/.X11-unix \
  --volume ${XAUTHORITY:-$HOME/.Xauthority}:/root/.Xauthority:rw \
  --volume /etc/passwd:/etc/passwd:ro \
  --volume /etc/group:/etc/group:ro \
  --volume $HOME:/$HOME:rw \
  --volume /dev:/dev \
  --volume $HOME/named_pipes/:/hostpipe \
  --network host \
  $image_name

# Remove the named pipe directory (after Docker Compose exits)
rm -r "$HOME"/named_pipes

echo "Docker Compose has finished. eval_pipe.sh should have exited gracefully." 