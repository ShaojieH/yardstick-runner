#!/bin/bash

java_pid=$(pidof java)

python3 ./pecosa.py ./data/5/log.txt $java_pid