#!/bin/bash
set -e

if [ $UID -ne 0 ]; then
    echo This script must be ran as root. > /dev/stderr
    exit 1
fi

cd "$(dirname "${BASH_SOURCE[0]}")"
if type -P apt-get; then
    dpkg -i rgreceiver*.deb
    apt-get install -f
elif type -P yum; then
    yum install rgreceiver*.rpm -y
else
    echo ERROR: Neither apt-get or yum are installed. > /dev/stderr
    echo Couldn\'t install dependency: rgreceiver*.deb or rgreceiver*.rpm. \
        > /dev/stderr
    exit 2
fi

mkdir -p /opt/rgsconnect
cp -r * /opt/rgsconnect/
ln -s /opt/rgsconnect/RGSConnect /usr/local/bin/
