<?php
$config = new StdClass();
$config->debugModeActive="true";
// if using LDAP auth, set group 
$config->useLDAP = True;
$config->superAdminGroup ="";

$config->databaseServer= "";
$config->databaseUsername="";
$config->databasePassword="";
$config->databaseName="";

// LDAP SETTINGS
// ldapServer is used to authenticate a user's username and password. Performs a DNS lookup for the given server name.
$config->ldapServer="";
$config->ADbase="";
$config->ADUserPrefix="";
$config->ADUserPostfix="";
$config->certfile="";
$config->openLDAPServer="";
// queries the openLDAP server for group membership based on memberuid=$username
$config->ldapSearchQuery="memberuid=%s";
$config->groupNameAttribute = 'cn';

?>
