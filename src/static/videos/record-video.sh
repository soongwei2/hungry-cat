#!/bin/bash

ffmpeg -y -r 10 -i http://localhost:8080/dev/video0 -t 00:10:00 -c:v h264_omx $1.mp4