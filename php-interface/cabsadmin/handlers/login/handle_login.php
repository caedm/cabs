<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
//include "./config/settings.php";
    // takes the username, password, and the URL to redirect to once logged in as POST variables. 
    //
    $username = $_POST["username"];
    $password = $_POST["password"];
    $tryCount = 0;
    if ($config->useLDAP === True) {
        while ($tryCount < 3) {
            if ($username !== "" && $password != "") {
                $dns = dns_get_record($config->ldapServer);
                $target = $dns[0]['target'];
        
                $loginConnection = ldap_connect($target);
                if($loginConnection) {
                    configure_ldap_options($loginConnection, $config);
                    if (ldap_start_tls($loginConnection) === True ) {
                        $user = $config->ADUserPrefix . $username . $config->userPostfix;
                        // attempt a signin with the provided user name and password
                        $loginSucceeded = ldap_bind($loginConnection, $user, $password);
        
                        // make a separate ldap query to the OpenLDAP server to get group information of the user.
                        if ($loginSucceeded) {
                            //echo "logged in \n";
                            $data_server = $config->openLDAPServer;
                            $dataConnection = ldap_connect($data_server);
                            if ($dataConnection) {
                                configure_ldap_options($dataConnection, $config);
                                if (ldap_start_tls($dataConnection) === True) {
                                    $searchResult = ldap_search($dataConnection, $config->ADbase, sprintf($config->ldapSearchQuery, $username), [$config->groupNameAttribute]);
                                    $entries = ldap_get_entries($dataConnection, $searchResult);
                                    $groups = extractGroupInfo($entries, $config);
                                   // echo var_export($groups);
                                    session_start();
                                    addToSession($groups);
                                    echo "Successfully logged in <br>";
                                    header("refresh: .5; url=../../index.php");
                                    exit();
                                }
                            }
                        }
                    }
                }
            }
            $tryCount++;
        }
        echo "login failed <br>";
        header("refresh: 1; url=login.php");
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

function configure_ldap_options($connection) {
    ldap_set_option($connection, LDAP_OPT_X_TLS_CACERTFILE, $config->certfile);
    ldap_set_option($connection, LDAP_OPT_X_TLS_REQUIRE_CERT, LDAP_OPT_X_TLS_DEMAND);
    ldap_set_option($connection, LDAP_OPT_PROTOCOL_VERSION, 3);
    ldap_set_option($connection, LDAP_OPT_REFERRALS, 0);
}

?>