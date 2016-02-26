#!/bin/bash
STEP=300s
MKGRAPH=./mkgraph.sh

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
    $MKGRAPH
    # manage.py only works if you're in the same directory.
    cd $WWW
    source $WWW/env/bin/activate
    echo yes | $WWW/manage.py collectstatic
    deactivate
    cd -
}

while true; do
    update &
    sleep $STEP
done
