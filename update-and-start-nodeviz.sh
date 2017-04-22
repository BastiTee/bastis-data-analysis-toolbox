#!/bin/bash

cd $( dirname $( readlink -f $0 ))
uptodate=$( git pull | head -n1 | grep -i "up-to-date" )
[ ! -z "$uptodate" ] && {
  echo "No changes detected."
  exit 1
}
cd robota_viz/node
npm install
[ -f pidfile ] && { pid=$( head -n1 pidfile); kill -9 $pid; }
node app.js > /dev/null &
echo $! > pidfile

