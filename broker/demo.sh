#!/bin/bash
network=cabsnet

cd "$(dirname "${BASH_SOURCE[0]}")"
docker build -t cabsbroker .
opts="--rm -v $PWD:/code -p 18181:18181 -p 18183:18183 --network=$network --net-alias broker"
if [ $# -gt 0 ]; then
    opts+=' -it'
fi
if ! docker network ls | grep -q $network; then
    docker network create --driver bridge $network
fi
docker run $opts cabsbroker "$@"
