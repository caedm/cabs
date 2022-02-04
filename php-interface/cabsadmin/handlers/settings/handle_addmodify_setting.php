<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";

if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

$mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
$setting = $mysqli->real_escape_string($_POST['setting']);
$value = $mysqli->real_escape_string($_POST['value']);

$query = "SELECT * FROM settings WHERE setting = \"$setting\"";

$result = $mysqli->query($query);

if ($result->num_rows > 0) {
    echo "Modifying record<br>";
    $query = "UPDATE settings set value=\"$value\" where setting = \"$setting\"";
} else {
    echo "Inserting new record<br>";
    $query = "INSERT INTO settings(setting,value) VALUES (\"$setting\",\"$value\")";
}

if ($mysqli->query($query) === TRUE) {
    header("refresh: 3; url=../../views/cabs_settings.php");
    echo "Record updated successfully; redirecting in 3 seconds";
} else {
    echo "Error updating record: " . $mysqli->error;
    echo "<br>";
    echo $query;
}
exit;
?>
