#!/bin/bash

script_dir="$( dirname "$( readlink -f "$0" )" )"
source "$script_dir/base.sh"
is_root

PY=$( get_python_com )
[ -z $PY ] && exit 1

stdoutlog "Removing installed dependencies..."
cat requirements.txt | grep -v -e "^#" | grep "#" |\
awk '{print $1}' | while read lib
do
  $PY -m pip uninstall -y $lib
done
$PY -m pip uninstall -y robota

stdoutlog "Cleaning local workspace..."
rm -vrf _* nltk-data
rm -vf bptbx
