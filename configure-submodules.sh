#!/bin/bash
cd "$( dirname "$( readlink -f "$0" )" )"
git submodule init
# Run git submodule update --remote to upgrade to HEAD revision of sm
git submodule update
