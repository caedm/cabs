#!/bin/bash
# Create a binary tarball for distribution.
#set -e
#if [ ! -d "$CAEDMPRINT" ]; then
#    echo "ERROR: environmental variable CAEDMPRINT not set to a directory"
#    echo "Please run \`export CAEDMPRINT=/path/to/project/root\`"
#    exit 1
#fi
#
#if [ "$1" = "--nobin" ]; then
#    nobin=true
#    shift
#fi
#
#version=7.1.1
#name=caedmprint-$version
#dest="$CAEDMPRINT"/gen/$name
#archive="${dest}.tar.gz"
#
#if [ -e "$dest" ]; then
#    rm -vr "$dest"
#fi
#mkdir -vp "$dest"
#cd "$CAEDMPRINT/gen/"
#if [ "$nobin" ]; then
#    cp "$CAEDMPRINT/src/caedmprint.py" "$dest/caedmprint"
#else
#    pyinstaller --debug --onefile  "$CAEDMPRINT/src/caedmprint.py"
#    cp "$CAEDMPRINT/gen/dist/caedmprint" "$dest"
#fi
#cp -vLr "$CAEDMPRINT"/{res/,src/{backend,init.sh},scripts/install.sh,docs/README} "$dest"
#chmod +x "$dest/install.sh"
#tar -vcf "$archive" "./$name/"
