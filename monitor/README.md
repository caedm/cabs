# CABS Monitor
Connection Automation/Brokerage System

The monitor is an Autoit script that is meant to run periodically on a Windows VM. It tries to log
in to all the RGS blades. If it can't log in, it will send commands to the blade to restart the RGS service and then
reboot if necessary. If the blade still doesn't respond, the script will tell the broker to disable the blade.
If blades disabled by the Autoit script start to work later, the script will re-enable them.
