<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";

if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

$mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
$machinename = $mysqli->real_escape_string($_POST['machinename']);
$pool = $mysqli->real_escape_string($_POST['pool']);

$query = "SELECT * FROM machines WHERE machine = \"$machinename\"";

$result = $mysqli->query($query);

if ($result->num_rows > 0) {
    echo "Modifying record<br>";
    $query = "UPDATE machines set name=\"$pool\" where machine = \"$machinename\"";
} else {
    echo "Inserting new record<br>";
    $query = "INSERT INTO machines(name,machine,active,deactivated,reason) VALUES (\"$pool\",\"$machinename\",\"1\",\"0\",\"\")";
}

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
