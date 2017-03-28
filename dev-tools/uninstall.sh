#!/bin/bash

cd "$( dirname "$( dirname "$( readlink -f $0 )" )" )"
source "dev-tools/base.sh"
PY=$( get_python_com )
[ -z $PY ] && exit 1

is_root

stdoutlog "Deleting currently installed library..."
find /usr/local/ -iname "*bdatbx*" | while read file
do
  rm -vfr "$file"
done

stdoutlog "Removing installed dependencies..."
cat requirements.txt | grep "#" | awk '{print $7}' | while read lib
do
  $PY -m pip uninstall -y $lib
done

stdoutlog "Cleaning local workspace..."
rm -vrf _sanity _test nltk-data
