#!bin/bash

# clean up any remaining gphoto2 processes
procs=($(pgrep -fla gphoto2))
# print content of procs
echo "procs: ${procs[@]}"

# iterate over procs, retrieve pid and kill it 
for proc in "${procs[@]}"; do
    echo "proc: $proc"
    kill -9 $(echo $proc | awk '{print $1}')
    break
done
