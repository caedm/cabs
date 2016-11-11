# CABS Client
Connection Automation/Brokerage System

## Overview
The Client is used by end users to request an open machine from the Broker. After it receives
the hostname from the broker, it will run the RGS Receiver to connect to the given machine.

## Building
### Linux
Use `make` to build a distributable archive for linux. You must have docker
installed. The binaries created with pyinstaller only work on the distribution
they are built on, so we use docker to create binaries for red hat and ubuntu.

### Windows
You must create the executable manually inside of Windows using pyinstaller.
Follow these steps to set up a Windows environment:
 - create a windows VM
 - install python
 - install pyinstaller with pip
 - download and install wxPython (get it from their website)
 - set up a shared folder so windows has access to the `app` and `build`
   directories.

Then you can create the windows binary with this command:
`pyinstaller --onefile --clean --distpath build/pyinstaller/dist
--workpath build/pyinstaller --specpath build/pyinstaller
--name RGSConnect-windows app/src/CABS_client.py`

After that, run `make windows` (from Linux) to create a distributable
Windows installer. nsis must be installed.

## Installation
After building, copy the newly created archive to the target machine and run either `install.sh`
or `install.exe`. Make sure to edit `CABS_client.conf` as needed.
