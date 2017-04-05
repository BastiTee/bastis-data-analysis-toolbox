#!/bin/bash

# prepare execution environment
cd "$( dirname "$( dirname "$( readlink -f $0 )" )" )"
source "dev-tools/base.sh"
PY=$( get_python_com )
[ -z $PY ] && { echo "Python not installed."; exit 1; }
echo "Running python: $( $PY --version )"

$PY -m robota_test.test_suite
run_pfx="$PY -m robota_scripts"
