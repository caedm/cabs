<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";

if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

$mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
$poolname = $mysqli->real_escape_string($_POST['poolname']);
$disablereason = $mysqli->real_escape_string($_POST['disablereason']);

$query = "UPDATE pools set deactivated=\"1\",reason=\"$disablereason\" where name = \"$poolname\"";

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
