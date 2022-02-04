<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";

if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

$mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
$machinename = $mysqli->real_escape_string($_POST['machinename']);
$disablereason = $mysqli->real_escape_string($_POST['disablereason']);

$query = "UPDATE machines set deactivated=\"1\",reason=\"$disablereason\" where machine = \"$machinename\"";

if ($mysqli->query($query) === TRUE) {
    header("refresh: 3; url=../../views/machines.php");
    echo "Record updated successfully; redirecting in 3 seconds";
} else {
    echo "Error updating record: " . $mysqli->error;
    echo "<br>";
    echo $query;
}
exit;
?>
