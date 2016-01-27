#!/bin/bash
set -e
USAGE="$0 [-d|--dry-run]
$0 [-h|--help]

Installs the CABS broker."
ERR_OPTION=1
ERR_ROOT=2
echo=
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
        echo invalid option: $i
        exit $ERR_OPTION
        ;;
    esac
done

[ "$echo" ] && echo DRY RUN
if [ $UID -ne 0 -a ! "$echo" ]; then
    echo This script must be ran as root.
    exit $ERR_ROOT
fi

$echo cd "$( dirname "${BASH_SOURCE[0]}" )"
$echo mkdir -p /usr/share/cabsbroker/
for f in res/{agent_cert.pem,broker_server.pem,caedm_ad.pem,trusted_clients.pem}; do
    $echo install -vm 644 $f /usr/share/cabsbroker/
done
$echo install -vm 644 cabsbroker.conf /usr/share/cabsbroker/
$echo install -v src/cabsbroker.py /usr/bin/cabsbrokerd
echo Installation complete.
