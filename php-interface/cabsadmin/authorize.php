<?php
if (session_status() != PHP_SESSION_ACTIVE) {
  session_start();
}

if (!isAuthorized()) {
  header('refresh: .5; url=/views/login.php');
  exit();
}

function isAuthorized() {
  foreach($_SESSION as $key => $value) {
    if (strpos($key, 'authorized') > -1) {
      return True;
    }
  }
  return False;
}

function isSuperAdmin($config) {
  if (session_status() != PHP_SESSION_ACTIVE) {
      session_start();
  }
  if ($config->useLDAP === True) {
    return in_array($config->superAdminGroup, $_SESSION['groups'], true);
  }
  else {
    return True;
  }
}
?>