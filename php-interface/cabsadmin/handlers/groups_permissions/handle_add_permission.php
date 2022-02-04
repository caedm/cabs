<?php
    include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
    include "$_SERVER[DOCUMENT_ROOT]/standard_functions.php";
    include "$_SERVER[DOCUMENT_ROOT]/authorize.php";

    

    $mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
    $groupName = $mysqli->real_escape_string($_POST['groupname']);
    $poolName = $mysqli->real_escape_string($_POST['poolname']);
    if (isSuperAdmin($config)) {
        // check to see if the group is already there
        // make sure that group is an existing group and that pool is an existing pool
        $query = "INSERT INTO grp_permissions (group_name, pool_name) VALUES ('$groupName', '$poolName')";
        if ($mysqli->query($query) === True) {
            echo "successfully added permission";
            header("refresh: 2; url=../../views/groups.php");
        }
        else {
            echo "error adding permission <br>"; 
        }        
    }
    else {
        echo "forbidden <br>";
    }
    
?>