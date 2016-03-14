#!/bin/bash

if [ "$1" = "-h" ]; then
    
    echo "usage: $0 <directory>"
    echo "This script installs the CABS Linux Client to <directory>"
    exit 0
fi

SRCDIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

if [ -z "$1" ]; then
    read -p "Install Directory : " DIR
else
    DIR=$1
fi

mkdir -m 775 -p $DIR

cp $SRCDIR/CABS_Client $DIR/CABS_Client
cp $SRCDIR/CABS_client.conf $DIR/CABS_client.conf
cp $SRCDIR/Header.png $DIR/Header.png
cp $SRCDIR/Icon.png $DIR/Icon.png
cp $SRCDIR/*.pem $DIR/

#make a shortcut?
