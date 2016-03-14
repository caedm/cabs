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
for f in ./certs/*.pem; do
    dest=/usr/local/share/cabsbroker/$(basename $f)
    if [ ! -e $dest ]; then
        $echo install -vm 600 $f $dest
    fi
done
$echo install -vm 644 ./conf/cabsbroker.conf /usr/local/share/cabsbroker/
$echo install -v ./src/cabsbroker.py /usr/local/sbin/cabsbrokerd
$echo install -vm 644 ./src/cabsbroker.service /etc/systemd/system/
echo Installation complete.
echo "When installing for the first time,"
echo " - copy /usr/local/share/cabsbroker/cabsbroker.conf to"
echo "   /etc/cabsbroker.conf and make changes as needed."
echo " - then run \`"($dirname "${BASH_SOURCE[0]}")"/setupDatabase.py\`"
echo " - start with \`systemctl start cabsbroker; systemctl enable cabsbroker\`"
