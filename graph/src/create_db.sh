#!/bin/bash
cd "$(dirname "${BASH_SOURCE[0]}")"
source ./mkgraph_lib.sh
DIR="./db"
mkdir -p "$DIR"
for pool in ${POOLS[@]}; do
    dest="$DIR/${pool}.rrd"
    if [ -e "$dest" ]; then
        echo skipping "$dest": already exists
        continue
    fi
    rrdtool create "$dest" \
        DS:users:GAUGE:600:0:U \
        DS:active:GAUGE:600:0:U \
        DS:available:GAUGE:600:0:U \
        $(get_rra MAX) \
        $(get_rra MIN) \
        $(get_rra AVERAGE)
done
