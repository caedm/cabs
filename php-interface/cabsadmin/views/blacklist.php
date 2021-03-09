<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/standard_functions.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";
 
if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

function get_lists_string($config) {
    $mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
    $result = mysqli_query($mysqli, "SELECT * FROM blacklist;");
    $result->data_seek(0);
    $lists = array();
    while ($item = $result->fetch_assoc()) {
        array_push($lists, $item);
    }
    $m = '';
    $m .= '<script type="text/javascript">';
    $m .= 'let lists = JSON.parse(\'';
    $m .= json_encode($lists);
    $m .= '\');';
    $m .= '</script>';
    $m .= '<div class="pure-g">';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= ' <div class="pure-u-3-4">';
    $m .= '     <table class="pure-table">';
    $m .= '         <thead>';
    $m .= '             <tr>';
    $m .= '                 <th>Address</th>';
    $m .= '                 <th>Banned</th>';
    $m .= '                 <th>Attempts</th>';
    $m .= '                 <th>Time Cleared</th>';
    $m .= '             </tr>';
    $m .= '         </thead>';
    $m .= '         <tbody>';
    for ($i = 0; $i < count($lists); $i++) {
        $m .= '         <tr>';
        $m .= "             <td>" . $lists[$i]["address"] . "</td>";
        $m .= "             <td>" . $lists[$i]["banned"] . "</td>";
        $m .= "             <td>" . $lists[$i]["attempts"] . "</td>";
        $m .= "             <td>" . $lists[$i]["timecleared"] . "</td>";
        $m .= '         </tr>';
    }
    $m .= '         </tbody>';
    $m .= '     </table>';
    $m .= ' </div>';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= '</div>';
    return $m;
}

function get_add_to_lists_form() {
    $m = '<div class="pure-g">';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= ' <form class="pure-form pure-form-aligned pure-u-3-4">';
    $m .= '     <fieldset>';
    $m .= '         <legend>Add to list</legend>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="address">Address:</label>';
    $m .= '             <input id="address" type="text" placeholder="127.0.0.1" required>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="whitelist" class="pure-radio">';
    $m .= '                 <input id="whitelist" type="radio" name="whitelistblacklist" value="0" checked>';
    $m .= '                 Whitelist';
    $m .= '             </label>';
    $m .= '             <label for="blacklist" class="pure-radio">';
    $m .= '                 <input id="blacklist" type="radio" name="whitelistblacklist" value="1">';
    $m .= '                 Blacklist';
    $m .= '             </label>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <button type="submit" class="pure-button">Add to list</button>';
    $m .= '         </div>';
    $m .= '     </fieldset>';
    $m .= ' </form>';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= '</div>';
    return $m;
}

echo '<!DOCTYPE HTML>';
echo '<html>';
echo get_head_string();
echo '    <body>';
echo get_menu_string();
echo get_lists_string($config);
if (isSuperAdmin($config)) {
    echo get_add_to_lists_form();
}
echo '    </body>';
echo '</html>';
exit;
