#!/bin/bash
cd "$(dirname "${BASH_SOURCE[0]}")"
service cabsagent stop
./install.sh
service cabsagent start
