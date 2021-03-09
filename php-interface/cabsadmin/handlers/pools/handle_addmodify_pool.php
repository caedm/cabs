<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";

if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

$mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
$poolname = $mysqli->real_escape_string($_POST['poolname']);
$newpoolname = $mysqli->real_escape_string($_POST['newpoolname']);
$pooldescription = $mysqli->real_escape_string($_POST['pooldescription']);
$secondarypools = $mysqli->real_escape_string($_POST['secondarypools']);
// $authorizedgroups = $mysqli->real_escape_string($_POST['authorizedgroups']);
$deactivated = $mysqli->real_escape_string($_POST['deactivated']);
$poolnamepattern = "/^[^\s]*$/";

$query = "SELECT * FROM pools WHERE name = \"$poolname\"";

$result = $mysqli->query($query);

if ($result->num_rows > 0) {
    echo "Modifying record<br>";
    $query = "UPDATE pools set description=\"$pooldescription\",secondary=\"$secondarypools\",deactivated=\"$deactivated\" where name = \"$poolname\"";
    if ("" != $newpoolname.trim()) {
        if (preg_match($poolnamepattern, $newpoolname)) {
            echo "Updating name<br>";
            $query .= "UPDATE machines set name=\"$newpoolname\" where name=\"$poolname\" ". " " . "UPDATE pools set name=\"$newpoolname\" where name=\"$poolname\"";
        }
        else {
            echo "Failed to update name. Spaces are not allowed in new pool name.<br>";
        }
    }
    
} else {
    echo "Inserting new record<br>";
    $query = "INSERT INTO pools(name,description,secondary,deactivated,reason) VALUES (\"$poolname\",\"$pooldescription\",\"$secondarypools\",$deactivated,\"\")";
}


if ($mysqli->query($query) === TRUE) {
    header("refresh: 3; url=../../views/pools.php");
    echo "Record updated successfully; redirecting in 3 seconds";
} else {
    echo "Error updating record: " . $mysqli->error;
    echo "<br>";
    echo $query;
}
exit;
?>
