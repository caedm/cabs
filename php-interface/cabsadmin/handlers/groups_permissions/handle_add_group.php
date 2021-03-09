<?php
    include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
    include "$_SERVER[DOCUMENT_ROOT]/standard_functions.php";
    include "$_SERVER[DOCUMENT_ROOT]/authorize.php";


    $mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
    $groupName = $mysqli->real_escape_string($_POST['groupname']);
    if (isSuperAdmin($config)) {
        // check to see if the group is already there
        $query = "INSERT INTO groups (name) VALUES ('$groupName')";
        if ($mysqli->query($query) === True) {
            echo "successfully added group";
            header("refresh: 2; url=../../views/groups.php");
        }
        else {
            echo "error adding group"; 
        }        
    }
    else {
        echo "forbidden <br>";
    }
    
?>