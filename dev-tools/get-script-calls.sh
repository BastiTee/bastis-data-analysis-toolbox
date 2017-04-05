cd "$( dirname "$( dirname "$( readlink -f $0 )" )" )"
source "dev-tools/base.sh" > /dev/null
PY=$( get_python_com )
[ -z $PY ] && exit 1
find robota_scripts -type f -iname "*.py" -and ! -iname "__init__*" |\
while read script; do
  echo $PY -m robota_scripts.$( basename $script .py )
done
