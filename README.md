# CABS
Connection Automation/Brokerage System

##Overview
CABS is used to assign machines to remote clients. Here at CAEDM, we use it to
assign RGS blades to our students. The entire project has several parts:

###The Broker
- Our server that communicates between the Client and the Agent.
- Tracks free machines via a database.
- Machines are organized by "Pools" and pools can specify secondary pools for backup.
- Tracks usage history, and configuration history.
- Configuration and monitoring can be done via a web interface.
- Setup settings are stored in a configuration file.

###The Agent
- On a machine containing the RGS sender.
- Sends a status report to the Broker on a set interval.
- Confirms users currently logged into that machine.
- Available as an application on Windows or Linux.
- Configurable via a configuration file (can be distributed with proper default configurations).

###The Client
- On user's machines.
- A GUI for connections.
- Authenticates the User, and returns available pools.
- Can start an RGS session with RGS Receiver.
- Available as a desktop application on Windows, Linux, and Macintosh.
- Configurable via a configuration file (can be distributed with proper default configurations).

###The Interface
- A Django app for monitoring and configuring the Broker.
- View graphs, machine status, pools, settings, blacklist and logs.

####Graphs
CABS Graph is an appendage to the interface. It uses rrdtool to monitor the
machines and produces graphs which are viewed from the interface.

More information is in the wiki. It is kept in the cabs-broker repo, but it
covers all the other repos as well.

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
