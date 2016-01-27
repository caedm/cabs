#!/bin/bash
set -e
USAGE="$0 [-d|--dry-run] [-f|--force]
$0 [-h|--help]

Installs the CABS broker.

  -f, --force: rename existing config files instead of installing with .new
               extension"
ERR_OPTION=1
ERR_ROOT=2
echo=
for i in "$@"; do
    case $i in
    -d|--dry-run)
        echo=echo
        ;;
    -f|--force)
        force=true
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

function install_conf {
    src="$1"
    dest="$2"
    if [ -e "$dest" ]; then
        if ! $force && ! cmp -s "$src" "$dest"; then
            $echo install -vm 644 "$src" "$dest".new
            echo $(tput bold)warning: $(basename "$dest") installed as $dest.new$(tput sgr0)
        else
            $echo install -vm 644 --backup=simple "$src" "$dest"
        fi
    else
        $echo install -vm 644 "$src" "$dest"
    fi
}

[ "$echo" ] && echo DRY RUN
if [ $UID -ne 0 -a ! "$echo" ]; then
    echo This script must be ran as root.
    exit $ERR_ROOT
fi

$echo cd "$( dirname "${BASH_SOURCE[0]}" )"
$echo mkdir -p /usr/share/cabsbroker/
for f in res/{agent_cert.pem,broker_server.pem,caedm_ad.pem,trusted_clients.pem}; do
    $echo install -vm 644 $f /usr/share/cabsbroker/
done
install_conf cabsbroker.conf /usr/share/cabsbroker/cabsbroker.conf
$echo install -v src/cabsbroker.py /usr/bin/cabsbrokerd
echo Installation complete.
