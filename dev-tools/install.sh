#!/bin/bash

cd "$( dirname "$( dirname "$( readlink -f $0 )" )" )"
source "dev-tools/base.sh"

stdoutlog "configuring python version"
PY=$( get_python_com )
[ -z $PY ] && exit 1
stdoutlog "using python version: $( $PY --version 2>&1 | cut -d" " -f2 )"

stdoutlog "configuring pip version"
$PY -m pip -V 2> /dev/null > /dev/null
[ $? == 1 ] && {
  echo "PIP for python3 not installed."
  wget https://bootstrap.pypa.io/get-pip.py -o /dev/null -O get-pip.py
  chmod a+x get-pip.py
  sudo -H $PY get-pip.py
}
stdoutlog "using pip version: $( $PY -m pip -V 2>&1 | cut -d" " -f2 )"

stdoutlog "configuring python dependencies"
run_pip=0
cat requirements.txt | grep "#" | awk '{ print $5 }' | while read package
do
  error=$( $PY -c "import $package" 2>&1 | grep ImportError )
  [ ! -z "$error" ] && {
    echo "  + package '$package' not yet installed."
    sudo -H $PY -m pip install -r requirements.txt
    break
  }
done

stdoutlog "install toolbox"

stdoutlog "configuring nltk"
[ "$1" == "-manual" ] && {
  $PY -c "import nltk; nltk.download()"
  } || {
  for module in averaged_perceptron_tagger stopwords punkt tokenize; do
    $PY -c \
    "import nltk; nltk.download('$module', download_dir='nltk-data');"
  done
}

stdoutlog "cleaning up"
[ -f "get-pip.py" ] && rm get-pip.py

global=$( yesno "Install bdatpx globally?" )
[ "$global" == "1" ] && {
  stdoutlog "Installing globally..."
  sudo -H ./setup.py install
  sudo -H rm -vrf bdatbx.egg-info build dist

  stdoutlog "Listing content in egg..."
  find $( find /usr/local/ -type d -iname "*bdatbx*" | head -n1 )
}

echo
