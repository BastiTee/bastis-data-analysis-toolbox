#!/bin/bash

echo "Script might prompt for sudo-rights. Don't go away."
script_dir="$( dirname "$( readlink -f "$0" )" )"
source "$script_dir/base.sh"

sudo -H apt install -y git mongodb python3 python3-dev python3-tk

[ -z $( command -v git ) ] && {
  echo "You need to install git first."
  exit 1
}
stdoutlog "$( git --version )"

[ -z $( command -v mongo ) ] || [ -z $( command -v mongod ) ] && {
  echo "You need to install mongodb first."
  exit 1
}
stdoutlog "mongo version: $( mongod --version | head -n 1 )"

PY=$( get_python_com )
[ -z $PY ] && exit 1
stdoutlog "python version: $( $PY --version 2>&1 | cut -d" " -f2 )"

$PY -m pip -V 2> /dev/null > /dev/null
[ $? == 1 ] && {
  echo "PIP for python3 not installed."
  wget https://bootstrap.pypa.io/get-pip.py -o /dev/null -O get-pip.py
  chmod a+x get-pip.py
  $PY get-pip.py
  [ -f "get-pip.py" ] && rm get-pip.py
}
stdoutlog "pip version: $( $PY -m pip -V 2>&1 | cut -d" " -f2 )"

stdoutlog "configuring python dependencies"
run_pip=0
cat ${script_dir}/../requirements.txt | grep "#" | awk '{ print $5 }' | while read package
do
  error=$( $PY -c "import $package" 2>&1 | grep ImportError )
  [ ! -z "$error" ] && {
    echo "  + package '$package' not yet installed."
    sudo -H $PY -m pip install -r ${script_dir}/../requirements.txt
    break
  }
done

stdoutlog "configuring nltk"
[ "$1" == "-manual" ] && {
  $PY -c "import nltk; nltk.download()"
  } || {
  for module in averaged_perceptron_tagger stopwords punkt; do
    $PY -c \
    "import nltk; nltk.download('$module', download_dir='nltk-data');"
  done
}

bptbx_dir="${script_dir}/../_bptbx_install"
bptbx_linktarget="$( readlink -f ${script_dir}/../ )/bptbx"
stdoutlog "installing link to $bptbx_linktarget"
[ ! -L ${bptbx_linktarget} ] || [ ! -e ${bptbx_linktarget} ] && {
  git clone https://github.com/BastiTee/bastis-python-toolbox.git $bptbx_dir
  cd $bptbx_dir
  $PY -m pip install -r requirements.txt
  cd ..
  ln -s ${bptbx_dir}/bptbx $bptbx_linktarget
}

cd ${script_dir}/..
$PY -m robota_test.test_suite

echo
