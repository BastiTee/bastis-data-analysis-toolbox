#!/bin/bash

cd "$( dirname "$( dirname "$( readlink -f $0 )" )" )"
source "dev-tools/base.sh"
PY=$( get_python_com )
[ -z $PY ] && exit 1

is_root

stdoutlog "Removing installed dependencies..."
cat requirements.txt | grep -v -e "^#" | grep "#" |\
awk '{print $7}' | while read lib
do
  $PY -m pip uninstall -y $lib
done
$PY -m pip uninstall -y bdatbx

stdoutlog "Cleaning local workspace..."
rm -vrf _* nltk-data
rm -vf bptbx
