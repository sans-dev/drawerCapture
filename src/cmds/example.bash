#!bin/bash

# catch kwargs 
args=( "$@" )
for ((i=0; i<${#args[@]}; i++)); do
    case ${args[i]} in
        --camera_name) MODEL=${args[i+1]};;
        --port) PORT=${args[i+1]};;
    esac
done

# echo all kwargs line by line
echo "MODEL: $MODEL"
echo "PORT: $PORT"