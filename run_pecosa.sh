#!/bin/bash

java_pid=$(pidof java)

python3 ./pecosa.py ./data/2/log.txt $java_pid