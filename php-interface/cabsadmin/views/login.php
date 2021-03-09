<?php
include "$_SERVER[DOCUMENT_ROOT]/standard_functions.php";
$handler_prefix = "/handlers/login";
    // simple form for logging inm -> uname and pass
function loginForm(){
    global $handler_prefix;
    $m = '<div class="pure-g">';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= ' <form class="pure-form pure-form-aligned pure-u-3-4" action="' . $handler_prefix . '/handle_login.php" method="post">';
    $m .= '     <fieldset>';
    $m .= '         <legend>Login</legend>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="username">Username</label>';
    $m .= '             <input id="username" name="username" type="text" required>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <label for="password">password</label>';
    $m .= '             <input id="password" name="password" type="password" required>';
    $m .= '         </div>';
    $m .= '         <div class="pure-control-group">';
    $m .= '             <button type="submit" class="pure-button">Login</button>';
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
echo '      <h1>Login</h2>';
echo loginForm();
echo '    </body>';
echo '</html>';
exit;
?>