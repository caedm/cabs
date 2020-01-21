# CABS Broker
Connection Automation/Brokerage System

## Overview
- Our server that communicates between the Client and the Agent.
- Tracks free machines via a database.
- Machines are organized by "Pools" and pools can specify secondary pools for backup.
- Tracks usage history, and configuration history.
- Configuration and monitoring can be done via a web interface.
- Setup settings are stored in a configuration file.

## Installation
Install Debian 8
run `apt install sudo git vim python-pip libmysqlclient-dev libpython2.7-dev libldap2-dev libsasl2-dev mysql-server mysql-client`
give sudo privileges to your user with visudo
run `git clone https://github.com/caedm/cabs`
navigate to `cabs/broker/app`
run `sudo ./install.sh`
add the credentials for my mysql server to `/opt/cabsbroker/cabsbroker.conf`
navigate to `/opt/cabsbroker`
run `./setupDatabase.py`
start with systemctl start/enable cabsbroker

You will need to add an entry to the broker's database for each machine to be
managed. This can be done from the Interface after it is installed. It can also
be done manually with SQL. You also need to add an entry for each pool.
