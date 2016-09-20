#!/bin/bash
touch /tmp/users.txt
for user in $(cat /tmp/users.txt); do
    echo "$user tty7         2016-09-20 09:10 (:0)"
done
