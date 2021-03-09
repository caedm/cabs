<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}
?>
