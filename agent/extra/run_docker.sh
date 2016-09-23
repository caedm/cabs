#!/bin/bash
set -e
usage() {
    echo "Usage: $0 [-h <hostname>] [command]" 1>&2
    exit 1
}
    
network=cabsnet
alias=agentk
while getopts ":h" opt; do
    case "${opt}" in
        h)
            alias="${OPTARG}" ;;
        *)
            usage ;;
    esac
done
shift $((OPTIND - 1))

cd "$(dirname $(dirname "${BASH_SOURCE[0]}"))"
make
docker build -t cabsagent .
opts="--rm -v $PWD:/code --network=$network --net-alias $alias \
      --hostname $alias --name $alias"
if [ $# -gt 0 ]; then
    opts+=' -it'
fi
if ! docker network ls | grep -q $network; then
    docker network create --driver bridge $network
fi
docker run $opts cabsagent "$@"
