#!/bin/sh

for x in `seq 0 1`; do
    for y in `seq 0 1`; do
        python2 client.py $x $y &
    done
done
