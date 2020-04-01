#!/bin/bash
set -e

if [ $UID -ne 0 ]; then
    echo This script must be ran as root. > /dev/stderr
    exit 1
fi
DIR=/opt/cabsbroker

cd "$(dirname "${BASH_SOURCE[0]}")"
pip3 install -r requirements.txt
mkdir -p $DIR
install -v cabsbroker.py $DIR
install -v setupDatabase.py $DIR
if ! [ -f $DIR/cabsbroker.conf ]; then
    install -vm 644 cabsbroker.conf $DIR
else
    echo $DIR/cabsroker.conf already exists, skipping...
fi
install -vm 644 cabsbroker.service /etc/systemd/system/

echo Installation complete.
echo "When installing for the first time,"
echo " - add the credentials for your MySQL server to $DIR/cabsbroker.conf"
echo " - then run \`$DIR/setupDatabase.py\`"
echo " - start with \`systemctl start cabsbroker; systemctl enable cabsbroker\`"
