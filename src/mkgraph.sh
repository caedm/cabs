#!/bin/bash
source ./mkgraph_lib.sh
LENGTHS=(12h 1d 7d 1M 1y 3y)

for length in ${LENGTHS[@]}; do
    for pool in ${POOLS[@]}; do
        mkgraph $length $pool 
    done
    for title in "${!AGGREGATE[@]}"; do
        mk_aggregate_graph $length "$title" ${AGGREGATE[$title]}
    done
    #mk_aggregate_graph $length "All Windows" OffCampusWindows OnCampusWIndows
    #mk_aggregate_graph $length "All Linux" RGSLinux RGSOffCampusLinux
    #mk_aggregate_graph $length "All pools" ${POOLS[@]}
done
