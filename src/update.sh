#!/bin/bash
STEP=300s

cd "$(dirname "${BASH_SOURCE[0]}")"
source ./mkgraph_lib.sh
source ./cabsgraph.conf

update () {
    logger -t cabsgraph "updating the CABS graphs"
    for pool in ${POOLS[@]}; do
        result="$(query_db "$pool")"
        users=$(echo "$result" | cut -f 1)
        machines=$(echo "$result" | cut -f 2)
        available=$(echo "$result" | cut -f 3)
        logger -t cabsgraph "\'$pool\' has $users users, $machines online and $available available"
        rrdtool update db/${pool}.rrd N:$users:$machines:$available
    done
    mk_all_graphs
    export_graphs
}

while true; do
    update &
    sleep $STEP
done
