#!/bin/bash
set -e  # exit immediately if any command terminates unsuccessfully.
USAGE="$0 [-d|--dry-run] [install|uninstall]
$0 [-h|--help]

Installs or uninstalls cabsagent (default: install)."

ERR_OPTION=1
ERR_PROJ_ROOT=2
ERR_ROOT=3
action=install
echo=
dest=/usr/lib/CABS/

for i in "$@"; do
    case $i in
    install)
        action=install
        ;;
    uninstall)
        action=uninstall
        ;;
    -d|--dry-run)
        echo=echo
        ;;
    -h|--help)
        echo "$USAGE"
        exit 0
        ;;
    *)
        echo invalid option: $i
        exit $ERR_OPTION
        ;;
    esac
done

[ "$echo" ] && echo DRY RUN
if [ $UID -ne 0 -a ! "$echo" ]; then
    echo This script must be ran as root.
    exit $ERR_ROOT
fi

if [ "$CABSAGENT_ROOT" != "" ]; then
    root="$CABSAGENT_ROOT"
else
    cd "$(dirname "${BASH_SOURCE[0]}")"
    root="$(pwd | sed 's/\(.*agent\/\).*/\1/')"
    if [ "$root" = "" ]; then
        echo "couldn't find cabsagent project root. Please run \`export "
        echo "CABSAGENT_ROOT=/path/to/cabs/agent/project\` and try again."
        exit $ERR_PROJ_ROOT
    fi
fi
echo "project root: $root"
cd "$root"

if [ "$action" = install ]; then
    $echo mkdir -vp "$dest"
    $echo install -vm 640 ./res/*.pem "$dest"
    $echo install -vm 644 --backup=simple ./res/cabsagent_linux.conf "$dest/cabsagent.conf"
    $echo install -v ./src/cabsagent.py "$dest/cabsagentd"
    $echo install -v ./src/cabsagent /etc/init.d/
    $echo chkconfig --add cabsagent --level 345
    echo Installation complete.
elif [ "$action" = uninstall ]; then
    for f in "$dest"/*.pem \
             "$dest"/{cabsagentd,cabsagent.conf} \
             /etc/init.d/cabsagent; do
        if [ -e "$f" ]; then
            $echo rm -vr "$f"
        fi
    done
    $echo chkconfig --del cabsagent
    echo Uninstallation complete.
fi
