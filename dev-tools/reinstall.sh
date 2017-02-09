#!/bin/bash

function stdoutlog () {
    [ -z $( command -v tput ) ] && {
        echo -e "\n--- $@\n"
    } || {
        echo -e "\n$( tput setaf 1)$@$( tput sgr0 )\n"
    }
}

LOCALFILES="bdatbx.egg-info build dist nltk-data"

cd "$( dirname "$( dirname "$( readlink -f $0 )" )" )"
[ $( whoami ) != "root" ] && { echo "Must be run as root"; exit 1; }

stdoutlog "Deleting currently installed library..."
find /usr/local/ -iname "*bdatbx*" | while read file
do
    rm -vfr "$file"
done

stdoutlog "Removing installed dependencies..."
cat requirements.txt | grep "#" | awk '{ print $1 }' | while read lib
do
    python3 -m pip uninstall -y $lib
done

stdoutlog "Cleaning local workspace..."
rm -vrf $LOCALFILES

stdoutlog "Installing globally..."
./setup.py install

stdoutlog "Run tests..."
bdatbx-test-library

stdoutlog "Listing content in egg..."
find $( find /usr/local/ -type d -iname "*bdatbx*" | head -n1 )

stdoutlog "Cleaning up..."
rm -rf $LOCALFILES
