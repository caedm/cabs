<?php
    if(session_status() != PHP_SESSION_ACTIVE) {
        session_start();
    }
    unset($_SESSION['groups']);
    unset($_SESSION['authorized']);
    header('refresh: 1; url=login.php');
?>