#!/bin/bash

if [ "$1" = "-h" ]; then
    
    echo "usage: $0 <directory>"
    echo "This script installs the CABS Broker to <directory>"
    exit 0
fi

#use apt-get to make sure that the following are installed:
#python, python-twisted, python-ldap, python-mysqldb, pyOpenSSL
#In the future, i may need to specify version numbers, this was build with python-twisted 14, and python2.7
if [[ $EUID -eq 0 ]]; then
    apt-get install python python-ldap python-mysqldb python-openssl python-twisted
else
    sudo apt-get install python python-ldap python-mysqldb python-openssl python-twisted
fi
#make the directory, and put the Broker there
if [ -z "$1" ]; then
    read -p "Install Directory : " Dir
else
    Dir=$1
fi

mkdir -m 775 -p $Dir

cp ./CABS_server.conf $Dir/CABS_server.conf
cp ./CABS_server.py $Dir/CABS_server.py
cp ./*.pem $Dir/

#then call setupDatabase.py
python ./setupDatabase.py

exit 0