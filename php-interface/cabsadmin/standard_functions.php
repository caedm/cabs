<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";

if (empty($_SERVER['HTTPS']) || $_SERVER['HTTPS'] === "off") {
    $location = 'https://' . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];
    header('HTTP/1.1 301 Moved Permanently');
    header('Location: ' . $location);
    exit;
}

function get_head_string() {
    $retstring = '';
    $retstring .= '<head>';
    $retstring .= '    <meta charset="utf-8"/>';
    $retstring .= '    <title>CABS</title>';
    $retstring .= '    <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.1/build/pure-min.css" integrity="sha384-oAOxQR6DkCoMliIh8yFnu25d7Eq/PHS21PClpwjOTeU2jRSq11vu66rf90/cZr47" crossorigin="anonymous">';
    $retstring .= '    <link rel="stylesheet" href="/css/general_styles.css">';
    $retstring .= '</head>';
    return $retstring;
}

function get_menu_string() {
    $retstring = '';
    $retstring .= '    <div class="pure-menu pure-menu-horizontal">';
    $retstring .= '        <a href="/index.php" class="pure-menu-heading pure-menu-link">CABS</a>';
    $retstring .= '        <ul class="pure-menu-list">';
    $retstring .= '            <li class="pure-menu-item"><a href="/views/graphs.php?pool=All_pools" class="pure-menu-link">Graphs</a></li>';
    $retstring .= '            <li class="pure-menu-item"><a href="/views/machines.php" class="pure-menu-link">Machines</a></li>';
    $retstring .= '            <li class="pure-menu-item"><a href="/views/pools.php" class="pure-menu-link">Pools</a></li>';
    $retstring .= '            <li class="pure-menu-item"><a href="/views/cabs_settings.php" class="pure-menu-link">Settings</a></li>';
    $retstring .= '            <li class="pure-menu-item"><a href="/views/lists.php" class="pure-menu-link">Lists</a></li>';
    $retstring .= '            <li class="pure-menu-item"><a href="/views/history.php" class="pure-menu-link">History</a></li>';
    $retstring .= '            <li class="pure-menu-item"><a href="/views/groups.php" class="pure-menu-link">Groups</a></li>';
    $retstring .= '            <li class="pure-menu-item"><a href="/views/logout.php" class="pure-menu-link">Logout</a></li>';
    $retstring .= '       </ul>';
    $retstring .= '   </div>';
    return $retstring;
}

function get_filter_string() {
    $m = '';
    $m .= '<div class="pure-control-group filter">';
    $m .= ' <input id="filter" name="filter" type="text">';
    $m .= ' <input id="filterbutton" type="button" value="Filter">';
    $m .= '</div>';
    return $m;
}

?>
