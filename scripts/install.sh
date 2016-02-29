#!/bin/bash
set -e
USAGE="$0 [options]
$0 [-h|--help]

Installs the CABS broker.

  -h, --help:    show this help message and exit.
  -d, --dry-run: show what commands the installer will run without actually
                 doing anything.
"
echo=
force=false
noconf=false
rsyncDry=

for arg in "$@"; do
    case $arg in
    -d|--dry-run)
        echo=echo
        rsyncDry="--dry-run"
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

if [ "$EUID" -ne 0 -a ! "$echo" ]; then
    echo "This script must be run as root."
    exit
fi
if [ "$echo" ]; then
    echo DRY RUN
fi

if [ "$CABS_INTERFACE_ROOT" != "" ]; then
    SRC="$CABS_INTERFACE_ROOT"
else
    cd "$(dirname "${BASH_SOURCE[0]}")"
    SRC="$(pwd | sed 's/\(.*interface\/\).*/\1/')"
    if [ "$SRC" = "" ]; then
        echo "couldn't find cabs interface project root. Please run \`export "
        echo "CABS_INTERFACE_ROOT=/path/to/cabs/interface\` and try again."
        exit $1
    fi
fi
echo "project root: $SRC"

DEST=/var/www/CABS_interface
$echo mkdir -p $DEST

$echo touch /etc/apache2/mods-enabled/python.load

rsync $rsyncDry -av --size-only --exclude 'local_settings.py' --exclude 'migrations/' "$SRC"/src/ $DEST/
$echo install -vm 644 "$SRC"/res/apache_settings.conf-TEMPLATE /etc/apache2/sites-enabled/000-default.conf-TEMPLATE

$echo source $DEST/env/bin/activate
$echo $DEST/manage.py makemigrations
$echo $DEST/manage.py migrate
$echo cd $DEST
echo yes | $echo ./manage.py collectstatic
$echo deactivate

#enable https only
$echo a2enmod rewrite
$echo a2enmod ssl

$echo service apache2 restart
