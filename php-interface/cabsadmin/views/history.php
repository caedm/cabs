<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/standard_functions.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";

if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

function cmp_logs($a, $b) {
    return $a["timestamp"] < $b["timestamp"];
}

function get_logs_string($config) {
    $mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
    $result = mysqli_query($mysqli, "SELECT * FROM log;");
    $result->data_seek(0);
    $logs = array();
    while ($log = $result->fetch_assoc()) {
        array_push($logs, $log);
    }
    usort($logs, "cmp_logs");
    $m = '';
    $m .= '<script type="text/javascript">';
    $m .= 'let logs = JSON.parse(\'';
    $m .= str_replace("'", "", json_encode($logs));
    $m .= '\');';
    $m .= '</script>';
    $m .= '<table class="pure-table">';
    $m .= '    <thead>';
    $m .= '        <tr>';
    $m .= '            <th class="time">Time</th>';
    $m .= '            <th>Message</th>';
    $m .= '            <th>Message Type</th>';
    $m .= '            <th>id</th>';
    $m .= '        </tr>';
    $m .= '    </thead>';
    $m .= '    <tbody>';
    for ($i = 0; $i < count($logs); $i++) {
        $classlist = 'filterable';
        if ($logs[$i]['msg_type'] === 'WARNING') {
            $classlist .= ' red';
        } else if ($logs[$i]['msg_type'] === 'DEBUG') {
            $classlist .= ' yellow';
        }
        $id = 'tr' . $logs[$i]["id"];
        $m .= "    <tr class='$classlist'>";
        $m .= "        <td>" . $logs[$i]["timestamp"] . "</td>";
        $m .= "        <td>" . $logs[$i]["message"] . "</td>";
        $m .= "        <td>" . $logs[$i]["msg_type"] . "</td>";
        $m .= "        <td>" . $logs[$i]["id"] . "</td>";
        $m .= '    </tr>';
    }
    $m .= '    </tbody>';
    $m .= '</table>';
    return $m;
}

echo '<!DOCTYPE HTML>';
echo '<html>';
echo get_head_string();
echo '    <body>';
echo get_menu_string();
echo '      <h1>Logs</h1>';
echo get_filter_string();
echo get_logs_string($config);
echo '      <script src="../js/filter.js"></script>';
echo '    </body>';
echo '</html>';
exit;
