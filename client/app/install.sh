#!/bin/bash
if [ $UID -ne 0 ]; then
    echo This script must be ran as root. > /dev/stderr
    exit 1
fi
cd "$(dirname "${BASH_SOURCE[0]}")"/src
files="CABS_client.conf cert.pem Header.png Icon.ico Icon.png version.txt"
dir=/opt/RGSConnect

if type -P apt-get; then
    if dpkg -l rgsconnect >/dev/null 2>&1 ; then
        echo Found old version of RGSConnect, uninstalling...
        apt-get remove rgsconnect -y
    fi
    dpkg -i rgreceiver*.deb
    apt-get install -f
    bin=RGSConnect-ubuntu
elif type -P yum; then
    if rpm -q RGSConnect >/dev/null ; then
        echo Found old version of RGSConnect, uninstalling...
        yum remove RGSConnect -y
    fi
    yum upgrade rgreceiver*.rpm -y
    bin=RGSConnect-rhel
else 
    echo "ERROR: Couldn't install rgreceiver because neither apt-get or yum are installed.
RGSConnect is only supported on Ubuntu and Red Hat." > /dev/stderr
    exit 2
fi

set -e
mkdir -vp $dir
for f in $files; do
    install -vm 644 $f $dir/$f
done
install -v $bin $dir/RGSConnect
mkdir -p /usr/local/share/applications/
install -vm 644 rgsconnect.desktop /usr/local/share/applications

echo
echo Installation complete.
