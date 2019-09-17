#!/bin/bash
step=1
for (( i = 0; i < 60; i=(i+step) )); do
    $(curl localhost:8000/watcher)
    sleep $step
done
exit 0