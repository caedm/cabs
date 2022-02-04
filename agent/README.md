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
Run `make linux` to create an archive named `build/cabsagent-linux-<version>.zip`. Copy the
contents to the target machine and run `install.sh`. This will install the agent to
`/opt/cabsagent/`. After installation, edit `/opt/cabsagent/cabsagent.conf` as needed. Start
the service with `systemctl start cabsagent`. Set it to start on boot with `systemctl enable
cabsagent`.

You can update the service simply by running `install.sh` again followed by `systemctl restart
cabsagent`. The install script won't overwrite `cabsagent.conf`, so make sure to manually add
in any changes you need.

### Windows
#### Building
First, you have to create cabsagent.exe and the executables for any python scripts in
`app\checks\` with pyinstaller. In a Windows environment,
 - install ActiveState python3. This will ensure the win32 python modules are installed
   correctly. If the modules aren't installed correctly, later on the Windows service will give
   an error about the service not starting in a timely fashion.
 - Install dependency modules: `pip -r app/requirements.txt`.
 - Install pyinstaller: `pip install pyinstaller`
 - Edit `build.bat` to include the python agent and any desired checks. Run `build.bat` to create executables.

After that, you can create an install.exe using nsis. Be sure to place any desired ssl certificates in the app folder. Rename the cabsagent-windows.conf to cabsagent.conf and make changes as necessary. Edit install.nsi to your preferences and open the script with nsis. The resulting install.exe along with the other contents of the directory can be copied to any machine to install the agent to run in the background.

## Troubleshooting
On Windows, the logs are stored in the Local System user's APPDATA folder. This folder could be
'C:\Windows\System32\config\systemprofile\AppData\Roaming`. 
