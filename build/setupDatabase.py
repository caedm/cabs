#!/usr/bin/python
#This script is called by the installer.sh for the Broker
#This script checks the .conf file, and if it needs to, it sets up a local mysql server
#Then the script will attempt to connect to the database and create the needed tables for CABS

import os
import MySQLdb

settings = {}

def readConfigFile():
    #open the .conf file and return the variables as a dictionary
    global settings
    filelocation = os.path.dirname(os.path.abspath(__file__)) + '/CABS_server.conf'
    with open(filelocation, 'r') as f:
        for line in f:
            line = line.strip()
            if (not line.startswith('#')) and line:
                try:
                    (key,val) = line.split(':\t',1)
                except:
                    try:
                        (key,val) = line.split(None,1)
                        key = key[:-1]
                    except:
                        key = line
                        key = key.strip()
                        key = key[:-1]
                        val = ''
                settings[key] = val
        f.close()

def main():
    readConfigFile()
    #now take the alloted database and create the tables you will need
    try:
        #get the required information
        dbhost = settings["Database_Addr"]
        dbport = int(settings["Database_Port"])
        dbuser = settings["Database_Usr"]
        dbpass = settings["Database_Pass"]
        dbname = settings["Database_Name"]
        #check dbname ?
    except:
        raise SystemExit(1)
    
    try:
        db = MySQLdb.connect(host=dbhost, port=dbport, user=dbuser, passwd=dbpass, db=dbname)
        cursor = db.cursor()
    except:
        try:
            db = MySQLdb.connect(host=dbhost, port=dbport, user=dbuser, passwd=dbpass)
            cursor = db.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS " + dbname)
            cursor.execute("USE " + dbname)
        except:
            print "Could not connect to MySQL server.\nMake sure that the MySQL server is installed and {0} is a user with proper permissions and password.".format(dbuser)
            raise SystemExit(1)
    
    operations = ["CREATE TABLE IF NOT EXISTS machines (name VARCHAR(32) NOT NULL, machine VARCHAR(32) PRIMARY KEY, active TINYINT(1) NOT NULL, status VARCHAR(18), last_heartbeat TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, deactivated TINYINT(1) NOT NULL, reason VARCHAR(120))",
        "CREATE TABLE IF NOT EXISTS current (user VARCHAR(32) NOT NULL, name VARCHAR(32) NULL, machine VARCHAR(32) PRIMARY KEY, confirmed TINYINT(1) NOT NULL, connecttime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS pools (name VARCHAR(32) PRIMARY KEY, description VARCHAR(1024) NULL, secondary VARCHAR(1024) NULL, groups VARCHAR(1024) NULL, deactivated TINYINT(1) NOT NULL, reason VARCHAR(120) NULL)",
        "CREATE TABLE IF NOT EXISTS blacklist (address VARCHAR(32) PRIMARY KEY, banned TINYINT(1) NULL, attempts INT(11) NULL, timecleared TIME NULL)",
        "CREATE TABLE IF NOT EXISTS whitelist (address VARCHAR(32) PRIMARY KEY)",
        "CREATE TABLE IF NOT EXISTS settings (setting VARCHAR(32) PRIMARY KEY, value VARCHAR(64) NOT NULL)",
        "CREATE TABLE IF NOT EXISTS log (timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, message VARCHAR(1024) NULL, msg_type VARCHAR(16) NULL, id INT(11) PRIMARY KEY AUTO_INCREMENT)",
        ]
    for query in operations:
        cursor.execute(query)
    db.close()

if __name__ == "__main__":
    main()





