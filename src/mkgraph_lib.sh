ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$ROOT/cabsgraph.conf"

mk_all_graphs () {
    LENGTHS=(12h 1d 7d 1M 1y 3y)
    for length in ${LENGTHS[@]}; do
        for pool in ${POOLS[@]}; do
            mkgraph $length $pool 
        done
        for title in "${!AGGREGATE[@]}"; do
            mk_aggregate_graph $length "$title" ${AGGREGATE[$title]}
        done
    done
}

mkgraph () {
    mk_aggregate_graph $1 $2 $2
}

mk_aggregate_graph () {
    length="$1"
    name="$2"
    shift 2
    pools="$@"
    prefix=$(tr ' ' '_' <<< $name)
    dir="$ROOT/static/graphs/$prefix/"
    if [ "$length" = 12h ]; then
        users=$(get_users $pools)
        title="$name ($length. $users users)"
    else
        title="$name ($length)"
    fi
    mkdir -p "$dir"
    rrdtool graph "$dir/$length.png" \
        --start -$length --title "$title" \
        $(get_args $pools) \
        LINE2:min_available#00FF00:"Min machines available" \
        LINE1:avg_active#0000FF:"Avg machines active" \
        LINE1:max_users#FF0000:"Max users"
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

get_users() {
    users=0
    for pool in "$@"; do
        count=$(rrdtool fetch "$ROOT/db/$pool.rrd" MAX | sed '/nan/d' | tail -n 1 | awk '{print $2}')
        count=$(printf "%.0f" $count)
        ((users+=count))
    done
    echo $users
}

export_graphs() {
    # manage.py only works if you're in the same directory.
    cd $WWW
    source $WWW/env/bin/activate
    echo yes | $WWW/manage.py collectstatic
    deactivate
    cd -
}
