#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root."
    exit
fi
DIR=/opt/cabsinterface
cd "$(dirname "${BASH_SOURCE[0]}")"
mkdir -p $DIR

pip install -r requirements.txt

touch /etc/apache2/mods-enabled/python.load
cp -r admin_tools cabs_admin manage.py $DIR/
install -vm 644 apache_settings.conf /etc/apache2/sites-enabled/000-default.conf

mkdir -p /opt/cabsgraph/static

a2enmod wsgi

echo
echo Installation complete.
echo "Run with \`python $DIR/manage.py runserver\`"
echo "You may need to run \`python $DIR/manage.py migrate\` first."
