#!/bin/bash
user=
while getopts "u:" opt; do
    case $opt in
        u) user=${OPTARG} ;;
    esac
done
shift $((OPTIND - 1))

echo $user > /users.txt
/opt/cabsagent/cabsagent.py
