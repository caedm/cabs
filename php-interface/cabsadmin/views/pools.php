<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/standard_functions.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";

if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}
$handler_prefix="/handlers/pools";

function get_pools_string($config) {
    global $handler_prefix;
    $mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
    $result = mysqli_query($mysqli, "SELECT * FROM pools;");
    $result->data_seek(0);
    $pools = array();
    while ($pool = $result->fetch_assoc()) {
        array_push($pools, $pool);
    }
    $m = '';
    $m .= '<script type="text/javascript">';
    $m .= 'let pools = JSON.parse(\'';
    $m .= str_replace("'", "", json_encode($pools));
    $m .= '\');';
    $m .= '</script>';
    $m .= '<table class="pure-table cramped-table">';
    $m .= '    <thead>';
    $m .= '        <tr>';
    $m .= '            <th class="clickable" onclick="sortTable(0)">Pool</th>';
    $m .= '            <th class="clickable" onclick="sortTable(1)">Description</th>';
    $m .= '            <th class="clickable" onclick="sortTable(2)">Secondary</th>';
    $m .= '            <th class="clickable" onclick="sortTable(3)">Groups</th>';
    $m .= '            <th class="clickable" onclick="sortTable(4)">Disable Reason</th>';
    $m .= '            <th class="clickable" onclick="sortTable(5)">Actions</th>';
    $m .= '        </tr>';
    $m .= '    </thead>';
    $m .= '    <tbody>';
    for ($i = 0; $i < count($pools); $i++) {
        $name = $pools[$i]["name"];
        $classlist = 'filterable';
        if ($pools[$i]['deactivated'] === '1') {
            $classlist .= ' red';
        }
        $m .= "    <tr class='$classlist'>";
        $m .= "        <td>" . $pools[$i]["name"] . "</td>";
        $m .= "        <td>" . $pools[$i]["description"] . "</td>";
        $m .= "        <td>" . $pools[$i]["secondary"] . "</td>";
        $m .= "        <td>" . $pools[$i]["groups"] . "</td>";
        $m .= "        <td>" . $pools[$i]["reason"] . "</td>";
        $m .= "        <td>";
        if ($pools[$i]['deactivated'] === "0") {
            $m .= "     <form class='pure-form in-table' action='$handler_prefix/handle_disable_pool.php' method='post'>";
            $m .= "         <label for='disablereason'>Disable Reason:</label>";
            $m .= "         <input name='disablereason' type='text'>";
            $m .= "         <input name='poolname' type='hidden' value='$name'>";
            $m .= "         <button type='submit' class='pure-button'>Disable</button>";
        } else {
            $m .= "         <a class='pure-button' href='$handler_prefix/handle_enable_pool.php?poolname=$name'>Enable</a>";
        }
        $m .= "             <a class='pure-button button-scary' onclick='return confirmClick();' href='$handler_prefix/handle_delete_pool.php?poolname=$name'>Delete</a>";
        if ($pools[$i]['deactivated'] === "0") {
            $m .= "         </form>";
        }
        $m .= "        </td>";
        $m .= '    </tr>';
    }
    $m .= '    </tbody>';
    $m .= '</table>';
    return $m;
}

function get_add_to_pools_form() {
    global $handler_prefix;
    $m = '<div class="pure-g">';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= ' <form class="pure-form pure-form-aligned pure-u-3-4" action="' . $handler_prefix . '/handle_addmodify_pool.php" method="post">';
    $m .= '     <fieldset>';
    $m .= '         <legend>Add or modify pool</legend>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="poolname">Pool Name:</label>';
    $m .= '             <input id="poolname" name="poolname" pattern="^[^\s]*$" title="Spaces are not allowed in pool name." type="text" required>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="pooldescription">Pool Description:</label>';
    $m .= '             <input id="pooldescription" name="pooldescription" type="text" required>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="secondarypools">Secondary Pools:</label>';
    $m .= '             <input id="secondarypools" name="secondarypools" type="text">';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="activated" class="pure-radio">';
    $m .= '                 <input id="activated" type="radio" name="deactivated" value="0" checked>';
    $m .= '                 Activated';
    $m .= '             </label>';
    $m .= '             <label for="deactivated" class="pure-radio">';
    $m .= '                 <input id="deactivated" type="radio" name="deactivated" value="1">';
    $m .= '                 Deactivated';
    $m .= '             </label>';
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

function change_pool_name_form() {
    global $handler_prefix;
    $m = '<div class="pure-g">';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= ' <form class="pure-form pure-form-aligned pure-u-3-4" action="' . $handler_prefix . '/handle_namechange_pool.php" method="post">';
    $m .= '     <fieldset>';
    $m .= '         <legend>Change name</legend>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="originalpoolname">Original Pool Name:</label>';
    $m .= '             <input id="originalpoolname" name="originalpoolname" pattern="^[^\s]*$" type="text" required>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="newpoolname">New Pool Name:</label>';
    $m .= '             <input id="newpoolname" name="newpoolname" type="text" pattern="^[^\s]*$" title="Spaces are not allowed in pool name." required>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <button type="submit" class="pure-button">Change Name</button>';
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
echo '      <h1>Pools</h2>';
echo get_filter_string();
echo get_pools_string($config);
if (isSuperAdmin($config)) {
    echo get_add_to_pools_form();
    echo change_pool_name_form();
}
echo '      <script src="../js/filter.js"></script>';
echo '    </body>';
echo '</html>';
exit;
