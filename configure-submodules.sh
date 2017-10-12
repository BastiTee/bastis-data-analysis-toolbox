#!/bin/bash
cd "$( dirname "$( readlink -f "$0" )" )"
git submodule init
git submodule update --remote
