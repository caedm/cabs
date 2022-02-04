<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/standard_functions.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";
include "$_SERVER[DOCUMENT_ROOT]/permissions_helpers.php";


if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

$handler_prefix = "/handlers/machines";

function get_machines_string($config) {
    global $handler_prefix;
    $mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
    $result = mysqli_query($mysqli, "SELECT * FROM current RIGHT JOIN machines ON machines.machine = current.machine;");
    $result->data_seek(0);
    $machines = array();
    while ($machine = $result->fetch_assoc()) {
        array_push($machines, $machine);
    }
    $m = '';
    $m .= '<script type="text/javascript">';
    $m .= 'let machines = JSON.parse(\'';
    $m .= str_replace("'", "", json_encode($machines));
    $m .= '\');';
    $m .= '</script>';
    $m .= '<table class="pure-table cramped-table">';
    $m .= '    <thead>';
    $m .= '        <tr>';
    $m .= '            <th class="clickable" onclick="sortTable(0)">Machine</th>';
    $m .= '            <th class="clickable" onclick="sortTable(1)">Pool</th>';
    $m .= '            <th class="clickable" onclick="sortTable(2)">User</th>';
    $m .= '            <th class="clickable" onclick="sortTable(3)">Active</th>';
    $m .= '            <th class="clickable" onclick="sortTable(4)">Status</th>';
    $m .= '            <th class="clickable" onclick="sortTable(5)">Last Heartbeat</th>';
    $m .= '            <th class="clickable" onclick="sortTable(6)">Disable Reason</th>';
    $m .= '            <th class="clickable" onclick="sortTable(7)">Actions</th>';
    $m .= '        </tr>';
    $m .= '    </thead>';
    $m .= '    <tbody>';
    $poolPermissions = get_pool_permissions($config);
    $poolNames = get_pool_names($poolPermissions);
    for ($i = 0; $i < count($machines); $i++) {
        $classlist = 'filterable';
        if ($machines[$i]['deactivated'] === '1') {
            $classlist .= ' red';
        }
        $machinename = $machines[$i]['machine'];
        $m .= "   <tr class='$classlist'>";
        $m .= "       <td>" . $machines[$i]["machine"] . "</td>";
        $m .= "       <td>" . $machines[$i]["name"] . "</td>";
        $m .= "       <td>" . $machines[$i]["user"] . "</td>";
        $m .= "       <td>" . $machines[$i]["active"] . "</td>";
        $m .= "       <td>" . $machines[$i]["status"] . "</td>";
        $m .= "       <td>" . $machines[$i]["last_heartbeat"] . "</td>";
        $m .= "       <td>" . $machines[$i]["reason"] . "</td>";
        $m .= "       <td>";
        if (in_array($machines[$i]["name"], $poolNames, true)) {
            if ($machines[$i]['deactivated'] === "0") {
                $m .= "     <form class='pure-form in-table' action='$handler_prefix/handle_disable_machine.php' method='post'>";
                $m .= "         <label for='disablereason'>Disable Reason:</label>";
                $m .= "         <input name='disablereason' type='text' required>";
                $m .= "         <input name='machinename' type='hidden' value='$machinename'>";
                $m .= "         <button type='submit' class='pure-button'>Disable</button>";
            } else {
                $m .= "         <a class='pure-button' href='$handler_prefix/handle_enable_machine.php?machine=$machinename'>Enable</a>";
            }
            $m .= "             <a class='pure-button button-scary' onclick='return confirmClick();' href='$handler_prefix/handle_delete_machine.php?machine=$machinename'>Delete</a>";
            if ($machines[$i]['deactivated'] === "0") {
                $m .= "     </form>";
            }
        }
        
        $m .= "       </td>";
        $m .= '   </tr>';
    }
    $m .= '    </tbody>';
    $m .= '</table>';
    return $m;
}

function get_add_to_machines_form($config) {
    global $handler_prefix;

    $m = '<div class="pure-g">';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= ' <form class="pure-form pure-form-aligned pure-u-3-4" action="' . $handler_prefix . '/handle_addmodify_machine.php" method="post">';
    $m .= '     <fieldset>';
    $m .= '         <legend>Add or modify a machine</legend>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="machinename">Machine Name:</label>';
    $m .= '             <input id="machinename" name="machinename" type="text" required>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="pool">Pool:</label>';
    #$m .= '             <input id="pool" name="pool" type="text" required>';
    $m .= '             <select id="pool" name="pool">';
    $poolPermissions = get_pool_permissions($config);
    forEach($poolPermissions as $pool) {
        $m .= "             <option value='$pool[name]'>$pool[name]</option>";
    }
    $m .= '             </select>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <button type="submit" class="pure-button">Add/Modify</button>';
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
echo '      <script src="../js/sortTable.js"></script>';
echo '      <script src="../js/confirm.js"></script>';
echo get_menu_string();
echo '      <h1>Machines</h1>';
echo get_filter_string();
echo get_machines_string($config);
echo get_add_to_machines_form($config);
echo '      <script src="../js/filter.js"></script>';
echo '    </body>';
echo '</html>';
exit;
