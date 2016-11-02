#!/bin/bash
network=cabsnet

cd "$(dirname "${BASH_SOURCE[0]}")"
docker build -t cabsinterface .
if ! docker network ls | grep -q $network; then
    docker network create --driver bridge $network
fi
docker run --rm -it -v $PWD:/code -p 8080:80 --network=$network \
           --net-alias interface cabsinterface "$@"
