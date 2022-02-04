<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";

if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

$mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
$machinename = $mysqli->real_escape_string($_GET['machine']);

$query = "DELETE FROM current WHERE machine=\"$machinename\"";

if ($mysqli->query($query) === TRUE) {
} else {
    echo "Error updating record: " . $mysqli->error;
    echo "<br>";
    echo $query;
}

$query = "DELETE FROM machines WHERE machine=\"$machinename\"";

if ($mysqli->query($query) === TRUE) {
    header( "refresh: 3; url=../../views/machines.php");
    echo "Record updated successfully; redirecting in 3 seconds";
} else {
    echo "Error updating record: " . $mysqli->error;
    echo "<br>";
    echo $query;
}
exit;
?>
