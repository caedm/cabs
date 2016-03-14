# CABS Graph
Connection Automation/Brokerage System

##Overview
CABS Graph uses rrdtool to keep track of the number of machines online, the number of logged-in users and the
number of open machines. It runs as a daemon and generates new graphs for the Interface every five minutes.

##Installation

Dependencies:
 - mysql-client
 - rrdtool

`install.sh` will install CABS Graph to `/opt/cabsgraph/`. After installation,
the script will give necessary instructions for configuration. The MySQL
information should be the same as the Broker's database. Before starting the
daemon, the Interface should be installed (otherwise the daemon won't be able
to copy the generated graphs over to the correct location).

See the README and wiki in the cabs-broker repo for more information about the CABS system.
