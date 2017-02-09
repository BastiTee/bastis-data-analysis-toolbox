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
