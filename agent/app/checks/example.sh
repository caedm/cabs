#!/bin/bash

# make script executable, in linux -> ch kmod -x example.sh

# gets all pids associated with sshd. If none exist, prints out 'not running'.
# Then checks conections of each pid. If at least one connection is good, return 'Okay'. 
# If none pass, return 'not connected'

# make sure to output only 1 line which can either be:
# Okay | not connected | not found | not running

pids=($(pgrep sshd))

length=${#pids[@]}
if [ $length -eq 0 ]
then 
    echo "not running"
    exit 0
fi
for ((i=0;i<$length; i++))
do
    # check connections in netstat | grep pid
    conn_report=$(netstat -tpan | grep ${pids[$i]})
    readarray -t conns <<<"$conn_report"
    conn_length=${#conns[@]}
    
    for ((j=0;j<$conn_length;j++))
    do
        state=$(echo $conns[$i] | awk '{print $6}')
        if [ "$state" = "ESTABLISHED" ] || [ "$state" = "LISTENING" ] || [ "$state" = "SYN_SENT" ] || [ "$state" = "SYN_RECV" ]
        then
            echo "Okay"
            exit 0
        fi
    done
done
echo "not connected"
