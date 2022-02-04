#!/bin/bash
set -e
service mysql start
mysql -u root -pmypassword < /code/extra/createdb.sql
cd /code/app
./setupDatabase.py
cd -
mysql -u user -ppass test < /code/extra/populatedb.sql

exec "$@"
