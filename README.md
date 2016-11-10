# CABS
Connection Automation/Brokerage System

##Overview
CABS is used to assign machines to remote clients. Here at CAEDM, we use it to
assign RGS blades to our students. The entire project has several parts. See
the wiki for information about how the system works. For
installation instructions, see the README files inside of the sub-directories.

##Installation
The broker, agent and interface have Dockerfiles that each define a working test environment.
See the Dockerfiles for what dependencies need to be installed first. Although the Dockerfiles
are set up for development, they have commented lines that show how to install and run the
applications for production.

Additional installation instructions, if any, are included in the README files of the individual
parts of cabs.

##Development and Testing
We use Docker to create a test environment for CABS. `control.py` contains automated test cases.
They have been tested with Docker 1.12.3 and Python 2.7. Follow these steps to run the tests:

 - Run `./broker/dev.sh` to start the broker. Wait until the line "starting up" is printed to
   stdout.
 - In another terminal window, run `./control.py test`. (note: the first time you run this, it will
   take a while for `control.py` to start all the docker containers needed to simulate the agents).

To view the state of the simulated agents, start the CABS interface with
`./interface/dev.sh`. After the django app is running, visit `localhost:8080` in a web
browser. Log in with username "cabstest" and password "password". Click on the "Machines"
tab. You can use `control.py` to manually simulate events such as a user requesting a
machine through the cabs client, a user logging in to a machine, a machine shutting down,
etc. Run `./control.py --help` for a list of commands.

###Tips for development
When developing the agent, use `./control.py restart` to restart the cabs agent on all running
Docker containers. If you make changes to the Dockerfile for the agent, use `./control.py build` to
rebuild the image and stop all containers running the old image.
