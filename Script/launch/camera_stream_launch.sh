#!/usr/bin/env bash
if ps a | grep 'testOnDemandRTSPServer' | grep -v grep
then
    echo "RTSPServer has been started."
    pid=$(pgrep -f 'testOnDemandRTSPServer')
else
    /home/jingzhe/live/testProgs/testOnDemandRTSPServer &
    pid=$!
fi
trap "kill $pid" EXIT
raspivid -o /tmp/rpicam -t 0 -fl -fps 10 -n &
sleep 3s
echo "start live555 rtsp://192.168.0.249:8554/liv0"
echo "pid $pid"
echo "capture video stream."
while :
do
    sleep 1m
done