#!/bin/bash
set -e
service mysql start
mysql -u root -pmypassword < /createdb.sql
cd /opt/cabsbroker/
./setupDatabase.py
cd -

exec "$@"
