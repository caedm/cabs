#!/bin/bash
set -e

if [ $UID -ne 0 ]; then
    echo This script must be ran as root. > /dev/stderr
    exit 1
fi
DIR=/opt/cabsagent

cd "$(dirname "${BASH_SOURCE[0]}")"
pip install -r requirements.txt
mkdir -p $DIR
install -v cabsagent.py $DIR
install -vm 644 cabsagent.service /etc/systemd/system/
if ! [ -f $DIR/cabsagent.conf ]; then
    install -vm 644 cabsagent.conf $DIR
else
    echo $DIR/cabsroker.conf already exists, skipping...
fi

echo
echo Installation complete.
echo "Start with \`systemctl start cabsagent; systemctl enable cabsagent\`"
