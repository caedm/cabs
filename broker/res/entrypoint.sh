#!/bin/bash
set -e
service mysql start
mysql -u root -pmypassword < /opt/cabsbroker/createdb.sql
cd /opt/cabsbroker/
./setupDatabase.py
cd -

echo "$@"
if [ "$1" = dev ]; then
    cd /code/src
    bash
else
    exec "$@"
fi
