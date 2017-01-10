# CABS
Connection Automation/Brokerage System

## Overview
CABS is used to assign machines to remote clients. Here at CAEDM, we use it to assign RGS
blades to our students. The entire project has several parts. See the wiki for information
about how the system works. For installation instructions, see the README files inside of the
sub-directories.

## Development and Testing
We use Docker to create a test environment for CABS. `control.py` contains automated test cases.
They have been tested with Docker 1.12.3 and Python 2.7. Follow these steps to run the tests:

 1. Run `./broker/dev.sh` to start the broker. Wait until the line "starting up" is printed to
    stdout.
 2. In another terminal window, run `./control.py test`. (note: the first time you run this, it
    will take a while for `control.py` to start all the docker containers needed to simulate
    the agents).

To view the state of the simulated agents, start the CABS interface with
`./interface/dev.sh`. After the django app is running, visit `localhost:8080` in a web
browser. Log in with username "cabstest" and password "password". Click on the "Machines"
tab. You can use `control.py` to manually simulate events such as a user requesting a
machine through the cabs client, a user logging in to a machine, a machine shutting down,
etc. Run `./control.py --help` for a list of commands.

### Tips for development
When developing the agent, use `./control.py restart` to restart the cabs agent on all running
Docker containers. If you make changes to the Dockerfile for the agent, use `./control.py
build` to rebuild the image and stop all containers running the old image.

Also, watch out for certificate files. Those are the only files we haven't checked into the git
repo (for obvious reasons). On my machine, I have the following files:

    agent/app/agent_server.pem
    agent/app/broker_cert.pem
    client/app/src/cert.pem

You don't need these files to run the automated test cases in `control.py`, but you will need
them when running `make` for the agent or client. It's probably easiest to get them from one of
our working machines that has the agent/client already installed.

## Release Notes

### v01092017-1
Bug Fixes:
 1. install linux client files with proper permissions
 2. fix various problems with the windows client installer

### v12142016-2

Bug Fixes:

1. Passwords with colons

New Features:

1. The agent talks with the RGS Tester.  If the tester can't log in to  a blade, it is disabled
   by "auto-it".  The rgsconnect agent if it finds itself in this state will first attempt to
   restart the rgs sender service to rectify the problem.  If the tester then finds the system
   working on the next round of tests, then the blade is re-enabled.  If the tester still can't
   log in on the next round of tests, it will send a reboot command to the agent service.  This
   feature has been working beautifully on the Linux systems for multiple semesters now without
   any ill effects.

2. The agent can have modules loaded to test for broken conditions.  If a broken condition is
   found, the agent can tell the broker to not have anyone visit that machine.  The modules can
   include code to rectify the problem if desired.


Notes from the developer:

install.exe should start the agent running right away, but it wasn't doing it for me. The
service did start automatically after I rebooted though. Alternatively, you can run `sc
start cabs_agent` from a command prompt to start it immediately.

The agent writes logs to the Local System user's APPDATA folder. On my VM, the location
was C:\Windows\System32\config\systemprofile\AppData\Roaming\cabsagent.log. By default
on Windows, the log level is set to WARNING (so there shouldn't be anything in the log
if all is well). If you edit \Program Files\CABS\Agent\cabsagent.conf and set Log_Level
to INFO (and then restart the cabs agent service), the agent will log every time it
sends a heartbeat which could be handy if you're not sure whether or not it's working.

Oh, and one more thing: I don't think the install.exe file will work unless they
uninstall the existing agent first (fixing that could be on the todo list). Running
\Program Files\CABS\Agent\uninstall.exe should do it, but they should check the Agent
folder and delete any files that uninstall.exe doesn't take care of.
