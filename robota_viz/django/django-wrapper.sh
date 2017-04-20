#!/bin/bash

export ROBOTA_HOST="localhost"
export ROBOTA_PORT="50199"

function show_help () {
  echo $@
cat << EOF
Usage: $( basename $0) -i <INPUT_DATA> -t <TEMPLATE> [-h <HOSTNAME>] [-p <PORT>]

  -i <INPUT_DATA>       File holding the alphanumeric input data.
  -t <TEMPLATE>         D3.js visualization template
  -h <HOSTNAME>         Hostname (default: $ROBOTA_HOST)
  -p <PORT>             Port number (default: $ROBOTA_PORT)

EOF
  exit 1
}

while getopts "hi:t:h:p" opt; do
  case "$opt" in
    i) export ROBOTA_INPUT="$( readlink -f $OPTARG)";;
    t) export ROBOTA_TEMPLATE="$( readlink -f $OPTARG)";;
    h) export ROBOTA_HOST="$OPTARG";;
    p) export ROBOTA_PORT="$OPTARG";;
    h) show_help;;
    *) echo "Illegal argument."; show_help;;
  esac
done
[ -z "$ROBOTA_INPUT" ] && show_help "No input file set."
[ -z "$ROBOTA_TEMPLATE" ] && show_help "No template file set."
[ ! -f "$ROBOTA_INPUT" ] && show_help "Input file does not exist."
[ ! -f "$ROBOTA_TEMPLATE" ] && show_help "Template file does not exist."


cd $( dirname $( readlink -f $0 ))
echo "+ ROBOTA_HOST     = $ROBOTA_HOST"
echo "+ ROBOTA_PORT     = $ROBOTA_PORT"
echo "+ ROBOTA_INPUT    = $ROBOTA_INPUT"
echo "+ ROBOTA_TEMPLATE = $ROBOTA_TEMPLATE"

static_dir="django_wrapper/static"
rm -rf ${static_dir}
mkdir -p ${static_dir}
copy_com="cp django_wrapper/shared/* \
${ROBOTA_INPUT} ${ROBOTA_TEMPLATE} ${static_dir}"
eval $copy_com
echo "-----------"
echo $copy_com
echo "-----------"
find ${static_dir}
echo "-----------"

ROBOTA_INPUT=$( basename $ROBOTA_INPUT )
ROBOTA_TEMPLATE=$( basename $ROBOTA_TEMPLATE )

./manage.py runserver $ROBOTA_HOST:$ROBOTA_PORT --noreload
