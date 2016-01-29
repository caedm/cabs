#!/bin/bash
set -e
USAGE="$0 [-d|--dry-run]
$0 [-h|--help]

Installs the CABS broker.

  -h, --help:    show this help message and exit.
  -d, --dry-run: show what commands the installer will run without actually
                 doing anything.
"
ERR_OPTION=1
ERR_ROOT=2
ERR_BAD_PROGRAMMER=3
force=false
noconf=false
for i in "$@"; do
    case $i in
    -d|--dry-run)
        echo=echo
        ;;
    -h|--help)
        echo "$USAGE"
        exit 0
        ;;
    *)
        echo invalid option: $i > /dev/stderr
        exit $ERR_OPTION
        ;;
    esac
done

[ "$echo" ] && echo DRY RUN
if [ $UID -ne 0 -a ! "$echo" ]; then
    echo This script must be ran as root.
    exit $ERR_ROOT
fi

cd "$(dirname "${BASH_SOURCE[0]}")"
root="$(pwd | sed 's/\(.*broker\/\).*/\1/')"
if [ "$root" = "" ]; then
    echo "Couldn't find cabsbroker project root. Project root must be named"
    echo "\`broker\`."
    exit 1
fi
$echo cd "$root"

$echo mkdir -p /usr/local/share/cabsbroker/
for f in ./res/{agent_cert.pem,broker_server.pem,caedm_ad.pem,trusted_clients.pem}; do
    $echo install -vm 644 $f /usr/local/share/cabsbroker/
done
$echo install -vm 644 ./res/cabsbroker.conf /usr/local/share/cabsbroker/
$echo install -v ./src/cabsbroker.py /usr/local/sbin/cabsbrokerd
$echo install -vm 644 ./src/cabs.service /etc/systemd/system/
echo Installation complete.
echo "Don't forget to run $(tput bold)\`systemctl start cabs; systemctl enable cabs\`$(tput sgr0)."
