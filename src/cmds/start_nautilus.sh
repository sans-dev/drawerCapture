#!/bin/bash

# Get the directory path from the argument
directory="$1"

# Construct the command
command="echo \"nautilus $directory\" > /hostpipe/drawercapture_host"

# Execute the command
eval "$command"