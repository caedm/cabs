#!/bin/bash
set -e
service mysql start
mysql -u root -pmypassword < /createdb.sql
cd /opt/cabsbroker/
./setupDatabase.py
cd -

echo "$@"
if [ "$1" = dev ]; then
    cd /code/app
    bash
else
    exec "$@"
fi
