<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
$username = $_POST["username"];
$password = $_POST["password"];
$tryCount = 0;
if ($config->useLDAP === True) {
    while ($tryCount < 3) {
        if ($username !== "" && $password != "") {
            $ldap_server = $config->openLDAPServer;
            $loginConnection = ldap_connect($ldap_server);
            if ($loginConnection && ldap_start_tls($loginConnection)) {
                //configure_ldap_options($loginConnection, $config);
                $user = $config->ADUserPrefix . $username . $config->userPostfix;
                // attempt a signin with the provided user name and password
                $loginSucceeded = ldap_bind($loginConnection, $user, $password);
                // make a separate ldap query to the OpenLDAP server to get group information of the user.
                if ($loginSucceeded) {
                    $searchResult = ldap_search($loginConnection , $config->ADbase, sprintf($config->ldapSearchQuery, $username), [$config->groupNameAttribute]);
                    $entries = ldap_get_entries($loginConnection , $searchResult);
                    $groups = extractGroupInfo($entries, $config);
                    session_start();
                    addToSession($groups);
                    echo "Successfully logged in <br>";
                    header("refresh: .5; url=../../index.php");
                    exit();
                    }
                }
            }
            $tryCount++;
        }
    }
    echo "login failed <br>";
    header("refresh: 1; url=../../login.php");
    exit();
}
else {
    if (session_status() !== PHP_SESSION_ACTIVE) {
        session_Start();
    }
    $_SESSION['authorized'] = True;
}

function addToSession($groups) {
    if (session_status() !== PHP_SESSION_ACTIVE) {
        session_Start();
    }
    $_SESSION['groups'] = $groups;
    $_SESSION['authorized'] = True;
}


function extractGroupInfo($entries, $config) {
    $groups = array_map(function($entry) use (&$config) {
        return $entry[$config->groupNameAttribute][0];
    }, $entries);
    return $groups;
}

?>