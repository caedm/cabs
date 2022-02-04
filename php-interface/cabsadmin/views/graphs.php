<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/standard_functions.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";

function get_graphs_string() {
    $pool = $_GET['pool'];
    $m = '';
    $m .= '<div class="graph-holder">';
    $images = glob("graphs/$pool/*");
    foreach ($images as $image) {
        $m .= "<img src='$image'>";
    }
    $m .= '</div>';
    return $m;
}

function get_choose_pool_string() {
    $retstring = '';
    $retstring .= '<div class="pure-menu pure-menu-horizontal">';
    $retstring .= ' <ul class="pure-menu-list">';
    $directories = glob('graphs/*' , GLOB_ONLYDIR);
    foreach ($directories as $directory) {
        $pool = substr($directory, strlen($directory) - strpos(strrev($directory), '/'));
        $retstring .= " <li class='pure-menu-item'><a href='graphs.php?pool=$pool' class='pure-menu-link'>$pool</a></li>";
    }
    $retstring .= ' </ul>';
    $retstring .= '</div>';
    return $retstring;
}

echo '<!DOCTYPE HTML>';
echo '<html>';
echo get_head_string();
echo '    <body>';
echo get_menu_string();
echo '      <h1>Graphs</h1>';
echo get_choose_pool_string();
echo get_graphs_string();
echo '    </body>';
echo '</html>';
exit;
