#!/bin/bash
set -e
USAGE="$0 [-d|--dry-run] [-f|--force] [-n|--no-conf]
$0 [-h|--help]

Installs the CABS broker.

  -h, --help:    show this help message and exit.
  -d, --dry-run: show what commands the installer will run without actually
                 doing anything.
  -f, --force:   rename existing config files instead of installing with .new
                 extension.
  -n, --no-conf: don't install conf files at all.
"
ERR_OPTION=1
ERR_ROOT=2
ERR_BAD_PROGRAMMER=3
force=false
noconf=false
for i in "$@"; do
    case $i in
    -d|--dry-run)
        echo=echo
        ;;
    -f|--force)
        force=true
        ;;
    -n|--no-conf)
        noconf=true
        ;;
    -h|--help)
        echo "$USAGE"
        exit 0
        ;;
    *)
        echo invalid option: $i > /dev/stderr
        exit $ERR_OPTION
        ;;
    esac
done

function install_conf {
    if $noconf; then
        return
    fi
    src="$1"
    dest="$2"
    if [ -d "$dest" ]; then
        dest="$dest/$(basename "$src")"
    fi
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

cd "$(dirname "${BASH_SOURCE[0]}")"
root="$(pwd | sed 's/\(.*broker\/\).*/\1/')"
if [ "$root" = "" ]; then
    echo "Couldn't find cabsbroker project root. Project root must be named"
    echo "\`broker\`."
    exit 1
fi
$echo cd "$root"

$echo mkdir -p /usr/local/share/cabsbroker/
for f in ./res/{agent_cert.pem,broker_server.pem,caedm_ad.pem,trusted_clients.pem}; do
    $echo install -vm 644 $f /usr/local/share/cabsbroker/
done
install_conf ./res/cabsbroker.conf /etc/
$echo install -v ./src/cabsbroker.py /usr/local/sbin/cabsbrokerd
$echo install -v ./src/init /etc/init.d/cabs
echo Installation complete.
