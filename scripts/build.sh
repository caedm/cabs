#!/bin/bash
# Create a binary tarball for distribution.
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"
root="$(pwd | sed 's/\(.*broker\/\).*/\1/')"
if [ "$root" = "" ]; then
    echo "Couldn't find cabsbroker project root. Project root must be named"
    echo "\`broker\`."
    exit 1
fi

version=1.1
name=cabsbroker-$version
dest="$root"/gen/$name
archive="${dest}.tar.gz"

if [ -e "$dest" ]; then
    rm -vr "$dest"
fi
mkdir -vp "$dest"
cd "$root/gen/"
cp -vLr "$root"/{res/,src/cabsbroker.py,scripts/install.sh} "$dest"
chmod +x "$dest/install.sh"
tar -vcf "$archive" "./$name/"
