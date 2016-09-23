#!/bin/bash
network=cabsnet

cd "$(dirname $(dirname "${BASH_SOURCE[0]}"))"
docker build -t cabsinterface .
opts="--rm -v $PWD:/code -p 8080:80 --network=$network --net-alias interface"
if [ $# -gt 0 ]; then
    opts+=' -it'
fi
if ! docker network ls | grep -q $network; then
    docker network create --driver bridge $network
fi
docker run $opts cabsinterface "$@"
