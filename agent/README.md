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
Copy the `app/` directory to the machine and run `app/install.sh`. This will install the agent
to `/opt/cabsagent/`. After installation, edit `/opt/cabsagent/cabsagent.conf` as needed. Start
the service with `systemctl start cabsagent`. Set it to start on boot with `systemctl enable
cabsagent`.

### Windows
#### Building
First, you have to create cabsagentsvc.exe with pyinstaller. In a Windows environment,
 - install ActiveState python. This will ensure the win32 python modules are installed
   correctly. If the modules aren't installed correctly, later on the Windows service will give
   an error about the service not starting in a timely fashion.
 - Install dependency modules: `pip -r app/requirements.txt`.
 - Install pyinstaller: `pip install pyinstaller`
 - Create the executable: `pyinstaller --onefile app/cabsagentsvc.py`
 - Move the executable from `dist/cabsagentsvc.exe` to `app/cabsagentsvc.exe`

After that, you can run `make` from Linux to create a zipfile with the installation script.
Make will include ssl certificates that are not checked into git, so make sure those are in the
app directory. You may want to edit `app/cabsagent.conf` before running `make` so that the
zipfile will contain the configuration you want.

#### Installing
Once the zipfile is created (it will be at `build/cabsagent-windows-<version>.zip`), copy it to
the target machine, unzip and run `install.exe`. After installing, this will start the agent
immediately and set it to start on boot.

If something doesn't work, you can test it out by
running `cabsagentsvc.exe debug` from a command prompt in the `C:\Program Files\CABS\Agent`
directory. You may have to run `cabsagentsvc.exe stop` first if the service is already running.
