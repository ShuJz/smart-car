#!/usr/bin/env bash
echo 'Start slam sorket sever...'
/home/jingzhe/workspace/orb_python3/build/socket_slam /home/jingzhe/workspace/orb_python3/Vocabulary/ORBvoc.txt /home/jingzhe/workspace/orb_python3/src/TUM1.yaml &
pid=$!

trap "kill $pid" EXIT

sleep 20s

/home/jingzhe/workspace/socket_service/build/SocketClientMat
