#!/bin/bash
if [ $UID -ne 0 ]; then
    echo This script must be ran as root > /dev/stderr
    exit 1
fi
DIR=/opt/cabsgraph/
cd "$(dirname "${BASH_SOURCE[0]}")"/..
mkdir -p $DIR
install -v ./src/create_db.sh "$DIR"
install -v ./src/mkgraph.sh "$DIR"
install -v ./src/mkgraph_lib.sh "$DIR"
install -v ./src/update.sh "$DIR"
install -vm 600 ./conf/my.cnf.TEMPLATE "$DIR"
install -vm 644 ./conf/cabsgraph.conf.TEMPLATE "$DIR"
install -vm 644 ./conf/cabsgraph.service /etc/systemd/system/
echo "You must edit $DIR/my.cnf.TEMPLATE and rename to my.cnf"
echo "You must edit $DIR/cabsgraph.conf.TEMPLATE and rename to cabsgraph.conf"
echo "Then run \`$DIR/create_db.sh\` to set up the databases."
echo "After that, don't forget to run \`systemctl start cabsgraph; systemctl enable cabsgraph\`"
