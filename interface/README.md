# CABS Interface
Connection Automation/Brokerage System

##Overview
The Interface is a Django app used to monitor and configure the Broker. It
presents real-time information about what machines are online, what users are
logged in, etc.

##Installation
The interface has been tested on a debian server. We have it installed on the
same machine as the Broker.

Install dependencies (including web server):

    apt-get install apache2 python python-{pip,virtualenv,mysqldb,dev} \
            libldap2-dev libsasl2-dev libmysqlclient18 libmysqlclient-dev \
            libssl-dev libapache2-mod-wsgi

Set up the environment and project:

    mkdir /var/www/CABS_interface
    cd /var/www/CABS_interface
    virtualenv env
    source env/bin/activate

Copy the `app/` directory to the machine and run `app/install.sh`. This will install the interface
to `/opt/cabsinterface/`.

You will need to edit `/opt/cabsinterface/admin_tools/settings.py` and
`/opt/cabsinterface/admin_tools/settings-local.py-TEMPLATE`, removing the
`-TEMPLATE` suffix. An example config file for Apache will also be installed to
`/etc/apache2/sites-enabled/000-default.conf-TEMPLATE`. After editing the
config files, may need to run the install script again if it failed the first
time. You may need to run `a2enmod rewrite; a2enmod ssl` if you want to use
only ssl.

To display graphs, you will need to install CABS Graph.
