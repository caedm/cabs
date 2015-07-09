#!/bin/bash

#Run_Broker.sh Start/Sop the CABS Broker (CABS_server.py)

lockfile=/var/lock/cabs_server
srcdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
#change this to /dev/null to have no log
logfile=./broker_log

start() {
    if [ ! -f $lockfile ]; then
        echo "Starting CABS Broker"
        nohup /usr/bin/python $srcdir/CABS_server.py > $logfile 2>&1 & echo $! > $lockfile
    else
        echo "Lockfile exists already. Try restart."
    fi
}

stop() {
    echo "Stopping CABS Broker"
    kill -9 $( cat $lockfile )
    rm -f $lockfile
}

case "$1" in
    start)
        start
    ;;
    stop)
        stop
    ;;
    restart|reload)
        stop
        start
    ;;
    *)
        echo "Usage: $0 {start|stop|reload}"
        exit 1
esac
exit 0

