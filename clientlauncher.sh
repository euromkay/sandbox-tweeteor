#!/bin/bash

for x in 0 1 2 3 4
do 
    for y in 0 1 2
    do
        ssh pi@tile-$x-$y "cd shared/sandbox-tweeteor; \
            DISPLAY=:0.0 nohup ./client.py $x $y >/dev/null 2>&1 &"
    done
done
