#!/bin/sh
maxX=`awk '/win_per_row/ {print $3 - 1}' < config`
maxY=`awk '/win_per_col/ {print $3 - 1}' < config`
for x in `seq 0 $maxX`; do
    for y in `seq 0 $maxY`; do
        python2 client.py $x $y &
    done
done
