<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/standard_functions.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";

$handler_prefix = "/handlers/lists";

if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

function get_blacklist_string($config) {
    $mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
    $result = mysqli_query($mysqli, "SELECT * FROM blacklist;");
    $result->data_seek(0);
    $blacklist = array();
    while ($item = $result->fetch_assoc()) {
        array_push($blacklist, $item);
    }
    $m = '';
    $m .= '<script type="text/javascript">';
    $m .= 'let blacklist = JSON.parse(\'';
    $m .= str_replace("'", "", json_encode($blacklist));
    $m .= '\');';
    $m .= '</script>';
    $m .= '<table class="pure-table">';
    $m .= '    <thead>';
    $m .= '        <tr>';
    $m .= '            <th>Address</th>';
    $m .= '            <th>Banned</th>';
    $m .= '            <th>Attempts</th>';
    $m .= '            <th>Time Cleared</th>';
    $m .= '            <th>Actions</th>';
    $m .= '        </tr>';
    $m .= '    </thead>';
    $m .= '    <tbody>';
    for ($i = 0; $i < count($blacklist); $i++) {
        $address = $blacklist[$i]["address"];
        $newbanned = $blacklist[$i]["banned"];
        if ($newbanned === "0") {
            $newbanned = 1;
        } else {
            $newbanned = 0;
        }
        $m .= '    <tr class="filterable">';
        $m .= "        <td>" . $blacklist[$i]["address"] . "</td>";
        $m .= "        <td>" . $blacklist[$i]["banned"] . "</td>";
        $m .= "        <td>" . $blacklist[$i]["attempts"] . "</td>";
        $m .= "        <td>" . $blacklist[$i]["timecleared"] . "</td>";
        $m .= "        <td><a class='pure-button' href='handle_toggle_ban.php?newbanned=$newbanned&address=$address'>Toggle Ban</a><a class='pure-button' href='handle_delete_from_list.php?whitelistblacklist=blacklist&address=$address'>Delete</a></td>";
        $m .= '    </tr>';
    }
    $m .= '    </tbody>';
    $m .= '</table>';
    return $m;
}

function get_whitelist_string($config) {
    $mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
    $result = mysqli_query($mysqli, "SELECT * FROM whitelist;");
    $result->data_seek(0);
    $whitelist = array();
    while ($item = $result->fetch_assoc()) {
        array_push($whitelist, $item);
    }
    $m = '';
    $m .= '<script type="text/javascript">';
    $m .= 'let whitelist = JSON.parse(\'';
    $m .= str_replace("'", "", json_encode($whitelist));
    $m .= '\');';
    $m .= '</script>';
    $m .= '<table class="pure-table">';
    $m .= '    <thead>';
    $m .= '        <tr>';
    $m .= '            <th>Address</th>';
    $m .= '            <th>Actions</th>';
    $m .= '        </tr>';
    $m .= '    </thead>';
    $m .= '    <tbody>';
    for ($i = 0; $i < count($whitelist); $i++) {
        $address = $whitelist[$i]["address"];
        $m .= '    <tr class="filterable">';
        $m .= "        <td>" . $whitelist[$i]["address"] . "</td>";
        $m .= "        <td><a class='pure-button' href='handle_delete_from_list.php?whitelistblacklist=whitelist&address=$address'>Delete</a></td>";
        $m .= '    </tr>';
    }
    $m .= '    </tbody>';
    $m .= '</table>';
    return $m;
}

function get_add_to_lists_form() {
    global $handler_prefix;
    $m = '<div class="pure-g">';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= ' <form class="pure-form pure-form-aligned pure-u-3-4" action="' . $handler_prefix. '/handle_add_to_list.php" method="post">';
    $m .= '     <fieldset>';
    $m .= '         <legend>Add to list</legend>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="address">Address:</label>';
    $m .= '             <input id="address" name="address" type="text" placeholder="127.0.0.1" required>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="whitelist" class="pure-radio">';
    $m .= '                 <input id="whitelist" type="radio" name="whitelistblacklist" value="whitelist" checked>';
    $m .= '                 Whitelist';
    $m .= '             </label>';
    $m .= '             <label for="blacklist" class="pure-radio">';
    $m .= '                 <input id="blacklist" type="radio" name="whitelistblacklist" value="blacklist">';
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
echo get_filter_string();
echo '      <h1>Blacklist</h1>';
echo get_blacklist_string($config);
echo '      <h1>Whitelist</h1>';
echo get_whitelist_string($config);
echo get_add_to_lists_form();
echo '      <script src="../js/filter.js"></script>';
echo '    </body>';
echo '</html>';
exit;
