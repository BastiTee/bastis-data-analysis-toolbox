#!/bin/bash

cd "$( dirname "$( dirname "$( readlink -f $0 )" )" )"
source "dev-tools/base.sh"
is_root

stdoutlog "Installing globally..."
./setup.py install

[ $? != 0 ] && { stdoutlog "Error during installation."; exit 1; }

stdoutlog "Run tests..."
bdatbx-test-library

stdoutlog "Listing content in egg..."
find $( find /usr/local/ -type d -iname "*bdatbx*" | head -n1 )
