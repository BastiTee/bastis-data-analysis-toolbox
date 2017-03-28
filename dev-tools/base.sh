function stdoutlog () {
  [ -z $( command -v tput ) ] && {
    echo -e "\n--- $@\n"
    } || {
    echo -e "\n$( tput setaf 1)$@$( tput sgr0 )\n"
  }
}

function is_root () {
  if [ $( whoami ) != "root" ]
  then
    echo "Must be run as root with 'sudo -H'."
    exit 1
  fi
}

function yesno () {
  read -p "$1 (y/n)" -n 1 -r
  if [[ $REPLY =~ ^[Yy]$ ]]
  then
    echo 1
  else
    echo 0
  fi
}

function get_python_com () {
  PY="python3"
  [ -z $( command -v "$PY" ) ] && {
    [ -z $( command -v python ) ] && {
      >&2 echo "You need to install python3 first."
      echo ""
      return
    }
    py_ver=$( python --version 2>&1 | tr "." " " | cut -d" " -f2 )
    [ ! -z "$py_ver" ] && [ $py_ver == 2 ] && {
      >&2 echo "Warning: You're using python3, but script's python3-optimized."
    }
    PY="python"
  }
  echo $PY
}

[ -d "../bastis-python-toolbox" ] && {
  stdoutlog "Extending python path with a local bptbx version.."
  export PYTHONPATH=${PYTHONPATH}:../bastis-python-toolbox
}
