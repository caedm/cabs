#!/bin/bash
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"
network=cabsnet

docker build -t cabsagent .
if ! docker network ls | grep -q $network; then
    docker network create --driver bridge $network
fi

start_agent() {
    alias=$1
    user=$2
    docker run --network=$network --net-alias $alias \
          --hostname $alias --name $alias -d \
          cabsagent
    echo "'$alias' started with user '$user'"
}

start_agent agentk user1
start_agent agentj ''
while true; do
    echo -n "Type 'quit' to kill agents: "
    read response
    [ "$response" = quit ] && break;
done
docker kill agentk agentj > /dev/null
docker rm agentk agentj > /dev/null
