<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";

if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

$mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
$originalpoolname = $mysqli->real_escape_string($_POST['originalpoolname']);
$newpoolname = $mysqli->real_escape_string($_POST['newpoolname']);
$namepattern = "/^[^\s]*$/";

if (preg_match($namepattern, $newpoolname)) {
    $mysqli->begin_transaction(MYSQLI_TRANS_START_READ_WRITE);
    $mysqli->autocommit(FALSE);
    echo "changing name.<br>";
    
    $query = "UPDATE pools SET name=\"$newpoolname\" WHERE name=\"$originalpoolname\";";
    if ($mysqli->query($query) === TRUE) {
        // continue with next query
        $machineQuery = "UPDATE machines SET name=\"$newpoolname\" WHERE name=\"$originalpoolname\";";
        if ($mysqli->query($machineQuery) === TRUE) {
            $mysqli->commit();
            header("refresh: 3; url=../../views/pools.php");
            echo "Record updated successfully; redirecting in 3 seconds";
            
        }
        else {
            echo "Error updating record: " . $mysqli->error;
            echo "<br>";
            echo $query;
            $mysqli->rollback();
        }
    }
}
else {
    echo "Error: no spaces allowed in new pool name. <br>";
}

exit;
?>
