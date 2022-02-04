<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/standard_functions.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";


function get_12h_graphs_string() {
    $m = '';
    $m .= '<div class="graph-holder">';
    $directories = glob('graphs/*' , GLOB_ONLYDIR);
    foreach ($directories as $directory) {
        $pool = substr($directory, strlen($directory) - strpos(strrev($directory), '/'));
        $m .= "<img src='graphs/$pool/12h.png'>";
    }
    $m .= '</div>';
    return $m;
}

echo '<!DOCTYPE HTML>';
echo '<html>';
echo get_head_string();
echo '    <body>';
echo get_menu_string();
echo '    <h1>CABS</h1>';
echo get_12h_graphs_string();
echo '    </body>';
echo '</html>';
exit;
