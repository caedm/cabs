#!/bin/bash
set -e
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root."
    exit
fi
#echo=echo

force=false
if [ "$1" = "-f" ]; then
    force=true
    shift
fi

function install_conf {
    src="$1"
    dest="$2"
    if [ -e "$dest" ]; then
        if ! $force && ! cmp -s "$src" "$dest"; then
            $echo install -vm 644 "$src" "$dest".new
            echo $(tput bold)warning: $(basename "$dest") installed as $dest.new$(tput sgr0)
        else
            $echo install -vm 644 --backup=simple "$src" "$dest"
        fi
    else
        $echo install -vm 644 "$src" "$dest"
    fi
}

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

$echo rsync -av --exclude 'settings.py' "$SRC"/src/ $DEST/
install_conf "$SRC"/src/admin_tools/settings.py $DEST/admin_tools/settings.py
install_conf "$SRC"/res/apache_settings.conf /etc/apache2/sites-enabled/000-default.conf

$echo source $DEST/env/bin/activate
$echo $DEST/manage.py makemigrations
$echo $DEST/manage.py migrate
$echo deactivate

#enable https only
a2enmod rewrite
a2enmod ssl

$echo service apache2 restart
