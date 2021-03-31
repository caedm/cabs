#!/bin/zsh
# This file is basically just a stub that exists to launch LabConnect on MacOS
python3version=`python3 -V`
pythonversion=`python -V` 2> /dev/null
zmodload zsh/regex

if [[ "$python3version" -regex-match "^Python 3.*$" ]]; then
    echo "Using $python3version"
    python3 /Applications/RGSConnect/rgsconnect.py
elif [[ "$pythonversion" -regex-match "^Python 3.*$" ]]; then
    echo "Using $pythonversion"
    python /Applications/RGSConnect/rgsconnect.py
else
    echo "Warning: python3 not detected"
    echo "Falling back to python2"
    echo "python2 is deprecated. Please upgrade to python3."
    python /Applications/RGSConnect/rgsconnect_legacy.py
fi
