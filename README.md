# CABS Interface
Connection Automation/Brokerage System

##Overview
The Interface is a Django app used to monitor and configure the Broker. It presents real-time information
about what machines are online, what users are logged in, etc.

##Installation
The interface has been tested on a debian server. We have it installed on the same machine as the Broker.

Install dependencies (including web server):

    apt-get install apache2 python python-{pip,virtualenv,mysqldb,dev} \
            libldap2-dev libsasl2-dev libmysqlclient18 libmysqlclient-dev \
            libssl-dev libapache2-mod-wsgi

Set up the environment and project:

    mkdir /var/www/CABS_interface
    cd /var/www/CABS_interface
    virtualenv env
    source env/bin/activate
    pip install django python-ldap django_auth_ldap MySQL-python dnspython django-reversion

Run the install script: `/path/to/interface/scripts/install.sh`. This will
install the interface to `/var/www/CABS_interface`. You will need to edit
`/var/www/CABS_interface/admin_tools/settings.py` and
`/var/www/CABS_interface/admin_tools/settings-local.py-TEMPLATE`, removing the
`-TEMPLATE` suffix. You may need to run the install script again if it failed
the first time.

To display graphs, you will need to install CABS Graph.

See the README and wiki in the cabs-broker repo for more information about the CABS system.
