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

        $query = "DELETE FROM grp_permissions WHERE group_name='$groupName' AND pool_name='$poolName'";
        if ($mysqli->query($query) === True) {
            echo "successfully removed permission";
            header("refresh: 2; url=../../views/groups.php");
        }
        else {
            echo "error removing permission"; 
        }        
    }
    else {
        echo "forbidden <br>";
    }
    
?>