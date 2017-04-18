#!/bin/bash

[ -z "$1" ] && { echo "No data dir given"; exit 1; }
data_dir=$( readlink -f $1 )

cd $( dirname $( readlink -f $0 ))
export ROBOTA_HOST="localhost"
export ROBOTA_PORT="50199"

echo "-- working-dir = $ROBOTA_STATIC"
rm -rvf django_wrapper/static
mkdir -vp django_wrapper/static

# mkdir -vp ${ROBOTA_STATIC}/django_wrapper/static
cp -v django_wrapper/shared/* ${data_dir}/* django_wrapper/static

echo "-----------"
find django_wrapper/static
echo "-----------"

./manage.py runserver $ROBOTA_HOST:$ROBOTA_PORT --noreload
