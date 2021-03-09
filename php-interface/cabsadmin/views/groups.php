<?php
#include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
// include "./config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/standard_functions.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";
include "$_SERVER[DOCUMENT_ROOT]/permissions_helpers.php";


$handler_prefix = "/handlers/groups_permissions";
function get_groups_string($config) {
    
    $mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
    $SQL = "SELECT g.name, group_concat(gp.pool_name) as pools
    FROM groups as g
    LEFT JOIN grp_permissions as gp ON g.name = gp.group_name
    GROUP BY g.name;";
    $result = mysqli_query($mysqli, $SQL);
    $result->data_seek(0);
    $groups = array();
    while ($group_info = $result->fetch_assoc()) {
        array_push($groups, $group_info);
    }

    $m = '';
    $m .= '<script type="text/javascript">';
    $m .= 'let pools = JSON.parse(\'';
    $m .= str_replace("'", "", json_encode($groups));
    $m .= '\');';
    $m .= '</script>';
    $m .= '<table class="pure-table cramped-table">';
    $m .= '    <thead>';
    $m .= '        <tr>';
    $m .= '            <th class="clickable" onclick="sortTable(0)">Group</th>';
    $m .= '            <th class="clickable" onclick="sortTable(1)">Permissions</th>';
    $m .= '        </tr>';
    $m .= '    </thead>';
    $m .= '    <tbody>';
    for ($i = 0; $i < count($groups); $i++) {
        $name = $groups[$i]["name"];
        $classlist = 'filterable';
        $m .= "    <tr class='$classlist'>";
        $m .= "        <td>" . $groups[$i]["name"] . "</td>";
        $m .= "        <td>" . $groups[$i]["pools"] . "</td>";
        $m .= "        </td>";
        $m .= '    </tr>';
    }
    $m .= '    </tbody>';
    $m .= '</table>';
    return $m;
}

function get_add_group_form() {
    global $handler_prefix;
    $m = '<div class="pure-g">';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= ' <form class="pure-form pure-form-aligned pure-u-3-4" action="' . $handler_prefix . '/handle_add_group.php" method="post">';
    $m .= '     <fieldset>';
    $m .= '         <legend>Add group</legend>';
    $m .= '         <div class="pure-control-group">';;
    $m .= '             <label for="groupname">Group Name</label>';
    $m .= '             <input id="groupname" name="groupname" pattern="^[^\s]*$" type="text" maxLength="32" required>';
    $m .= '         </div>';      
    $m .= '         <div class="pure-control-group">';
    $m .= '             <button type="submit" class="pure-button">Add</button>';
    $m .= '         </div>';
    $m .= '     </fieldset>';
    $m .= ' </form>';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= '</div>';
    return $m;
}

function get_add_permission_form($groups,$pools) {
    global $handler_prefix;
    $m = '<div class="pure-g">';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= ' <form class="pure-form pure-form-aligned pure-u-3-4" action="'. $handler_prefix . '/handle_add_permission.php" method="post">';
    $m .= '     <fieldset>';
    $m .= '         <legend>Add Permission to group</legend>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="group">Group:</label>';
    $m .= '             <select id="group" name="groupname">';
    //$groups = get_groups($config);
    forEach($groups as $group) {
        $m .= "             <option value='$group[name]'>$group[name]</option>";
    }
    $m .= '             </select>';
    // $m .= '             <label for="groupname">Group Name</label>';
    // $m .= '             <input id="groupname" name="groupname" pattern="^[^\s]*$" type="text" maxLength="32" required>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="pool">Pool:</label>';
    $m .= '             <select id="pool" name="poolname">';
    //$poolPermissions = get_pool_permissions($config);
    forEach($pools as $pool) {
        $m .= "             <option value='$pool[name]'>$pool[name]</option>";
    }
    $m .= '             </select>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <button type="submit" class="pure-button">Add</button>';
    $m .= '         </div>';
    $m .= '     </fieldset>';
    $m .= ' </form>';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= '</div>';
    return $m;
}

function get_delete_permission_form($groups, $pools) {
    global $handler_prefix;
    
    $m = '<div class="pure-g">';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= ' <form class="pure-form pure-form-aligned pure-u-3-4" action="'.$handler_prefix . '/handle_delete_permission.php" method="post">';
    $m .= '     <fieldset>';
    $m .= '         <legend>Remove Permission from group</legend>';;
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="group">Group:</label>';
    $m .= '             <select id="group" name="groupname">';
    //$groups = get_groups($config);
    forEach($groups as $group) {
        $m .= "             <option value='$group[name]'>$group[name]</option>";
    }
    $m .= '             </select>';
    // $m .= '             <label for="groupname">Group Name</label>';
    // $m .= '             <input id="groupname" name="groupname" pattern="^[^\s]*$" type="text" maxLength="32" required>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="pool">Pool:</label>';
    $m .= '             <select id="pool" name="poolname">';
    //$pools = get_pool_permissions($config);
    forEach($pools as $pool) {
        $m .= "             <option value='$pool[name]'>$pool[name]</option>";
    }
    $m .= '             </select>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <button type="submit" class="pure-button">Remove</button>';
    $m .= '         </div>';
    $m .= '     </fieldset>';
    $m .= ' </form>';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= '</div>';
    return $m;
}

$groups = get_groups($config);
$pools = get_pool_permissions($config);
echo '<!DOCTYPE HTML>';
echo '<html>';
echo get_head_string();
echo '    <body>';
echo '      <script src="../js/sortTable.js"></script>';
echo '      <script src="../js/confirm.js"></script>';
echo get_menu_string();
echo '      <h1>Groups</h2>';
echo get_filter_string();
echo get_groups_string($config);
if (isSuperAdmin($config)) {
    echo get_add_group_form();
    echo get_add_permission_form($groups,$pools);
    echo get_delete_permission_form($groups,$pools);
}
echo '      <script src="../js/filter.js"></script>';
echo '    </body>';
echo '</html>';
exit;


?>