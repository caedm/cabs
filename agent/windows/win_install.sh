#!/bin/bash
set -e  # exit immediately if any command terminates unsuccessfully.

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
mkdir -p ./gen/win/
cp ./src/cabsagent.py ./gen/win/
cp ./src/cabsagentsvc.py ./gen/win/
cp ./res/cabsagent_windows.conf ./gen/win/cabsagent.conf
cp ./res/*.pem ./gen/win/
