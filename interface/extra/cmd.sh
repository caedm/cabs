#!/bin/bash
echo starting up
./manage.py migrate
echo done migrating
./manage.py runserver 0.0.0.0:80
