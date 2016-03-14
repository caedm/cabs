# CABS
Connection Automation/Brokerage System

##Overview
CABS is used to assign machines to remote clients. Here at CAEDM, we use it to
assign RGS blades to our students. The entire project has several parts. Information about the
system as a whole is on the wiki, kept in the cabs-broker repo. For installation instructions, see
the individual README files.

###The Broker
- Our server that communicates between the Client and the Agent.
- Tracks free machines via a database.
- Machines are organized by "Pools" and pools can specify secondary pools for backup.
- Tracks usage history, and configuration history.
- Configuration and monitoring can be done via a web interface.
- Setup settings are stored in a configuration file.

##Installation
`scripts/install.sh` will install the broker to `/usr/local/`. Copy the default
config file from `/usr/local/share/cabsbroker/cabsbroker.conf` to
`/etc/cabsbroker.conf` and then read through the file, making changes as
needed. After that, run `scripts/setupDatabase.py` to create the SQL database
for the broker. To start the broker and set it to run on boot, run `systemctl start
cabsbroker; systemctl enable cabsbroker`.

You will need to add an entry to the broker's database for each machine to be
managed. This can be done from the Interface after it is installed. It can also
be done manually with SQL. You also need to add an entry for each pool.

See the README files in the other repositories for instructions on installing
the other parts.
