<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";


if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

$mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
$result = mysqli_query($mysqli, "SELECT * FROM cabsadmin.machines;");
$result->data_seek(0);
$machines = array();
while ($machine = $result->fetch_assoc()) {
    array_push($machines,$machine);
}
echo "let machines = JSON.parse('" . json_encode($machines) . "');";
?>
