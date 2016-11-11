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
Copy the `app/` directory to the machine and run `app/install.sh`. This will install the broker
to `/opt/cabsbroker/`. `install.sh` will output additional instructions for configuration after
installation.

You will need to add an entry to the broker's database for each machine to be
managed. This can be done from the Interface after it is installed. It can also
be done manually with SQL. You also need to add an entry for each pool.
