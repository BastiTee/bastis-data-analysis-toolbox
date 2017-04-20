#!/bin/bash

cd $( dirname $( dirname $( readlink -f $0 )))
./django-wrapper.sh \
-i ./examples/names-16-bonn.robota \
-t ./examples/names-16-bonn.html \
