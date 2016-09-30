#!/bin/bash
if [ $UID -ne 0 ]; then
    echo This script must be ran as root. > /dev/stderr
    exit 1
fi

# uninstall old version, then install rgreceiver
cd "$(dirname "${BASH_SOURCE[0]}")"/src
if type -P apt-get; then
    if dpkg -l rgsconnect >/dev/null 2>&1 ; then
        echo Found old version of RGSConnect, uninstalling...
        apt-get remove rgsconnect -y
    fi
    dpkg -i rgreceiver*.deb
    apt-get install -f
elif type -P yum; then
    if rpm -q RGSConnect >/dev/null ; then
        echo Found old version of RGSConnect, uninstalling...
        yum remove RGSConnect -y
    fi
    yum upgrade rgreceiver*.rpm -y
else
    echo ERROR: Neither apt-get or yum are installed. > /dev/stderr
    echo Couldn\'t install dependency: rgreceiver*.deb or rgreceiver*.rpm. \
        > /dev/stderr
    exit 2
fi

# install rgsconnect
set -e
mkdir -vp /opt/rgsconnect
cp -vr * /opt/rgsconnect/
ln -vs /opt/rgsconnect/RGSConnect /usr/local/bin/

echo
echo Installation complete.
