#!/usr/bin/python2
#This is the test Agent for CABS for linux

# Workaround until a bugfix in pyinstaller gets released on pypi.
# See https://github.com/pyinstaller/pyinstaller/commit/f788dec36b8d55f4518881be9f4188ad865306ec
import os
import logging
from sched import scheduler
from time import time, sleep

logfile = os.path.join(os.getenv("APPDATA"), "testsrv.log")
print "logfile: " + logfile
logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s %(message)s')
s = scheduler(time, sleep)
while True:
    s.enter(5, 1, lambda: logging.info("hello there"), ())
    s.run()
