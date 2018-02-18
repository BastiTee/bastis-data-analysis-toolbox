#!/bin/bash
cd "$( dirname "$( readlink -f $0 )" )"
source "dev-tools/base.sh" > /dev/null
PY=$( get_python_com )
[ -z $PY ] && exit 1
if [ $# -le 0 ]
then
    find robota_scripts -type f -iname "*.py" -and ! -iname "__init__*" |\
    while read script; do
      echo $( basename $script .py )
    done
else
    set -x
    script=$1
    shift
    export PYTHONPATH=${PYTHONPATH}:bastis-python-toolbox
    $PY robota_scripts/${script}.py $@
fi
