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

cd "$(dirname "${BASH_SOURCE[0]}")"

if [ "$action" = install ]; then
    $echo pip install -r ./requirements.txt
    $echo mkdir -vp /usr/share/cabsagent/
    $echo install -vm 600 ./res/*.pem /usr/share/cabsagent/
    $echo install -vm 644 ./res/cabsagent_linux.conf /usr/share/cabsagent/cabsagent.conf
    if [ ! -e /etc/cabsagent.conf ]; then
        $echo install -vm 644 ./res/cabsagent_linux.conf /etc/cabsagent.conf
    fi
    $echo install -v ./src/cabsagent.py /usr/sbin/cabsagentd
    $echo install -v ./src/cabsagent /etc/init.d/
    $echo chkconfig --add cabsagent --level 345
    echo Installation complete.
elif [ "$action" = uninstall ]; then
    $echo chkconfig --del cabsagent
    for f in /usr/share/cabsagent/ \
             /usr/sbin/cabsagentd \
             /etc/init.d/cabsagent \
             /etc/cabsagent.conf; do
        if [ -e "$f" ]; then
            $echo rm -vr "$f"
        fi
    done
    echo Uninstallation complete.
fi
