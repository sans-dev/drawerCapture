#!/bin/bash

mkdir -p "$HOME"/named_pipes # Create directory if it doesn't exist
mkfifo -m a+rw "$HOME"/named_pipes/drawercapture_host
echo "Opened pipe for container host communication"
# Run eval_pipe.sh in the background and capture its process ID (PID)
./eval_pipe.sh & 
eval_pipe_pid=$!
echo "Started pipe evaluation on host"
# Trap signal SIGTERM (sent when Docker container stops)
trap "kill -SIGTERM $eval_pipe_pid" TERM

echo "Starting app container"
# Start Docker Compose
MY_UID="$(id -u)" MY_GID="$(id -g)" docker compose up

# Remove the named pipe directory (after Docker Compose exits)
rm -r "$HOME"/named_pipes

echo "Docker Compose has finished. eval_pipe.sh should have exited gracefully." 