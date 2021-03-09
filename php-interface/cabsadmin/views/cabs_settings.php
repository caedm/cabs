<?php
include "$_SERVER[DOCUMENT_ROOT]/config/settings.php";
include "$_SERVER[DOCUMENT_ROOT]/standard_functions.php";
include "$_SERVER[DOCUMENT_ROOT]/authorize.php";


if ($config->debugModeActive == 'true') {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

$handler_prefix = "/handlers/settings";

function get_settings_string($config) {
    $mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
    $result = mysqli_query($mysqli, "SELECT * FROM settings;");
    $result->data_seek(0);
    $settings = array();
    while ($setting = $result->fetch_assoc()) {
        array_push($settings, $setting);
    }
    $m = '';
    $m .= '<script type="text/javascript">';
    $m .= 'let settings = JSON.parse(\'';
    $m .= str_replace("'", "", json_encode($settings));
    $m .= '\');';
    $m .= '</script>';
    $m .= '<table class="pure-table">';
    $m .= '    <thead>';
    $m .= '        <tr>';
    $m .= '            <th>Setting</th>';
    $m .= '            <th>Value</th>';
    $m .= '            <th>Applied</th>';
    $m .= '            <th>Actions</th>';
    $m .= '        </tr>';
    $m .= '    </thead>';
    $m .= '    <tbody>';
    for ($i = 0; $i < count($settings); $i++) {
        $classlist = 'filterable';
        $setting = $settings[$i]['setting'];
        $m .= "   <tr class='$classlist'>";
        $m .= "       <td>" . $settings[$i]["setting"] . "</td>";
        $m .= "       <td>" . $settings[$i]["value"] . "</td>";
        $m .= "       <td>" . $settings[$i]["applied"] . "</td>";
        $m .= "       <td><a class='pure-button button-scary' onclick='return confirmClick();' href='handle_delete_setting.php?setting=$setting'>Delete</a></td>";
        $m .= '   </tr>';
    }
    $m .= '    </tbody>';
    $m .= '</table>';
    return $m;
}

function get_add_to_settings_forms($config) {
    global $handler_prefix;
    $m = '<div class="pure-g">';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= ' <div class="pure-u-3-4">';
    $m .= '     <h3>Add/Modify Setting:</h3>';
    $m .= '     <select id="setting">';
    $m .= '         <option value="Maximum Clients">Maximum Clients</option>';
    $m .= '         <option value="Log Level">Log Level</option>';
    $m .= '         <option value="Log History Amount">Log History Amount</option>';
    $m .= '         <option value="Log Prune Time">Log Prune Time</option>';
    $m .= '         <option value="Machine Reserve Time">Machine Reserve Time</option>';
    $m .= '         <option value="Machine Timeout Time">Machine Timeout Time</option>';
    $m .= '         <option value="Enable Blacklist">Enable Blacklist</option>';
    $m .= '         <option value="Automatically Blacklist Attacks">Automatically Blacklist Attacks</option>';
    $m .= '         <option value="Blacklist Connections per Minute">Blacklist Connections per Minute</option>';
    $m .= '         <option value="Authentication Server">Authentication Server</option>';
    $m .= '         <option value="Authentication Prefix String">Authentication Prefix String</option>';
    $m .= '         <option value="Authentication Postfix String">Authentication Postfix String</option>';
    $m .= '         <option value="Authentication User Attribute">Authentication User Attribute</option>';
    $m .= '         <option value="Authentication Group Attribute">Authentication Group</option>';
    $m .= '         <option value="Minimum RGS Version">Minimum RGS Version</option>';
    $m .= '     </select>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Maximum Clients</legend>';
    $m .= '             <p>This setting choses the maximum number of simultaneous connections that the broker will attempt to handle at one time</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <label for="value">Specify a value from 1 to 250:</label>';
    $m .= '                 <input name="value" type="number" min=1 max=250 required>';
    $m .= '                 <input name="setting" type="hidden" value="Max_Clients">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Log Level</legend>';
    $m .= '             <p>This setting is the amount of logging the broker will do, with 0 being none, and 4 being full debug. 3 is usually a good amount.</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <label for="value">Specify a value from 0 to 4:</label>';
    $m .= '                 <input name="value" type="number" min=0 max=4 required>';
    $m .= '                 <input name="setting" type="hidden" value="Log_Amount">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Log History Amount</legend>';
    $m .= '             <p>This setting is the amount of logging lines the broker will keep when it prunes old history. The amount you want depends on your database and log level.</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <label for="value">Specify a non-negative integer:</label>';
    $m .= '                 <input name="value" type="number" min=0 required>';
    $m .= '                 <input name="setting" type="hidden" value="Log_Keep">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Log Prune Time</legend>';
    $m .= '             <p>This setting is the amount of time in-between each pruning of th elog. This can be a fairly high value.</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <label for="value">Specify a value in seconds:</label>';
    $m .= '                 <input name="value" type="number" min=0 required>';
    $m .= '                 <input name="setting" type="hidden" value="Log_Time">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Machine Reserve Time</legend>';
    $m .= '             <p>This setting is the amount of time that the broker will keep a machine reserved without receiving a connection confirmation from the agent. This must be longer than the agent\'s heartbeat interval (default 120 seconds), but usually is at least 2 or 3 times longer.</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <label for="value">Specify a value in seconds:</label>';
    $m .= '                 <input name="value" type="number" min=0 required>';
    $m .= '                 <input name="setting" type="hidden" value="Reserve_Time">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Machine Timeout Time</legend>';
    $m .= '             <p>This setting is the amount of time the broker will wait to hear from a machine\'s agent before marking the machine as inactive. This value must be longer than the reserve time (default of 360 seconds).</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <label for="value">Specify a value in seconds:</label>';
    $m .= '                 <input name="value" type="number" min=0 required>';
    $m .= '                 <input name="setting" type="hidden" value="Timeout_Time">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Enable Blacklist</legend>';
    $m .= '             <p>This enables or disables the blacklist</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <select name="value">';
    $m .= '                     <option value="True">True</option>';
    $m .= '                     <option value="False">False</option>';
    $m .= '                 </select>';
    $m .= '                 <input name="setting" type="hidden" value="Use_Blacklist">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Automatically Blacklist Attacks</legend>';
    $m .= '             <p>This enables or disables the auto-blacklisting of any addresses not in the whitelist that make too many connections per second to the broker.</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <select name="value">';
    $m .= '                     <option value="True">True</option>';
    $m .= '                     <option value="False">False</option>';
    $m .= '                 </select>';
    $m .= '                 <input name="setting" type="hidden" value="Auto_Blacklist">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Blacklist Connections per Minute</legend>';
    $m .= '             <p>This setting is the amount of time the broker will wait to hear from a machine\'s agent, before marking the machine as inactive.</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <label for="value">Specify a value in seconds:</label>';
    $m .= '                 <input name="value" type="number" min=0 required>';
    $m .= '                 <input name="setting" type="hidden" value="Auto_Max">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Authentication Server</legend>';
    $m .= '             <p>This setting is the LDAP or Active Directory server used to authenticate users and their groups. The groups can correspond to machine pools.</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <label for="value">Specify an address:</label>';
    $m .= '                 <input name="value" type="text" required>';
    $m .= '                 <input name="setting" type="hidden" value="Auth_Server">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Authentication Prefix String</legend>';
    $m .= '             <p>For LDAP or Active Directory, this is used to bulid the Distinguished Name. For LDAP you may want something like: cn=. For Active Directory you may want something like: DOMAIN\</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <label for="value">Specify a prefix string:</label>';
    $m .= '                 <input name="value" type="text" required>';
    $m .= '                 <input name="setting" type="hidden" value="Auth_Prefix">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Authentication Postfix String</legend>';
    $m .= '             <p>For LDAP or Active Directory, this is used to build the Distinguished Name. For LDAP you may want something like: ,ou=accounts,dc=mysite,dc=org. For Active Directory you may want something like: @mysite.org</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <label for="value">Specify a postfix string:</label>';
    $m .= '                 <input name="value" type="text" required>';
    $m .= '                 <input name="setting" type="hidden" value="Auth_Postfix">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Authentication User Attribute</legend>';
    $m .= '             <p>For LDAP or Active Directory, this is used as the attribute for users. For LDAP or Active Directory you may want something like: cn</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <label for="value">Specify an attribute tag:</label>';
    $m .= '                 <input name="value" type="text" required>';
    $m .= '                 <input name="setting" type="hidden" value="Auth_Usr_Attr">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Authentication Group Attribute</legend>';
    $m .= '             <p>For LDAP or Active Directory, this is used as the attribute for groups. For LDAP or Active Directory you may want something like: memberOf</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <label for="value">Specify an attribute tag:</label>';
    $m .= '                 <input name="value" type="text" required>';
    $m .= '                 <input name="setting" type="hidden" value="Auth_Grp_Attr">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= '     <form class="pure-form pure-form-aligned settingForms" action="'. $handler_prefix . '/handle_addmodify_setting.php" method="post">';
    $m .= '         <fieldset>';
    $m .= '             <legend>Minimum RGS Version</legend>';
    $m .= '             <p>This should be the lowest version of RGS you are willing to connect with. This should be 3 numbers separated by 2 periods, no whitespace.</p>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <label for="value">Specify an RGS version:</label>';
    $m .= '                 <input name="value" type="text" required>';
    $m .= '                 <input name="setting" type="hidden" value="RGS_Ver_Min">';
    $m .= '             </div>';
    $m .= '             <div class="pure-control-group">';
    $m .= '                 <button type="submit" class="pure-button">Add/Modify</button>';
    $m .= '             </div>';
    $m .= '         </fieldset>';
    $m .= '     </form>';
    $m .= ' </div>';
    $m .= ' <div class="pure-u-1-8">';
    $m .= ' </div>';
    $m .= '</div>';
    return $m;
}

echo '<!DOCTYPE HTML>';
echo '<html>';
echo get_head_string();
echo '    <body>';
echo '      <script src="../js/confirm.js"></script>';
echo get_menu_string();
echo '      <h1>Settings</h1>';
echo get_filter_string();
echo get_settings_string($config);
if (isSuperAdmin($config)) {
    echo get_add_to_settings_forms($config);
}
echo '      <script src="../js/filter.js"></script>';
echo '      <script src="../js/cabs_settings.js"></script>';
echo '    </body>';
echo '</html>';
exit;
