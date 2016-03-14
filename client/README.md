# CABS Client
Connection Automation/Brokerage System

##Overview
The Client is used by end users to request an open machine from the Broker. After it receives
the hostname from the broker, it will run the RGS Receiver to connect to the given machine.

##Installation

###Linux
`install_linux.sh` will the needed files to a directory of your choice (suppestion: `/opt/cabsclient/`). After
editing `CABS_client.conf`, it can be run with `<installdir>/Cabs_Client`.

###Windows
Simply run `Install_Cabs_Client.exe`, and edit `CABS_client.conf` as needed.

See the README and wiki in the cabs-broker repo for more information about the CABS system.
