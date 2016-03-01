ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$ROOT/cabsgraph.conf"

mkgraph () {
    mk_aggregate_graph $1 $2 $2
}

mk_aggregate_graph () {
    length="$1"
    title="$2"
    shift 2
    pools="$@"
    prefix=$(tr ' ' '_' <<< $title)
    dir="$ROOT/static/graphs/$prefix/"
    mkdir -p "$dir"
    rrdtool graph "$dir/$length.png" \
        --start -$length --title "$title ($length)" \
        $(get_args $pools) \
        LINE2:avg_active#0000FF:"Avg machines active" \
        LINE2:min_available#00FF00:"Min machines available" \
        LINE2:max_users#FF0000:"Max users"
}

get_args () {
    pools=("$@")
    for ((i=0; i < ${#pools[@]}; i++)); do
        echo -n "DEF:avg_active$i=db/${pools[$i]}.rrd:active:AVERAGE "
        echo -n "DEF:min_available$i=db/${pools[$i]}.rrd:available:MIN "
        echo -n "DEF:max_users$i=db/${pools[$i]}.rrd:users:MAX "
    done

    for func in avg_active min_available max_users; do
        echo -n "CDEF:$func=${func}0"
        for ((i=1; i < ${#pools[@]}; i++)); do
            echo -n ",${func}$i,+"
        done
        echo -n " "
    done
}

get_rra () {
    CF="$1"
    echo -n "RRA:$CF:0.5:1:144 \
             RRA:$CF:0.5:2:144 \
             RRA:$CF:0.5:12:168 \
             RRA:$CF:0.5:24:360 \
             RRA:$CF:0.5:288:365 \
             RRA:$CF:0.5:864:365"
    # I thought you could do this, but apparently you can't.
    #echo -n "RRA:$CF:0.5:5m:12h \
    #         RRA:$CF:0.5:10m:1d \
    #         RRA:$CF:0.5:1h:7d \
    #         RRA:$CF:0.5:2h:1M \
    #         RRA:$CF:0.5:1d:1y \
    #         RRA:$CF:0.5:3d:3y"
}

run_sql () {
    echo "$1" | mysql --defaults-file=$ROOT/my.cnf $DB
}

# TODO Get all queries in one go
query_db () {
    pool="$1"
    users=$(run_sql "SELECT COUNT(*) FROM current WHERE name = \"$pool\";" | tail -n 1)
    machines=$(run_sql "SELECT COUNT(*) FROM machines WHERE name = \"$pool\" AND active = True \
                        AND status LIKE '%%Okay' AND DEACTIVATED = False;" | tail -n 1)
    available=$(run_sql "SELECT COUNT(*) FROM machines WHERE name = \"$pool\" AND active = True \
                         AND status LIKE '%%Okay' AND DEACTIVATED = False \
                         AND machine NOT IN (SELECT machine FROM current);" | tail -n 1)
    echo -e "$users\t$machines\t$available"
}
