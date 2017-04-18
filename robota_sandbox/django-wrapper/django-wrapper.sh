#!/bin/bash

[ -z "$1" ] && { echo "No data dir given"; exit 1; }
data_dir=$( readlink -f $1 )

cd $( dirname $( readlink -f $0 ))
export ROBOTA_HOST="localhost"
export ROBOTA_PORT="50199"
export ROBOTA_TEMPLATE="d3.html"
export ROBOTA_INPUT="input.robota"

static_dir="django_wrapper/static"
rm -rvf ${static_dir}
mkdir -vp ${static_dir}
cp -v django_wrapper/shared/* ${data_dir}/* ${static_dir}

echo "-----------"
find ${static_dir}
echo "-----------"

./manage.py runserver $ROBOTA_HOST:$ROBOTA_PORT --noreload
