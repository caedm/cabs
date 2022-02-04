<?php
function get_pool_permissions($config) {
    $mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
    $groups = join("', '", $_SESSION['groups']);
    if (isSuperAdmin($config)) {
        $query = "SELECT * FROM pools;";
    }
    else {
        $query = "SELECT * from pools WHERE pools.name 
        IN (
            SELECT pool_name 
            FROM grp_permissions as gp
            WHERE gp.group_name IN ('$groups')
        );";
    }
    
    $result = mysqli_query($mysqli, $query);
    $pools = array();
    while ($pool = $result->fetch_assoc()) {
        array_push($pools, $pool);
    }
    return $pools;
}

function get_pool_names($pools) {
    return array_map(function($p) {
        return $p['name'];
    }, $pools);
}

function get_groups($config) {
    $mysqli = mysqli_connect($config->databaseServer, $config->databaseUsername, $config->databasePassword, $config->databaseName);
  
    $query = "SELECT * FROM groups";
    $result = mysqli_query($mysqli, $query);
    $groups = array();
    while ($group = $result->fetch_assoc()) {
        array_push($groups, $group);
    }
    return $groups;
}


?>