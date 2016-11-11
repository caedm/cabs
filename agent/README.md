# CABS Agent
Connection Automation/Brokerage System

## Overview
The Agent is installed on each machine managed by the Broker. It reports to the
Broker periodically on the status of the machine, including current users and
the status of a monitored process (rgsender in our case).

## Installation
In addition to installing the Agent on each machine, an entry for each machine
must be added to the Broker's database manually. See cabs-broker for more
information.

### Linux
Copy the `app/` directory to the machine and run
`app/install.sh`. This will install the agent to `/opt/cabsagent/`. After
installation, edit `/opt/cabsagent/cabsagent.conf` as needed. Start the service with
`systemctl start cabsagent`. Set it to start on boot with `systemctl enable cabsagent`.

### Windows
The most recent version of the Agent is incomplete for Windows.* A previous
version is in the windows folder. Run `windows/Install_CABS_Agent.exe` to
install.

*The script itself is working, but it isn't installable as a service yet.

See the README and wiki in the cabs-broker repo for more information about the CABS system.
