#!/bin/bash

java_pid=$(pidof java)

python3 ./pecosa.py ./log.txt $java_pid