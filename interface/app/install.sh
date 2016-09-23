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

#cd $DIR
#./manage.py makemigrations
#./manage.py migrate
#echo yes | $echo ./manage.py collectstatic
#cd -

a2enmod wsgi
##enable https only
#$echo a2enmod rewrite
#$echo a2enmod ssl
#
#$echo service apache2 restart

echo
echo Installation complete.
echo "Run with python $DIR/manage.py runserver"
