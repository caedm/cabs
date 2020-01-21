# CABS Interface
Connection Automation/Brokerage System

## Overview
The Interface is a Django app used to monitor and configure the Broker. It
presents real-time information about what machines are online, what users are
logged in, etc.

## Installation
The interface has been tested on a Debian 8 server. We have it installed on the
same machine as the Broker.

run `sudo apt install apache2 python python-{pip,virtualenv,mysqldb,dev} libldap2-dev libsasl2-dev libmysqlclient18 libmysqlclient-dev libssl-dev libapache2-mod-wsgi`

if you haven't already, clone the repository with `git clone https://github.com/caedm/cabs`

navigate to `cabs/interface/app/admin_tools`

copy the `local_settings.py-TEMPLATE` file to `local_settings.py`

edit the `ALLOWED_HOSTS` field in `settings.py` and `local_settings.py`

edit the database info in `settings.py` and `local_settings.py`

if not using TLS, set `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` to `False` in `settings.py`

make sure that `AUTH_LDAP_SERVER_URI` is being set in settings.py (it's kind of set at the very bottom, but only if debug is off)

if you want to use LDAP with TLS, you'll need to put a key of some sort somewhere. If not, you'll need to comment out the relevant lines in `settings.py`

edit the `AUTHENTICATION_BACKENDS` variable so that it looks like:

```python2
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
)
```

It may be set in more than one place. Make sure that it looks like this in all of them or you might not be able to log in with LDAP!

run `sudo mkdir /var/www/CABS_interface`

navigate to `/var/www/CABS_interface`

run `sudo virtualenv env`

run `source env/bin/activate`

navigate to cabs/interface/app

run `sudo ./install.sh`

This will install the interface to `/opt/cabsinterface/`.

edit `/etc/apache2/sites-enabled/000-default.conf` such that it has the line `Alias /static/ /opt/cabsinterface/cabs_admin/static` instead of `Alias /static/ /opt/cabsinterface/static/`

go to /opt/cabsinterface and run `sudo python2 manage.py migrate`.

finally, run `sudo systemctl restart apache2.service`

You may need to run `a2enmod rewrite; a2enmod ssl` if you want to use only ssl.

To display graphs, you will need to install CABS Graph.
