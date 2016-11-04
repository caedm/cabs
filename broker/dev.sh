#!/bin/bash
network=cabsnet

cd "$(dirname "${BASH_SOURCE[0]}")"
docker build -t cabsbroker .
if ! docker network ls | grep -q $network; then
    docker network create --driver bridge $network
fi
docker run --rm -it -v $PWD:/code -p 18181:18181 -p 18183:18183 \
    --network=$network --net-alias broker --name broker cabsbroker
