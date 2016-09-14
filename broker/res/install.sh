#!/bin/bash
set -e

if [ $UID -ne 0 ]; then
    echo This script must be ran as root. > /dev/stderr
    exit 1
fi
DIR=/opt/cabsbroker

cd "$(dirname "${BASH_SOURCE[0]}")"
pip install -r requirements.txt
mkdir -p $DIR
cp cabsbroker.py setupDatabase.py $DIR
if ! [ -f $DIR/cabsbroker.conf ]; then
    cp cabsbroker.conf $DIR
fi
install -vm 644 cabsbroker.service /etc/systemd/system/
#ln -s $DIR/cabsbroker.py /usr/local/bin/cabsbrokerd

echo Installation complete.
echo "When installing for the first time,"
echo " - edit $DIR/cabsbroker.conf as needed"
echo " - then run \`$DIR/setupDatabase.py\`"
echo " - start with \`systemctl start cabsbroker; systemctl enable cabsbroker\`"
