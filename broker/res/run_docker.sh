#!/bin/bash

cd "$(dirname $(dirname "${BASH_SOURCE[0]}"))"
make
docker build -t cabsbroker .
docker run -it --rm -v $PWD:/code cabsbroker "$@"
